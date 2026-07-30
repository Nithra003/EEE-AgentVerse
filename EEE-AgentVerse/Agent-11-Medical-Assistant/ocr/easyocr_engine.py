"""
ocr/easyocr_engine.py — EasyOCR implementation of BaseOCR.
Optimisations:
  • Loads only English by default; expands to full language list on first
    non-English detection (avoids loading 6 models at startup).
  • Reuses the reader instance across calls (lazy singleton per language set).
  • Converts PIL → numpy once per extract() call.
"""
from __future__ import annotations

import io
import threading
from typing import List, Optional

from ocr.base_ocr import BaseOCR, OCRResult
from config import OCR_LANGUAGES
from utils.logger import get_logger

log = get_logger(__name__)

# Languages to load on first use (English only for fast startup)
_FAST_LANGS: List[str] = ["en"]
_FULL_LANGS: List[str] = [l for l in OCR_LANGUAGES if l in ("en", "ta", "hi", "te", "ml", "kn")]


class EasyOCREngine(BaseOCR):
    engine_name = "easyocr"

    def __init__(self) -> None:
        self._reader = None
        self._reader_langs: Optional[List[str]] = None
        self._lock = threading.Lock()

    def is_available(self) -> bool:
        try:
            import easyocr  # noqa: F401
            return True
        except ImportError:
            return False

    def _get_reader(self, langs: Optional[List[str]] = None):
        target = langs or _FAST_LANGS
        with self._lock:
            if self._reader is None or self._reader_langs != target:
                import easyocr
                self._reader = easyocr.Reader(target, gpu=False, verbose=False)
                self._reader_langs = target
                log.info("EasyOCR reader initialised with languages: %s", target)
        return self._reader

    def extract(self, image_bytes: bytes, use_full_langs: bool = False) -> OCRResult:
        try:
            import numpy as np
            from PIL import Image

            langs  = _FULL_LANGS if use_full_langs else _FAST_LANGS
            reader = self._get_reader(langs)

            img     = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            arr     = np.asarray(img)           # single decode, no copy
            results = reader.readtext(arr, detail=1, paragraph=False)

            if not results:
                return OCRResult(
                    text="", confidence=0.0, engine=self.engine_name,
                    success=False, error="No text detected",
                )

            texts  = [t for (_, t, _) in results]
            confs  = [float(c) for (_, _, c) in results]
            avg_c  = sum(confs) / len(confs)
            full   = " ".join(texts)

            log.debug("EasyOCR: %d regions, avg_conf=%.2f, chars=%d", len(results), avg_c, len(full))
            return OCRResult(text=full, confidence=avg_c, engine=self.engine_name, success=True)

        except Exception as exc:
            log.error("EasyOCR extraction failed: %s", exc)
            return OCRResult(
                text="", confidence=0.0, engine=self.engine_name,
                success=False, error=str(exc),
            )

    def extract_multilang(self, image_bytes: bytes) -> OCRResult:
        """Re-run with the full language set (called by pipeline on low confidence)."""
        return self.extract(image_bytes, use_full_langs=True)
