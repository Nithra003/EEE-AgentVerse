"""
voice/tts_engine.py — Coqui TTS text-to-speech engine.
Returns WAV bytes that can be played in the browser via Streamlit components.
Falls back to browser SpeechSynthesis JS if Coqui is unavailable.
"""
from __future__ import annotations

import io
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from config import TTS_MODEL
from utils.logger import get_logger

log = get_logger(__name__)

_tts_model = None
_tts_loaded = False


def _load_tts():
    global _tts_model, _tts_loaded
    if _tts_loaded:
        return _tts_model
    try:
        from TTS.api import TTS
        log.info("Loading Coqui TTS model: %s", TTS_MODEL)
        _tts_model = TTS(model_name=TTS_MODEL, progress_bar=False, gpu=False)
        log.info("Coqui TTS model loaded.")
    except Exception as exc:
        log.warning("Could not load Coqui TTS: %s", exc)
        _tts_model = None
    _tts_loaded = True
    return _tts_model


@dataclass
class TTSResult:
    audio_bytes: Optional[bytes]
    success: bool
    fallback_js: Optional[str] = None   # JS snippet for browser TTS fallback
    error: Optional[str] = None


def synthesize(text: str, language: str = "en") -> TTSResult:
    """
    Convert text to speech.
    Returns WAV bytes on success, or a JS fallback snippet.
    """
    if not text.strip():
        return TTSResult(audio_bytes=None, success=False, error="Empty text")

    tts = _load_tts()
    if tts is not None:
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            tts.tts_to_file(text=text, file_path=tmp_path)
            audio_bytes = Path(tmp_path).read_bytes()
            Path(tmp_path).unlink(missing_ok=True)
            log.debug("TTS synthesised %d bytes for %d chars", len(audio_bytes), len(text))
            return TTSResult(audio_bytes=audio_bytes, success=True)
        except Exception as exc:
            log.warning("Coqui TTS synthesis failed: %s — using browser fallback", exc)

    # ── Browser SpeechSynthesis fallback ─────────────────────────────────────
    safe_text = text.replace("'", " ").replace('"', " ").replace("\n", " ")
    safe_text = safe_text.encode("ascii", "ignore").decode("ascii")
    js = (
        f"<script>"
        f"window.speechSynthesis.cancel();"
        f"var u=new SpeechSynthesisUtterance('{safe_text}');"
        f"u.rate=0.85; u.pitch=1.0; u.volume=1.0;"
        f"u.lang='{language}';"
        f"window.speechSynthesis.speak(u);"
        f"</script>"
    )
    return TTSResult(audio_bytes=None, success=False, fallback_js=js, error="Coqui unavailable")
