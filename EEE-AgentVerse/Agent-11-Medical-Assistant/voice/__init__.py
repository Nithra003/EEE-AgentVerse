# voice/__init__.py
from voice.stt_engine import transcribe, STTResult
from voice.tts_engine import synthesize, TTSResult

__all__ = ["transcribe", "STTResult", "synthesize", "TTSResult"]
