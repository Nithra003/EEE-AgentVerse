"""
tests/conftest.py — Shared fixtures for all ElderCare AI test suites.
"""
from __future__ import annotations

import io
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
AGENT3 = ROOT / "Agent-3-Appointment-Booking"
AGENT1 = ROOT / "Agent-1-Medicine-Reminder"
AGENT4 = ROOT / "Agent-4-Prescription-Explainer"
AGENT10 = ROOT / "Agent-10-Voice-Assistant"
AGENT11 = ROOT / "Agent-11-Medical-Assistant"

for p in [str(AGENT3), str(AGENT1), str(AGENT4), str(AGENT10), str(AGENT11)]:
    if p not in sys.path:
        sys.path.insert(0, p)


# ── Minimal white PNG (1×1 pixel) ─────────────────────────────────────────────
@pytest.fixture
def white_png_bytes() -> bytes:
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (200, 100), color=(255, 255, 255)).save(buf, format="PNG")
    return buf.getvalue()


# ── Sample prescription text ──────────────────────────────────────────────────
@pytest.fixture
def sample_prescription_text() -> str:
    return (
        "Dr. Priya Sharma\nCity Hospital\nDate: 12/06/2025\n"
        "Patient: Rajan Kumar\nTab Paracetamol 500mg twice daily 5 days after food\n"
        "Tab Metformin 500mg once daily 30 days after food"
    )


# ── Minimal patient dict ──────────────────────────────────────────────────────
@pytest.fixture
def sample_patient() -> dict:
    return {
        "name": "Rajan Kumar",
        "age": 68,
        "gender": "Male",
        "phone": "9876543210",
        "symptoms": "chest pain and shortness of breath",
    }


# ── Mock Gemini model ─────────────────────────────────────────────────────────
@pytest.fixture
def mock_gemini():
    with patch("google.generativeai.GenerativeModel") as m:
        instance = MagicMock()
        instance.generate_content.return_value.text = (
            "Cardiologist\nYour symptoms suggest a heart-related issue."
        )
        m.return_value = instance
        yield m
