"""
gemini_helper.py - Shared Gemini AI helper for all ElderCare AI agents
"""

import os
from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(_env_path)

_api_key = os.getenv("GEMINI_API_KEY")
_client  = None
_model   = None

if _api_key:
    try:
        from google import genai
        _client = genai.Client(api_key=_api_key)
        _model  = "gemini-2.0-flash"
    except Exception:
        try:
            import google.generativeai as genai_old
            genai_old.configure(api_key=_api_key)
            _model = genai_old.GenerativeModel("gemini-1.5-flash")
            _client = "legacy"
        except Exception:
            pass


def ask_gemini(prompt: str, fallback: str = "Unable to generate AI response.") -> str:
    """Send a prompt to Gemini and return the response text."""
    if not _api_key:
        return fallback
    try:
        if _client and _client != "legacy":
            from google import genai
            response = _client.models.generate_content(model=_model, contents=prompt)
            return response.text.strip()
        elif _client == "legacy":
            response = _model.generate_content(prompt)
            return response.text.strip()
    except Exception:
        pass
    return fallback
