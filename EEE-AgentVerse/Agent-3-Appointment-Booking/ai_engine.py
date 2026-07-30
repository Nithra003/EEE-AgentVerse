# ai_engine.py - Multi-Model AI Engine
# Primary: Qwen3 → Fallback: DeepSeek → Second Fallback: Llama
# Features: automatic switching, structured JSON, medical reasoning,
#            prescription understanding, conversation memory, prompt optimization.
# Guarantee: never crashes, never exposes model errors to users.

import json
import re
import logging
from typing import Optional
from doctors import DOCTORS, SPECIALTY_INFO, SYMPTOM_MAP, get_all_specialties
from tools import find_specialist

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model registry — ordered by preference
# ---------------------------------------------------------------------------
MODELS = [
    {"name": "qwen3",    "label": "Qwen3"},
    {"name": "deepseek-r1:7b", "label": "DeepSeek"},
    {"name": "llama3.2", "label": "Llama"},
]

MAX_MEMORY = 10   # conversation turns kept in context


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

def _build_symptom_prompt(symptoms: str, age: int, gender: str,
                           history_summary: str, specialties: str) -> str:
    context = f"\nPatient history context: {history_summary}" if history_summary else ""
    return f"""You are a senior medical triage AI for an ElderCare system.
Patient: {age}-year-old {gender}.
Reported symptoms: "{symptoms}".{context}
Available specialties: {specialties}.

Respond ONLY with valid JSON (no markdown, no explanation outside JSON):
{{
  "specialty": "<exact specialty from list>",
  "confidence": <integer 0-100>,
  "reasoning": "<1-2 sentence medical reasoning>",
  "urgency": "<routine|soon|urgent>",
  "prescription_flags": ["<any concerning medication interactions or flags if mentioned>"],
  "patient_message": "<friendly 1-sentence explanation for the elderly patient>"
}}"""


def _build_prescription_prompt(prescription_text: str, age: int) -> str:
    return f"""You are a medical AI helping an elderly patient ({age} years old) understand their prescription.
Prescription text: "{prescription_text}"

Respond ONLY with valid JSON:
{{
  "medications": [{{"name": "<drug>", "purpose": "<plain English purpose>", "warnings": "<key warnings>"}}],
  "summary": "<overall plain English summary for elderly patient>",
  "flags": ["<any serious interactions or concerns>"]
}}"""


# ---------------------------------------------------------------------------
# Memory manager
# ---------------------------------------------------------------------------

class ConversationMemory:
    def __init__(self):
        self._turns: list[dict] = []

    def add(self, role: str, content: str):
        self._turns.append({"role": role, "content": content})
        if len(self._turns) > MAX_MEMORY * 2:
            self._turns = self._turns[-(MAX_MEMORY * 2):]

    def summary(self) -> str:
        """Return a compact summary of recent turns for prompt injection."""
        if not self._turns:
            return ""
        parts = []
        for t in self._turns[-6:]:
            prefix = "Patient" if t["role"] == "user" else "Agent"
            parts.append(f"{prefix}: {t['content'][:120]}")
        return " | ".join(parts)

    def clear(self):
        self._turns.clear()


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class AIEngine:
    """
    Multi-model AI engine with automatic fallback.
    Primary: Qwen3 | Fallback: DeepSeek | Second Fallback: Llama
    All errors are caught internally; users always get a clean response.
    """

    def __init__(self):
        self.memory = ConversationMemory()
        self._active_model: Optional[str] = None
        self._ollama_available = self._check_ollama()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyse_symptoms(self, symptoms: str, age: int = 60,
                         gender: str = "unknown") -> dict:
        """
        Analyse symptoms and return structured specialist recommendation.
        Always returns a valid dict — never raises.
        """
        self.memory.add("user", f"Symptoms: {symptoms}")
        specialties = ", ".join(get_all_specialties())
        prompt = _build_symptom_prompt(
            symptoms, age, gender, self.memory.summary(), specialties
        )
        raw = self._call_with_fallback(prompt)
        result = self._parse_json(raw)

        if result and self._valid_specialty(result.get("specialty", "")):
            specialty = result["specialty"]
            doctors   = DOCTORS.get(specialty, DOCTORS["General Physician"])
            info      = SPECIALTY_INFO.get(specialty, {"icon": "🏥", "desc": ""})
            output = {
                "specialty":      specialty,
                "confidence":     result.get("confidence", 85),
                "icon":           info["icon"],
                "description":    result.get("patient_message") or info["desc"],
                "reasoning":      result.get("reasoning", ""),
                "urgency":        result.get("urgency", "routine"),
                "prescription_flags": result.get("prescription_flags", []),
                "doctors":        [d["name"] for d in doctors],
                "doctor_details": doctors,
            }
            self.memory.add("agent", f"Recommended: {specialty}")
            return output

        # Graceful degradation — keyword tool
        return self._keyword_fallback(symptoms)

    def explain_prescription(self, prescription_text: str, age: int = 60) -> dict:
        """
        Explain a prescription in plain English for elderly patients.
        Always returns a valid dict — never raises.
        """
        prompt = _build_prescription_prompt(prescription_text, age)
        raw    = self._call_with_fallback(prompt)
        result = self._parse_json(raw)
        if result and "summary" in result:
            return result
        return {
            "medications": [],
            "summary": "Please ask your doctor or pharmacist to explain this prescription.",
            "flags": [],
        }

    def add_to_memory(self, role: str, content: str):
        self.memory.add(role, content)

    def clear_memory(self):
        self.memory.clear()

    @property
    def active_model(self) -> str:
        return self._active_model or "keyword-fallback"

    # ------------------------------------------------------------------
    # Model calling with automatic fallback chain
    # ------------------------------------------------------------------

    def _check_ollama(self) -> bool:
        try:
            import ollama
            ollama.list()
            return True
        except Exception:
            return False

    def _call_with_fallback(self, prompt: str) -> str:
        if not self._ollama_available:
            return ""

        for model_cfg in MODELS:
            model_name = model_cfg["name"]
            try:
                import ollama
                response = ollama.chat(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.1, "num_predict": 512},
                )
                text = response["message"]["content"].strip()
                if text:
                    self._active_model = model_cfg["label"]
                    logger.info("AIEngine: used %s", model_cfg["label"])
                    return text
            except Exception as e:
                logger.warning("AIEngine: %s failed — %s", model_cfg["label"], type(e).__name__)
                continue

        return ""

    # ------------------------------------------------------------------
    # JSON parsing — robust, never crashes
    # ------------------------------------------------------------------

    def _parse_json(self, text: str) -> Optional[dict]:
        if not text:
            return None
        # Strip markdown fences if present
        cleaned = re.sub(r"```(?:json)?|```", "", text).strip()
        # Extract first {...} block
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            # Attempt lenient fix: replace single quotes, trailing commas
            try:
                fixed = re.sub(r",\s*([}\]])", r"\1", match.group())
                return json.loads(fixed)
            except Exception:
                return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _valid_specialty(self, specialty: str) -> bool:
        return specialty in get_all_specialties()

    def _keyword_fallback(self, symptoms: str) -> dict:
        self._active_model = "keyword-fallback"
        return find_specialist(symptoms)
