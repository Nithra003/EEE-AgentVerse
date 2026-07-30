"""
gemini_helper.py — Shared Gemini AI helper for all ElderCare AI agents.
Fixed: lazy initialization, removed string sentinel, proper error handling.
"""

import os
from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(_env_path)

_api_key = os.getenv("GEMINI_API_KEY", "").strip()

# Lazy-initialized client state
_initialized = False
_use_new_sdk = False
_client = None
_model = None


def _init():
    global _initialized, _use_new_sdk, _client, _model
    if _initialized:
        return
    _initialized = True
    if not _api_key or _api_key == "your_gemini_api_key_here":
        return
    try:
        from google import genai
        _client = genai.Client(api_key=_api_key)
        _model = "gemini-2.0-flash"
        _use_new_sdk = True
    except Exception:
        try:
            import google.generativeai as genai_old
            genai_old.configure(api_key=_api_key)
            _model = genai_old.GenerativeModel("gemini-2.0-flash")
            _use_new_sdk = False
        except Exception:
            pass


def ask_gemini(
    prompt: str,
    fallback: str = "AI response unavailable. Please try again in a moment.",
) -> str:
    """Send a prompt to Gemini and return the response text."""
    _init()
    if not _api_key or _api_key == "your_gemini_api_key_here":
        return "AI key not configured. Please add GEMINI_API_KEY to .env file."
    if _model is None:
        return fallback
    try:
        if _use_new_sdk and _client is not None:
            from google import genai
            response = _client.models.generate_content(model=_model, contents=prompt)
            return response.text.strip()
        elif not _use_new_sdk and _model is not None:
            response = _model.generate_content(prompt)
            return response.text.strip()
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower():
            return (
                "Gemini API quota exceeded. "
                "Please wait a minute and try again, or add a new API key to the .env file."
            )
    return fallback
