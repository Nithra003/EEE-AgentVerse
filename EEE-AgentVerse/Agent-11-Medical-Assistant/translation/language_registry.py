"""
translation/language_registry.py — All supported language codes and display names.
Maps ISO 639-1 codes to NLLB-200 flores codes and display names.
"""
from __future__ import annotations

from typing import Dict, NamedTuple, Optional


class LangInfo(NamedTuple):
    display_name: str
    nllb_code: str       # flores-200 code for NLLB-200
    native_name: str


# Subset of the most relevant languages; extend as needed
LANGUAGE_REGISTRY: Dict[str, LangInfo] = {
    "en":    LangInfo("English",    "eng_Latn", "English"),
    "ta":    LangInfo("Tamil",      "tam_Taml", "தமிழ்"),
    "hi":    LangInfo("Hindi",      "hin_Deva", "हिन्दी"),
    "te":    LangInfo("Telugu",     "tel_Telu", "తెలుగు"),
    "ml":    LangInfo("Malayalam",  "mal_Mlym", "മലയാളം"),
    "kn":    LangInfo("Kannada",    "kan_Knda", "ಕನ್ನಡ"),
    "mr":    LangInfo("Marathi",    "mar_Deva", "मराठी"),
    "bn":    LangInfo("Bengali",    "ben_Beng", "বাংলা"),
    "gu":    LangInfo("Gujarati",   "guj_Gujr", "ગુજરાતી"),
    "pa":    LangInfo("Punjabi",    "pan_Guru", "ਪੰਜਾਬੀ"),
    "ur":    LangInfo("Urdu",       "urd_Arab", "اردو"),
    "fr":    LangInfo("French",     "fra_Latn", "Français"),
    "de":    LangInfo("German",     "deu_Latn", "Deutsch"),
    "es":    LangInfo("Spanish",    "spa_Latn", "Español"),
    "ar":    LangInfo("Arabic",     "arb_Arab", "العربية"),
    "zh":    LangInfo("Chinese",    "zho_Hans", "中文"),
    "ja":    LangInfo("Japanese",   "jpn_Jpan", "日本語"),
    "ko":    LangInfo("Korean",     "kor_Hang", "한국어"),
    "pt":    LangInfo("Portuguese", "por_Latn", "Português"),
    "ru":    LangInfo("Russian",    "rus_Cyrl", "Русский"),
}


def get_lang_info(code: str) -> Optional[LangInfo]:
    return LANGUAGE_REGISTRY.get(code)


def get_nllb_code(lang_code: str) -> str:
    info = LANGUAGE_REGISTRY.get(lang_code)
    return info.nllb_code if info else "eng_Latn"


def get_display_name(lang_code: str) -> str:
    info = LANGUAGE_REGISTRY.get(lang_code)
    return info.display_name if info else lang_code.upper()


def all_language_options() -> Dict[str, str]:
    """Return {display_name: code} for UI dropdowns."""
    return {f"{v.display_name} ({v.native_name})": k for k, v in LANGUAGE_REGISTRY.items()}
