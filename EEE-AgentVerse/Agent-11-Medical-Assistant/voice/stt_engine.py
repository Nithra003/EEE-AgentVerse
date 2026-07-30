"""
voice/stt_engine.py — Whisper-based Speech-to-Text engine.
Returns transcribed text + detected language.
"""
from __future__ import annotations

import io
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from config import WHISPER_MODEL
from utils.logger import get_logger

log = get_logger(__name__)

_whisper_model = None
_whisper_loaded = False


def _load_whisper():
    global _whisper_model, _whisper_loaded
    if _whisper_loaded:
        return _whisper_model
    try:
        import whisper
        log.info("Loading Whisper model: %s", WHISPER_MODEL)
        _whisper_model = whisper.load_model(WHISPER_MODEL)
        log.info("Whisper model loaded.")
    except Exception as exc:
        log.warning("Could not load Whisper: %s", exc)
        _whisper_model = None
    _whisper_loaded = True
    return _whisper_model


@dataclass
class STTResult:
    text: str
    language: str
    success: bool
    error: Optional[str] = None


def transcribe(audio_bytes: bytes, hint_language: Optional[str] = None) -> STTResult:
    """
    Transcribe audio bytes (WAV/MP3/OGG) to text using Whisper.
    Returns STTResult with detected language code.
    """
    model = _load_whisper()
    if model is None:
        return STTResult(
            text="", language="en", success=False,
            error="Whisper model not available. Install openai-whisper."
        )

    try:
        # Write to temp file — Whisper requires a file path
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        options = {}
        if hint_language:
            options["language"] = hint_language

        result = model.transcribe(tmp_path, **options)
        Path(tmp_path).unlink(missing_ok=True)

        text = result.get("text", "").strip()
        lang = result.get("language", "en")
        log.debug("Whisper transcribed %d chars, lang=%s", len(text), lang)

        return STTResult(text=text, language=lang, success=bool(text))
    except Exception as exc:
        log.error("Whisper transcription failed: %s", exc)
        return STTResult(text="", language="en", success=False, error=str(exc))
