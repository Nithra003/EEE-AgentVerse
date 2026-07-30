"""
ocr/base_ocr.py — Abstract OCR interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class OCRResult:
    text: str
    confidence: float          # 0.0 – 1.0
    engine: str                # "easyocr" | "tesseract"
    success: bool
    error: Optional[str] = None

    @property
    def is_reliable(self) -> bool:
        return self.success and self.confidence >= 0.65


class BaseOCR(ABC):
    """Abstract base for OCR engines."""

    engine_name: str = ""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the engine dependencies are installed."""

    @abstractmethod
    def extract(self, image_bytes: bytes) -> OCRResult:
        """Extract text from raw image bytes."""
