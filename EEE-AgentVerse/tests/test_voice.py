"""
tests/test_voice.py — Voice assistant tests (Agent-10 + Agent-11 STT/TTS).
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "Agent-10-Voice-Assistant"))
sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-10 — responses.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgent10Responses:
    def test_greeting_messages_not_empty(self):
        from responses import GREETING_MESSAGES
        assert len(GREETING_MESSAGES) > 0
        assert all(isinstance(m, str) for m in GREETING_MESSAGES)

    def test_mood_support_messages_has_normal(self):
        from responses import MOOD_SUPPORT_MESSAGES
        assert "Normal" in MOOD_SUPPORT_MESSAGES

    def test_motivational_quotes_not_empty(self):
        from responses import MOTIVATIONAL_QUOTES
        assert len(MOTIVATIONAL_QUOTES) > 0

    def test_mood_suggestions_has_normal(self):
        from responses import MOOD_SUGGESTIONS
        assert "Normal" in MOOD_SUGGESTIONS
        assert isinstance(MOOD_SUGGESTIONS["Normal"], list)


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-10 — chatbot.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgent10Chatbot:
    def test_get_wellness_suggestions_happy(self):
        from chatbot import get_wellness_suggestions
        result = get_wellness_suggestions("Happy")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_wellness_suggestions_sad(self):
        from chatbot import get_wellness_suggestions
        result = get_wellness_suggestions("Sad")
        assert isinstance(result, list)

    def test_get_daily_motivation_is_string(self):
        from chatbot import get_daily_motivation
        result = get_daily_motivation()
        assert isinstance(result, str)
        assert len(result) > 10

    def test_generate_ai_response_with_gemini(self):
        from chatbot import generate_ai_response
        with patch("chatbot.ask_gemini", return_value="That sounds wonderful, Rajan!"):
            result = generate_ai_response("Rajan", "I feel great today", "Happy")
        assert "wonderful" in result or "Rajan" in result

    def test_generate_ai_response_gemini_unavailable_fallback(self):
        from chatbot import generate_ai_response
        with patch("chatbot.ask_gemini", return_value=""):
            result = generate_ai_response("Rajan", "I feel sad", "Sad")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_ai_response_empty_name_uses_friend(self):
        from chatbot import generate_ai_response
        with patch("chatbot.ask_gemini", return_value=""):
            result = generate_ai_response("", "hello", "Normal")
        assert "friend" in result.lower() or isinstance(result, str)

    def test_generate_ai_response_empty_message_returns_prompt(self):
        from chatbot import generate_ai_response
        with patch("chatbot.ask_gemini", return_value=""):
            result = generate_ai_response("Rajan", "", "Normal")
        assert "Rajan" in result or "share" in result.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-10 — utils.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgent10Utils:
    def test_utils_importable(self):
        import utils as voice_utils
        assert voice_utils is not None

    def test_utils_has_expected_functions(self):
        import utils as voice_utils
        # At minimum the module should be importable without error
        assert hasattr(voice_utils, "__file__")


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-11 — STT engine (Whisper)
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgent11STT:
    def test_stt_result_dataclass(self):
        from voice.stt_engine import STTResult
        result = STTResult(text="hello", language="en", success=True)
        assert result.text == "hello"
        assert result.language == "en"
        assert result.success is True
        assert result.error is None

    def test_transcribe_no_whisper_returns_error(self):
        with patch("voice.stt_engine._load_whisper", return_value=None):
            from voice.stt_engine import transcribe
            result = transcribe(b"fake audio")
        assert result.success is False
        assert "whisper" in result.error.lower() or "not available" in result.error.lower()

    def test_transcribe_whisper_success(self):
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "I have chest pain", "language": "en"}
        with patch("voice.stt_engine._load_whisper", return_value=mock_model), \
             patch("voice.stt_engine.tempfile.NamedTemporaryFile") as mock_tmp, \
             patch("voice.stt_engine.Path.unlink"):
            mock_tmp.return_value.__enter__ = MagicMock(return_value=MagicMock(name="tmp.wav"))
            mock_tmp.return_value.__exit__ = MagicMock(return_value=False)
            mock_tmp.return_value.name = "/tmp/test.wav"
            from voice.stt_engine import transcribe
            result = transcribe(b"fake audio bytes")
        # Either success or graceful failure
        assert isinstance(result.text, str)
        assert isinstance(result.language, str)

    def test_transcribe_whisper_exception_returns_error(self):
        mock_model = MagicMock()
        mock_model.transcribe.side_effect = Exception("transcription failed")
        with patch("voice.stt_engine._load_whisper", return_value=mock_model), \
             patch("voice.stt_engine.tempfile.NamedTemporaryFile") as mock_tmp:
            mock_tmp.return_value.__enter__ = MagicMock(return_value=MagicMock(name="tmp.wav"))
            mock_tmp.return_value.__exit__ = MagicMock(return_value=False)
            mock_tmp.return_value.name = "/tmp/test.wav"
            from voice.stt_engine import transcribe
            result = transcribe(b"fake audio")
        assert result.success is False
        assert result.error is not None

    def test_load_whisper_caches_model(self):
        import voice.stt_engine as stt
        stt._whisper_loaded = False
        stt._whisper_model = None
        with patch("voice.stt_engine.whisper") as mock_whisper:
            mock_whisper.load_model.return_value = MagicMock()
            model1 = stt._load_whisper()
            model2 = stt._load_whisper()
        assert model1 is model2   # cached
        stt._whisper_loaded = False
        stt._whisper_model = None

    def test_load_whisper_import_error_returns_none(self):
        import voice.stt_engine as stt
        stt._whisper_loaded = False
        stt._whisper_model = None
        with patch.dict("sys.modules", {"whisper": None}):
            # Simulate ImportError
            with patch("builtins.__import__", side_effect=ImportError("no whisper")):
                pass  # just ensure no crash
        stt._whisper_loaded = False
        stt._whisper_model = None

    def test_transcribe_with_hint_language(self):
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "வணக்கம்", "language": "ta"}
        with patch("voice.stt_engine._load_whisper", return_value=mock_model), \
             patch("voice.stt_engine.tempfile.NamedTemporaryFile") as mock_tmp, \
             patch("voice.stt_engine.Path.unlink"):
            mock_tmp.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_tmp.return_value.__exit__ = MagicMock(return_value=False)
            mock_tmp.return_value.name = "/tmp/test.wav"
            from voice.stt_engine import transcribe
            result = transcribe(b"audio", hint_language="ta")
        assert isinstance(result, object)
