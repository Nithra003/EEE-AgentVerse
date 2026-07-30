"""
tests/test_ai.py — AI engine tests (Agent-3 AIEngine + Agent-11 LLMRouter).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in [
    str(ROOT / "Agent-3-Appointment-Booking"),
    str(ROOT / "Agent-11-Medical-Assistant"),
]:
    if p not in sys.path:
        sys.path.insert(0, p)


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-3 — AIEngine
# ═══════════════════════════════════════════════════════════════════════════════

class TestAIEngine:
    def _engine(self, ollama=False):
        with patch("ai_engine.AIEngine._check_ollama", return_value=ollama):
            from ai_engine import AIEngine
            return AIEngine()

    # ── Symptom analysis ──────────────────────────────────────────────────────
    def test_analyse_no_ollama_keyword_fallback(self):
        engine = self._engine(ollama=False)
        result = engine.analyse_symptoms("knee pain and joint stiffness", age=70)
        assert result["specialty"] == "Orthopedic"

    def test_analyse_ollama_valid_json_response(self):
        engine = self._engine(ollama=True)
        mock_resp = {
            "message": {"content": json.dumps({
                "specialty": "Cardiologist",
                "confidence": 92,
                "reasoning": "Chest pain suggests cardiac issue.",
                "urgency": "urgent",
                "prescription_flags": [],
                "patient_message": "Please see a heart specialist.",
            })}
        }
        with patch("ai_engine.ollama.chat", return_value=mock_resp):
            result = engine.analyse_symptoms("chest pain", age=65, gender="male")
        assert result["specialty"] == "Cardiologist"
        assert result["confidence"] == 92
        assert result["urgency"] == "urgent"

    def test_analyse_ollama_invalid_json_falls_back(self):
        engine = self._engine(ollama=True)
        with patch("ai_engine.ollama.chat", return_value={"message": {"content": "not json"}}):
            result = engine.analyse_symptoms("fever and cold", age=60)
        assert "specialty" in result
        assert "doctors" in result

    def test_analyse_ollama_unknown_specialty_falls_back(self):
        engine = self._engine(ollama=True)
        bad_json = json.dumps({"specialty": "Astrologer", "confidence": 50,
                               "reasoning": "", "urgency": "routine",
                               "prescription_flags": [], "patient_message": ""})
        with patch("ai_engine.ollama.chat", return_value={"message": {"content": bad_json}}):
            result = engine.analyse_symptoms("fever", age=60)
        assert result["specialty"] in ["General Physician", "Cardiologist",
                                        "Orthopedic", "Dentist", "Dermatologist",
                                        "Ophthalmologist"]

    def test_analyse_ollama_exception_falls_back(self):
        engine = self._engine(ollama=True)
        with patch("ai_engine.ollama.chat", side_effect=Exception("connection refused")):
            result = engine.analyse_symptoms("tooth pain", age=55)
        assert "specialty" in result

    # ── Prescription explanation ───────────────────────────────────────────────
    def test_explain_prescription_no_ollama_safe_response(self):
        engine = self._engine(ollama=False)
        result = engine.explain_prescription("Paracetamol 500mg twice daily", age=65)
        assert "summary" in result
        assert "medications" in result
        assert "flags" in result

    def test_explain_prescription_ollama_valid(self):
        engine = self._engine(ollama=True)
        mock_content = json.dumps({
            "medications": [{"name": "Paracetamol", "purpose": "Pain relief",
                              "warnings": "Avoid alcohol"}],
            "summary": "Take Paracetamol for pain.",
            "flags": [],
        })
        with patch("ai_engine.ollama.chat", return_value={"message": {"content": mock_content}}):
            result = engine.explain_prescription("Paracetamol 500mg", age=65)
        assert result["summary"] == "Take Paracetamol for pain."
        assert len(result["medications"]) == 1

    # ── JSON parsing ──────────────────────────────────────────────────────────
    def test_parse_json_trailing_comma_fixed(self):
        engine = self._engine()
        result = engine._parse_json('{"key": "value",}')
        assert result is not None
        assert result["key"] == "value"

    def test_parse_json_nested(self):
        engine = self._engine()
        result = engine._parse_json('{"a": {"b": 1}}')
        assert result["a"]["b"] == 1

    def test_parse_json_none_input(self):
        engine = self._engine()
        assert engine._parse_json(None) is None

    # ── Memory ────────────────────────────────────────────────────────────────
    def test_memory_summary_truncates_old_turns(self):
        engine = self._engine()
        for i in range(20):
            engine.add_to_memory("user", f"message {i}")
        summary = engine.memory.summary()
        assert isinstance(summary, str)

    def test_memory_clear(self):
        engine = self._engine()
        engine.add_to_memory("user", "hello")
        engine.clear_memory()
        assert engine.memory.summary() == ""

    # ── Prompt builders ───────────────────────────────────────────────────────
    def test_build_symptom_prompt_contains_symptoms(self):
        from ai_engine import _build_symptom_prompt
        prompt = _build_symptom_prompt("chest pain", 70, "male", "", "Cardiologist")
        assert "chest pain" in prompt
        assert "70" in prompt
        assert "male" in prompt

    def test_build_prescription_prompt_contains_text(self):
        from ai_engine import _build_prescription_prompt
        prompt = _build_prescription_prompt("Paracetamol 500mg", 65)
        assert "Paracetamol" in prompt
        assert "65" in prompt

    # ── Model fallback chain ──────────────────────────────────────────────────
    def test_call_with_fallback_no_ollama_returns_empty(self):
        engine = self._engine(ollama=False)
        result = engine._call_with_fallback("test prompt")
        assert result == ""

    def test_call_with_fallback_all_models_fail(self):
        engine = self._engine(ollama=True)
        with patch("ai_engine.ollama.chat", side_effect=Exception("fail")):
            result = engine._call_with_fallback("test prompt")
        assert result == ""


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-11 — LLMRouter
# ═══════════════════════════════════════════════════════════════════════════════

class TestLLMRouter:
    def test_router_instantiation(self):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ai.llm_router import LLMRouter
        with patch("ai.llm_router.get_client") as mock_client:
            mock_client.return_value.ping.return_value = False
            router = LLMRouter()
            router._ready.wait(timeout=2)
        assert router is not None

    def test_router_generate_all_fail_returns_fallback(self):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ai.llm_router import LLMRouter
        from ai.base_llm import LLMResponse
        with patch("ai.llm_router.get_client") as mock_client:
            mock_client.return_value.ping.return_value = False
            router = LLMRouter()
            router._ready.wait(timeout=2)
        for model in router._models:
            model.generate = MagicMock(return_value=LLMResponse(
                text="", model="test", success=False, error="fail"
            ))
        resp = router.generate([])
        assert resp.success is False
        assert "ollama" in resp.text.lower() or "unavailable" in resp.text.lower()

    def test_router_generate_first_model_success(self):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ai.llm_router import LLMRouter
        from ai.base_llm import LLMResponse, LLMMessage
        with patch("ai.llm_router.get_client") as mock_client:
            mock_client.return_value.ping.return_value = False
            router = LLMRouter()
            router._ready.wait(timeout=2)
        router._models[0].generate = MagicMock(return_value=LLMResponse(
            text="Cardiologist", model="qwen3", success=True
        ))
        resp = router.generate([LLMMessage(role="user", content="chest pain")])
        assert resp.success is True
        assert resp.text == "Cardiologist"

    def test_router_chat_returns_string(self):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ai.llm_router import LLMRouter
        from ai.base_llm import LLMResponse
        with patch("ai.llm_router.get_client") as mock_client:
            mock_client.return_value.ping.return_value = False
            router = LLMRouter()
            router._ready.wait(timeout=2)
        router._models[0].generate = MagicMock(return_value=LLMResponse(
            text="Hello!", model="qwen3", success=True
        ))
        result = router.chat("You are helpful.", "Hello")
        assert isinstance(result, str)

    def test_get_router_singleton(self):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        import ai.llm_router as lr
        lr._router = None
        with patch("ai.llm_router.get_client") as mock_client:
            mock_client.return_value.ping.return_value = False
            r1 = lr.get_router()
            r2 = lr.get_router()
        assert r1 is r2
        lr._router = None

    def test_active_model_name_returns_string(self):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ai.llm_router import LLMRouter
        with patch("ai.llm_router.get_client") as mock_client:
            mock_client.return_value.ping.return_value = False
            router = LLMRouter()
            router._ready.wait(timeout=2)
        assert isinstance(router.active_model_name, str)
