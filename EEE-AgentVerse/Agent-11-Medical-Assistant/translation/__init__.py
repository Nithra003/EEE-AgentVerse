# translation/__init__.py
from translation.language_detector import detect_language, DetectionResult
from translation.nllb_translator import translate
from translation.language_registry import (
    all_language_options, get_display_name, get_nllb_code, LANGUAGE_REGISTRY,
)

__all__ = [
    "detect_language", "DetectionResult",
    "translate",
    "all_language_options", "get_display_name", "get_nllb_code", "LANGUAGE_REGISTRY",
]
