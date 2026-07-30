"""
agents/prescription_agent.py — Orchestrates: image → OCR → AI extract → DB save → reminders.
"""
from __future__ import annotations

import json
import re
from datetime import date
from typing import Any, Dict, List, Optional

from agents.base_agent import AgentResponse, BaseAgent
from ai.llm_router import get_router
from ai.prompt_templates import MEDICINE_EXPLAIN, PRESCRIPTION_EXTRACT
from database.engine import get_session
from database import repository as repo
from ocr.ocr_pipeline import OCRPipeline
from reminder.reminder_service import create_reminder_for_medicine
from utils.date_utils import parse_date
from utils.error_handler import safe_execute
from utils.logger import get_logger

log = get_logger(__name__)
_ocr_pipeline = OCRPipeline()


class PrescriptionAgent(BaseAgent):
    """
    Processes a prescription image end-to-end:
    1. OCR extraction
    2. AI-powered structured parsing
    3. Persist to database
    4. Auto-create medicine reminders
    """

    def process(self, user_input: str) -> AgentResponse:
        # This agent is driven by image bytes, not text input
        return AgentResponse(
            message="Please upload a prescription image.",
            success=False,
        )

    def process_image(self, image_bytes: bytes) -> AgentResponse:
        """Main entry point for prescription image processing."""
        # ── Step 1: OCR ───────────────────────────────────────────────────────
        pipeline_result = _ocr_pipeline.run(image_bytes)

        if not pipeline_result.ok:
            return AgentResponse(
                message=pipeline_result.user_message or "Could not read the prescription.",
                success=False,
                error="OCR failed",
            )

        ocr_text = pipeline_result.ocr.text
        ocr_conf = pipeline_result.ocr.confidence
        ocr_eng  = pipeline_result.ocr.engine

        log.info("OCR complete: engine=%s conf=%.2f chars=%d", ocr_eng, ocr_conf, len(ocr_text))

        # ── Step 2: AI extraction ─────────────────────────────────────────────
        extracted = self._extract_with_ai(ocr_text)
        if not extracted:
            return AgentResponse(
                message="Could not extract prescription details. Please try a clearer image.",
                success=False,
                error="AI extraction failed",
            )

        # ── Step 3: Persist ───────────────────────────────────────────────────
        rx_id = self._save_prescription(extracted, ocr_text, ocr_conf, ocr_eng)

        # ── Step 4: Auto-create reminders ─────────────────────────────────────
        reminder_count = 0
        if rx_id and self.user_id:
            reminder_count = self._create_reminders(rx_id)

        medicines = extracted.get("medicines", [])
        msg = (
            f"✅ Prescription read successfully!\n\n"
            f"Found **{len(medicines)} medicine(s)**. "
            f"Created **{reminder_count} reminder(s)** automatically."
        )
        if pipeline_result.user_message:
            msg += f"\n\n⚠️ {pipeline_result.user_message}"

        return AgentResponse(
            message=msg,
            success=True,
            data={
                "prescription_id": rx_id,
                "extracted":       extracted,
                "ocr_confidence":  round(ocr_conf, 2),
                "ocr_engine":      ocr_eng,
                "reminder_count":  reminder_count,
            },
        )

    def explain_medicine(
        self,
        medicine_name: str,
        strength: str = "",
        dosage: str = "",
        frequency: str = "",
        food_instruction: str = "",
        duration: str = "",
        diagnosis: str = "",
        patient_name: str = "the patient",
        age: int = 60,
    ) -> str:
        """Generate an elderly-friendly explanation for a single medicine."""
        router = get_router()
        prompt = MEDICINE_EXPLAIN.render_user(
            patient_name=patient_name,
            age=age,
            language=self.language,
            medicine_name=medicine_name,
            strength=strength,
            dosage=dosage,
            frequency=frequency,
            food_instruction=food_instruction,
            duration=duration,
            diagnosis=diagnosis,
        )
        result = router.chat(MEDICINE_EXPLAIN.system, prompt)
        return result or "Explanation unavailable. Please consult your doctor."

    # ── Private helpers ───────────────────────────────────────────────────────
    @safe_execute(fallback=None, user_message="AI extraction failed.")
    def _extract_with_ai(self, ocr_text: str) -> Optional[Dict]:
        router = get_router()
        prompt = PRESCRIPTION_EXTRACT.render_user(ocr_text=ocr_text)
        raw    = router.chat(PRESCRIPTION_EXTRACT.system, prompt)

        # Strip markdown fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()

        data = json.loads(raw)
        log.info("AI extracted %d medicines", len(data.get("medicines", [])))
        return data

    def _save_prescription(
        self,
        data: Dict,
        ocr_text: str,
        ocr_conf: float,
        ocr_eng: str,
    ) -> Optional[int]:
        if not self.user_id:
            return None
        try:
            rx_date = parse_date(data.get("date") or "")
            with get_session() as session:
                rx = repo.create_prescription(
                    session,
                    user_id=self.user_id,
                    raw_ocr_text=ocr_text,
                    ocr_engine=ocr_eng,
                    ocr_confidence=ocr_conf,
                    doctor_name=data.get("doctor_name"),
                    hospital_name=data.get("hospital_name"),
                    rx_date=rx_date,
                    patient_name=data.get("patient_name"),
                    patient_age=data.get("patient_age"),
                    patient_gender=data.get("patient_gender"),
                    diagnosis=data.get("diagnosis"),
                    special_notes=data.get("special_notes"),
                    ai_model_used=get_router().active_model_name,
                )
                rx_id = rx.id

                for med_data in data.get("medicines", []):
                    repo.create_medicine(
                        session,
                        user_id=self.user_id,
                        prescription_id=rx_id,
                        name=med_data.get("name", "Unknown"),
                        strength=med_data.get("strength"),
                        dosage=med_data.get("dosage"),
                        frequency=med_data.get("frequency"),
                        morning=bool(med_data.get("morning", False)),
                        afternoon=bool(med_data.get("afternoon", False)),
                        night=bool(med_data.get("night", False)),
                        before_food=bool(med_data.get("before_food", False)),
                        after_food=bool(med_data.get("after_food", False)),
                        duration_days=med_data.get("duration_days"),
                        special_instr=med_data.get("special_instr"),
                        confidence=med_data.get("confidence"),
                        start_date=date.today(),
                    )
            return rx_id
        except Exception as exc:
            log.error("_save_prescription failed: %s", exc)
            return None

    def _create_reminders(self, rx_id: int) -> int:
        count = 0
        try:
            with get_session() as session:
                rx = repo.get_prescription(session, rx_id)
                if not rx:
                    return 0
                for med in rx.medicines:
                    ids = create_reminder_for_medicine(self.user_id, med)
                    count += len(ids)
        except Exception as exc:
            log.error("_create_reminders failed: %s", exc)
        return count
