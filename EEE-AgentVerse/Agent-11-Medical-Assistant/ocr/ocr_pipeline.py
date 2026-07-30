"""
ocr/ocr_pipeline.py — Orchestrator: EasyOCR → retry → Tesseract → fail gracefully.
Optimisations:
  • Engines are constructed lazily (not at __init__ time).
  • Result is cached by SHA-1 of image bytes — identical uploads skip OCR entirely.
  • Step 2 uses extract_multilang() to expand language set only when needed.
"""
from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from ocr.base_ocr import OCRResult
from ocr.image_preprocessor import deskew, preprocess_enhanced, preprocess_standard
from config import OCR_CONFIDENCE_THRESHOLD, OCR_FALLBACK_THRESHOLD
from utils.logger import get_logger

log = get_logger(__name__)

_USER_MSG_LOW_QUALITY = (
    "The image quality is too low to read the prescription accurately. "
    "Please upload a clearer, well-lit photo and try again."
)
_USER_MSG_PARTIAL = (
    "The prescription was partially read. "
    "Results may be incomplete. Please verify the details."
)

# LRU cache: up to 32 recent OCR results keyed by image SHA-1
_result_cache: dict[str, "PipelineResult"] = {}
_cache_lock   = threading.Lock()
_CACHE_MAX    = 32


@dataclass
class PipelineResult:
    ocr: OCRResult
    user_message: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.ocr.success and self.ocr.confidence >= OCR_FALLBACK_THRESHOLD


class OCRPipeline:
    """
    Full OCR pipeline with lazy engine init and result caching.
    1. Standard preprocess → EasyOCR (English only, fast)
    2. If confidence low → deskew + enhanced + EasyOCR (full languages)
    3. If still low → Tesseract fallback
    4. If all fail → user-friendly error
    """

    def __init__(self) -> None:
        self._easy = None   # lazy
        self._tess = None   # lazy

    def _get_easy(self):
        if self._easy is None:
            from ocr.easyocr_engine import EasyOCREngine
            self._easy = EasyOCREngine()
        return self._easy

    def _get_tess(self):
        if self._tess is None:
            from ocr.tesseract_engine import TesseractEngine
            self._tess = TesseractEngine()
        return self._tess

    def run(self, image_bytes: bytes) -> PipelineResult:
        # ── Cache lookup ──────────────────────────────────────────────────────
        key = hashlib.sha1(image_bytes).hexdigest()
        with _cache_lock:
            if key in _result_cache:
                log.debug("OCR cache hit for key=%s", key[:8])
                return _result_cache[key]

        log.info("OCR pipeline started (%d bytes)", len(image_bytes))
        result = self._run_pipeline(image_bytes)

        # ── Cache store ───────────────────────────────────────────────────────
        with _cache_lock:
            if len(_result_cache) >= _CACHE_MAX:
                _result_cache.pop(next(iter(_result_cache)))
            _result_cache[key] = result

        return result

    def _run_pipeline(self, image_bytes: bytes) -> PipelineResult:
        easy = self._get_easy()

        # ── Step 1: Standard preprocess + EasyOCR (English, fast) ────────────
        if easy.is_available():
            processed = preprocess_standard(image_bytes)
            result    = easy.extract(processed)
            log.info("EasyOCR step 1: conf=%.2f success=%s", result.confidence, result.success)

            if result.success and result.confidence >= OCR_CONFIDENCE_THRESHOLD:
                return PipelineResult(ocr=result)

            # ── Step 2: Deskew + enhanced + full language set ─────────────────
            enhanced = preprocess_enhanced(deskew(image_bytes))
            result2  = easy.extract_multilang(enhanced)
            log.info("EasyOCR step 2: conf=%.2f success=%s", result2.confidence, result2.success)

            if result2.success and result2.confidence >= OCR_CONFIDENCE_THRESHOLD:
                return PipelineResult(ocr=result2)

            best_easy = result2 if result2.confidence > result.confidence else result
        else:
            log.warning("EasyOCR not available; skipping to Tesseract.")
            best_easy = OCRResult(text="", confidence=0.0, engine="easyocr", success=False)
            enhanced  = preprocess_standard(image_bytes)

        # ── Step 3: Tesseract fallback ────────────────────────────────────────
        tess = self._get_tess()
        if tess.is_available():
            tess_result = tess.extract(enhanced)
            log.info("Tesseract: conf=%.2f success=%s", tess_result.confidence, tess_result.success)

            if tess_result.success and tess_result.confidence >= OCR_FALLBACK_THRESHOLD:
                return PipelineResult(ocr=tess_result)

            if tess_result.confidence >= best_easy.confidence and tess_result.success:
                return PipelineResult(ocr=tess_result, user_message=_USER_MSG_PARTIAL)

        # ── Step 4: Return best available with warning ────────────────────────
        if best_easy.success and best_easy.text.strip():
            return PipelineResult(ocr=best_easy, user_message=_USER_MSG_PARTIAL)

        # ── Step 5: Complete failure ──────────────────────────────────────────
        log.error("OCR pipeline: all engines failed.")
        return PipelineResult(
            ocr=OCRResult(text="", confidence=0.0, engine="none",
                          success=False, error="All OCR engines failed"),
            user_message=_USER_MSG_LOW_QUALITY,
        )
