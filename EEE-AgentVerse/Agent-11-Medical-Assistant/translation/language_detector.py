"""
translation/language_detector.py — Language detection using langdetect.
Returns ISO 639-1 code with confidence; falls back to "en" on failure.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class DetectionResult:
    language: str       # ISO 639-1 code
    confidence: float   # 0.0 – 1.0
    reliable: bool      # True if confidence >= 0.80


def detect_language(text: str) -> DetectionResult:
    """
    Detect the language of `text`.
    Returns DetectionResult with language="en" on any failure.
    """
    if not text or len(text.strip()) < 10:
        return DetectionResult(language="en", confidence=0.0, reliable=False)

    try:
        from langdetect import detect_langs
        results = detect_langs(text)
        if results:
            top = results[0]
            lang = top.lang
            conf = float(top.prob)
            log.debug("Detected language: %s (%.2f)", lang, conf)
            return DetectionResult(language=lang, confidence=conf, reliable=conf >= 0.80)
    except Exception as exc:
        log.warning("Language detection failed: %s", exc)

    return DetectionResult(language="en", confidence=0.0, reliable=False)
