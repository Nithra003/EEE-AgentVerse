"""
ocr/tesseract_engine.py — Tesseract OCR fallback implementation.
Uses pytesseract with LSTM engine and block-level PSM.
"""
from __future__ import annotations

import io
import re

from ocr.base_ocr import BaseOCR, OCRResult
from config import TESSERACT_CMD
from utils.logger import get_logger

log = get_logger(__name__)


class TesseractEngine(BaseOCR):
    engine_name = "tesseract"

    def is_available(self) -> bool:
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def extract(self, image_bytes: bytes) -> OCRResult:
        try:
            import pytesseract
            from PIL import Image

            pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

            img = Image.open(io.BytesIO(image_bytes)).convert("L")

            # PSM 6 = assume uniform block of text; OEM 3 = LSTM + legacy
            config = "--oem 3 --psm 6"
            data = pytesseract.image_to_data(
                img, config=config, output_type=pytesseract.Output.DICT
            )

            words = []
            confs = []
            for word, conf in zip(data["text"], data["conf"]):
                word = word.strip()
                if word and conf != -1:
                    words.append(word)
                    confs.append(int(conf))

            if not words:
                return OCRResult(
                    text="", confidence=0.0, engine=self.engine_name,
                    success=False, error="No text detected"
                )

            full_text = " ".join(words)
            avg_conf  = (sum(confs) / len(confs)) / 100.0   # normalise to 0-1

            log.debug(
                "Tesseract: %d words, avg_conf=%.2f", len(words), avg_conf
            )
            return OCRResult(
                text=full_text,
                confidence=avg_conf,
                engine=self.engine_name,
                success=True,
            )
        except Exception as exc:
            log.error("Tesseract extraction failed: %s", exc)
            return OCRResult(
                text="", confidence=0.0, engine=self.engine_name,
                success=False, error=str(exc)
            )
