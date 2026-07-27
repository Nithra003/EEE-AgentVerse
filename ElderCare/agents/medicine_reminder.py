"""Medicine reminder agent for an eldercare multi-agent hackathon demo."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency during import
    def load_dotenv(*_args: Any, **_kwargs: Any) -> bool:
        return False

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover - optional dependency during import
    Anthropic = None  # type: ignore[assignment]

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class MedicineReminderAgent:
    """Generate patient-friendly medicine reminder responses."""

    ALLOWED_STATUSES = {"reminded", "confirmed", "missed"}

    def __init__(self, model: str = "claude-3-5-sonnet-latest") -> None:
        self.model = model
        self.client: Any | None = None
        self.api_key: str | None = None
        self._load_environment()

    def _load_environment(self) -> None:
        """Load the Anthropic API key from a .env file if present."""
        env_file = PROJECT_ROOT / ".env"
        load_dotenv(env_file)
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if Anthropic is not None and self.api_key:
            self.client = Anthropic(api_key=self.api_key)

    def generate_response(
        self,
        patient_name: str,
        medicine_name: str,
        dosage: str,
        scheduled_time: str,
        patient_response: str | None = None,
    ) -> dict[str, str]:
        """Create a warm reminder response in the required JSON format."""
        if not patient_name or not medicine_name or not dosage or not scheduled_time:
            raise ValueError(
                "patient_name, medicine_name, dosage, and scheduled_time are required"
            )

        prompt = self._build_prompt(
            patient_name=patient_name,
            medicine_name=medicine_name,
            dosage=dosage,
            scheduled_time=scheduled_time,
            patient_response=patient_response,
        )

        try:
            if self.client is not None and self.api_key:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=200,
                    temperature=0,
                    system=(
                        "You are a warm assistant for eldercare reminders. "
                        "Return valid JSON only with message_to_patient and status."
                    ),
                    messages=[{"role": "user", "content": prompt}],
                )
                raw_content = response.content[0].text if response.content else ""
                parsed = self._parse_model_json(raw_content)
                if parsed is not None:
                    return self._validate_payload(parsed)
        except Exception as exc:  # pragma: no cover - depends on external API
            print(f"Falling back to local response due to Anthropic error: {exc}")

        return self._build_fallback_response(
            patient_name=patient_name,
            medicine_name=medicine_name,
            patient_response=patient_response,
        )

    def _build_prompt(
        self,
        patient_name: str,
        medicine_name: str,
        dosage: str,
        scheduled_time: str,
        patient_response: str | None,
    ) -> str:
        """Create the prompt sent to the Anthropic model."""
        response_text = patient_response or ""
        return (
            f"You are helping with an eldercare reminder for {patient_name}. "
            f"The patient needs {medicine_name} with dosage {dosage} at {scheduled_time}. "
            f"The patient response was: {response_text}. "
            "Return ONLY valid JSON in this exact shape: "
            '{"message_to_patient": "...", "status": "reminded" | "confirmed" | "missed"}. '
            "If there is no patient response, use status reminded. "
            "If the patient confirms taking the medicine, use status confirmed. "
            "If the patient says they forgot, skipped, or will take it later, use status missed. "
            "Keep the response warm, respectful, and under two short sentences. "
            "Do not provide medical advice."
        )

    def _parse_model_json(self, raw_content: str) -> dict[str, Any] | None:
        """Parse JSON from the model output and tolerate code fences."""
        if not raw_content:
            return None

        text = raw_content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.MULTILINE).strip()

        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not match:
                return None
            try:
                payload = json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

        if isinstance(payload, dict):
            return payload
        return None

    def _validate_payload(self, payload: dict[str, Any]) -> dict[str, str]:
        """Ensure the model output matches the required contract."""
        status = str(payload.get("status", "")).strip().lower()
        message = str(payload.get("message_to_patient", "")).strip()
        if status not in self.ALLOWED_STATUSES or not message:
            raise ValueError("The model returned an invalid response payload")
        return {"message_to_patient": message, "status": status}

    def _build_fallback_response(
        self,
        patient_name: str,
        medicine_name: str,
        patient_response: str | None,
    ) -> dict[str, str]:
        """Create a deterministic response when the API is unavailable."""
        status = self._infer_status(patient_response)
        if status == "confirmed":
            message = (
                f"Thank you for letting me know, {patient_name}. "
                f"I’m glad you took your {medicine_name}."
            )
        elif status == "missed":
            message = (
                f"I’m sorry to hear that, {patient_name}. "
                "I’ll keep this note for you."
            )
        else:
            message = (
                f"Hello {patient_name}, this is a gentle reminder about your {medicine_name}."
            )
        return {"message_to_patient": message, "status": status}

    def _infer_status(self, patient_response: str | None) -> str:
        """Infer the reminder status from the patient response."""
        if not patient_response or not str(patient_response).strip():
            return "reminded"

        text = str(patient_response).strip().lower()
        if any(word in text for word in ("confirm", "confirmed", "yes", "took", "taken", "done")):
            return "confirmed"
        if any(
            word in text
            for word in ("forgot", "forgotten", "skip", "skipped", "later", "miss", "missed", "postpone")
        ):
            return "missed"
        return "reminded"

    def run_demo_tests(self) -> list[dict[str, str]]:
        """Run three example scenarios and print each result as formatted JSON."""
        scenarios = [
            {
                "patient_name": "Evelyn",
                "medicine_name": "Vitamin D",
                "dosage": "1 tablet",
                "scheduled_time": "8:00 AM",
                "patient_response": None,
            },
            {
                "patient_name": "Evelyn",
                "medicine_name": "Vitamin D",
                "dosage": "1 tablet",
                "scheduled_time": "8:00 AM",
                "patient_response": "Yes, I took it.",
            },
            {
                "patient_name": "Evelyn",
                "medicine_name": "Vitamin D",
                "dosage": "1 tablet",
                "scheduled_time": "8:00 AM",
                "patient_response": "I forgot and will take it later.",
            },
        ]

        results: list[dict[str, str]] = []
        for scenario in scenarios:
            result = self.generate_response(
                patient_name=scenario["patient_name"],
                medicine_name=scenario["medicine_name"],
                dosage=scenario["dosage"],
                scheduled_time=scenario["scheduled_time"],
                patient_response=scenario["patient_response"],
            )
            results.append(result)
            print(json.dumps(result, indent=2))
            print()
        return results


if __name__ == "__main__":
    MedicineReminderAgent().run_demo_tests()
