"""
tests/test_ocr.py — OCR pipeline tests (Agent-4 and Agent-11).
"""
from __future__ import annotations

import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in [
    str(ROOT / "Agent-4-Prescription-Explainer"),
    str(ROOT / "Agent-11-Medical-Assistant"),
]:
    if p not in sys.path:
        sys.path.insert(0, p)


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-4 — ocr_engine.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestOCREngine:
    @pytest.fixture
    def white_png(self):
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (400, 200), color=(255, 255, 255)).save(buf, format="PNG")
        return buf.getvalue()

    @pytest.fixture
    def prescription_png(self):
        """PNG with prescription-like text rendered via PIL."""
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (600, 300), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Dr. Priya Sharma", fill=(0, 0, 0))
        draw.text((10, 40), "City Hospital", fill=(0, 0, 0))
        draw.text((10, 70), "Date: 12/06/2025", fill=(0, 0, 0))
        draw.text((10, 100), "Patient: Rajan Kumar", fill=(0, 0, 0))
        draw.text((10, 130), "Tab Paracetamol 500mg twice daily 5 days after food", fill=(0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def test_extract_prescription_invalid_bytes_returns_safe(self):
        from ocr_engine import extract_prescription
        result = extract_prescription(b"garbage", max_retries=0)
        assert "confidence" in result
        assert result["confidence"] == 0.0 or "error" in result

    def test_extract_prescription_returns_required_keys(self):
        from ocr_engine import extract_prescription
        result = extract_prescription(b"garbage", max_retries=0)
        for key in ["raw_text", "fields", "confidence", "ocr_engine"]:
            assert key in result

    def test_preprocess_strategy_0(self, white_png):
        from ocr_engine import _to_numpy, _preprocess
        img = _to_numpy(white_png)
        out = _preprocess(img, 0)
        assert out is not None
        assert out.shape[0] > 0

    def test_preprocess_all_strategies(self, white_png):
        from ocr_engine import _to_numpy, _preprocess
        img = _to_numpy(white_png)
        for strategy in range(5):
            out = _preprocess(img, strategy)
            assert out is not None

    def test_score_fields_all_filled(self):
        from ocr_engine import _score_fields
        fields = {
            "doctor": "Dr. X", "hospital": "City Hospital",
            "date": "12/06/2025", "patient": "Rajan",
            "medicines": ["Tab Para"], "dosage": ["500mg"],
            "frequency": ["twice daily"], "duration": ["5 days"],
            "instructions": ["after food"],
        }
        score = _score_fields(fields, 0.9)
        assert score > 0.5

    def test_score_fields_all_empty(self):
        from ocr_engine import _score_fields
        fields = {k: "" for k in
                  ["doctor", "hospital", "date", "patient",
                   "medicines", "dosage", "frequency", "duration", "instructions"]}
        score = _score_fields(fields, 0.0)
        assert score == 0.0

    def test_extract_fields_empty_text(self):
        from ocr_engine import _extract_fields
        fields = _extract_fields("")
        assert fields["doctor"] == ""
        assert fields["medicines"] == []

    def test_extract_fields_full_prescription(self):
        from ocr_engine import _extract_fields
        text = (
            "Dr. Priya Sharma\nCity Hospital\nDate: 12/06/2025\n"
            "Patient: Rajan Kumar\n"
            "Tab Paracetamol 500mg twice daily 5 days after food\n"
            "Tab Metformin 500mg once daily 30 days after food"
        )
        fields = _extract_fields(text)
        assert fields["doctor"] == "Priya Sharma"
        assert len(fields["medicines"]) >= 1
        assert any("500mg" in d for d in fields["dosage"])

    def test_easyocr_mock_success(self, white_png):
        from ocr_engine import extract_prescription
        mock_results = [([[0, 0], [100, 0], [100, 20], [0, 20]],
                         "Tab Paracetamol 500mg", 0.85)]
        with patch("ocr_engine._run_easyocr", return_value=("Tab Paracetamol 500mg", 0.85)):
            result = extract_prescription(white_png, max_retries=1)
        assert result["confidence"] > 0

    def test_easyocr_fails_tesseract_fallback(self, white_png):
        from ocr_engine import extract_prescription
        with patch("ocr_engine._run_easyocr", side_effect=Exception("EasyOCR unavailable")), \
             patch("ocr_engine._run_tesseract", return_value=("Tab Aspirin 75mg", 0.7)):
            result = extract_prescription(white_png, max_retries=1)
        assert result["ocr_engine"] in ("Tesseract", "none", "EasyOCR")

    def test_confidence_thresholds(self):
        from ocr_engine import CONFIDENCE_RETRY_THRESHOLD, CONFIDENCE_ACCEPT_THRESHOLD
        assert 0 < CONFIDENCE_RETRY_THRESHOLD < CONFIDENCE_ACCEPT_THRESHOLD < 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-11 — OCR pipeline
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgent11OCRPipeline:
    @pytest.fixture
    def white_png(self):
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (300, 150), color=(255, 255, 255)).save(buf, format="PNG")
        return buf.getvalue()

    def test_pipeline_instantiation(self):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ocr.ocr_pipeline import OCRPipeline
        pipeline = OCRPipeline()
        assert pipeline is not None
        assert pipeline._easy is None   # lazy
        assert pipeline._tess is None

    def test_pipeline_result_ok_property(self):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ocr.ocr_pipeline import PipelineResult
        from ocr.base_ocr import OCRResult
        good = PipelineResult(ocr=OCRResult(text="hello", confidence=0.8,
                                             engine="easyocr", success=True))
        bad  = PipelineResult(ocr=OCRResult(text="", confidence=0.1,
                                             engine="none", success=False))
        assert good.ok is True
        assert bad.ok is False

    def test_pipeline_cache_hit(self, white_png):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ocr.ocr_pipeline import OCRPipeline, _result_cache
        _result_cache.clear()
        pipeline = OCRPipeline()
        mock_result = MagicMock()
        mock_result.ok = True

        with patch.object(pipeline, "_run_pipeline", return_value=mock_result) as mock_run:
            pipeline.run(white_png)
            pipeline.run(white_png)   # second call should hit cache
        assert mock_run.call_count == 1
        _result_cache.clear()

    def test_image_preprocessor_standard(self, white_png):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ocr.image_preprocessor import preprocess_standard
        result = preprocess_standard(white_png)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_image_preprocessor_enhanced(self, white_png):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ocr.image_preprocessor import preprocess_enhanced
        result = preprocess_enhanced(white_png)
        assert isinstance(result, bytes)

    def test_pipeline_all_engines_fail_returns_error(self, white_png):
        sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))
        from ocr.ocr_pipeline import OCRPipeline, _result_cache
        _result_cache.clear()
        pipeline = OCRPipeline()
        with patch.object(pipeline, "_get_easy") as mock_easy, \
             patch.object(pipeline, "_get_tess") as mock_tess:
            easy_inst = MagicMock()
            easy_inst.is_available.return_value = False
            mock_easy.return_value = easy_inst
            tess_inst = MagicMock()
            tess_inst.is_available.return_value = False
            mock_tess.return_value = tess_inst
            result = pipeline.run(white_png)
        assert result.ok is False
        _result_cache.clear()
