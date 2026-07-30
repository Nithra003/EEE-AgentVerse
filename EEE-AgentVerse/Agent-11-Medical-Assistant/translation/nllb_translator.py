"""
translation/nllb_translator.py — NLLB-200 local translation engine.
Falls back to LLM-based translation if the model is not downloaded,
and to returning the original text if both fail.
"""
from __future__ import annotations

from typing import Optional

import threading

from translation.language_registry import get_nllb_code
from translation.translation_cache import get_cache
from utils.logger import get_logger

log = get_logger(__name__)

_pipeline = None   # lazy-loaded transformers pipeline
_pipeline_loaded = False
_pipeline_lock   = threading.Lock()


def _load_pipeline():
    global _pipeline, _pipeline_loaded
    if _pipeline_loaded:
        return _pipeline
    with _pipeline_lock:
        if _pipeline_loaded:
            return _pipeline
        try:
            from transformers import pipeline as hf_pipeline
            from config import NLLB_MODEL_NAME
            log.info("Loading NLLB-200 model: %s (first run may be slow)", NLLB_MODEL_NAME)
            _pipeline = hf_pipeline(
                "translation",
                model=NLLB_MODEL_NAME,
                device=-1,   # CPU
            )
            log.info("NLLB-200 model loaded.")
        except Exception as exc:
            log.warning("Could not load NLLB-200: %s — LLM fallback will be used.", exc)
            _pipeline = None
        _pipeline_loaded = True
    return _pipeline


def translate(text: str, target_lang: str, source_lang: str = "en") -> str:
    """
    Translate `text` from `source_lang` to `target_lang`.
    Returns original text if translation is not possible.
    """
    if not text.strip():
        return text
    if target_lang == source_lang or target_lang == "en" and source_lang == "en":
        return text

    cache = get_cache()
    cached = cache.get(text, target_lang)
    if cached:
        return cached

    # ── Try NLLB-200 ─────────────────────────────────────────────────────────
    pipe = _load_pipeline()
    if pipe is not None:
        try:
            src_code = get_nllb_code(source_lang)
            tgt_code = get_nllb_code(target_lang)
            result = pipe(
                text,
                src_lang=src_code,
                tgt_lang=tgt_code,
                max_length=512,
            )
            translated = result[0]["translation_text"]
            cache.set(text, target_lang, translated)
            return translated
        except Exception as exc:
            log.warning("NLLB translation failed: %s — trying LLM fallback", exc)

    # ── LLM fallback ─────────────────────────────────────────────────────────
    try:
        from ai.llm_router import get_router
        from ai.prompt_templates import TRANSLATE_TEXT
        from translation.language_registry import get_display_name

        router = get_router()
        target_name = get_display_name(target_lang)
        prompt = TRANSLATE_TEXT.render_user(target_language=target_name, text=text)
        translated = router.chat(TRANSLATE_TEXT.system, prompt)
        if translated.strip():
            cache.set(text, target_lang, translated)
            return translated
    except Exception as exc:
        log.warning("LLM translation fallback failed: %s", exc)

    # ── Return original ───────────────────────────────────────────────────────
    log.error("All translation methods failed for lang=%s", target_lang)
    return text
