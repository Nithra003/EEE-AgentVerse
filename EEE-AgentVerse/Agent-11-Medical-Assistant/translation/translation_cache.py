"""
translation/translation_cache.py — Thread-safe LRU cache for translations.
Avoids re-running the model for identical (text, target_lang) pairs.
"""
from __future__ import annotations

import hashlib
import threading
from collections import OrderedDict
from typing import Optional

from config import TRANSLATION_CACHE_SIZE
from utils.logger import get_logger

log = get_logger(__name__)


class TranslationCache:
    """Thread-safe LRU cache keyed by (text_hash, target_lang)."""

    def __init__(self, maxsize: int = TRANSLATION_CACHE_SIZE) -> None:
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._maxsize = maxsize
        self._lock = threading.Lock()

    def _key(self, text: str, target_lang: str) -> str:
        digest = hashlib.md5(text.encode("utf-8")).hexdigest()
        return f"{digest}:{target_lang}"

    def get(self, text: str, target_lang: str) -> Optional[str]:
        key = self._key(text, target_lang)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
        return None

    def set(self, text: str, target_lang: str, translation: str) -> None:
        key = self._key(text, target_lang)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self._maxsize:
                    evicted = self._cache.popitem(last=False)
                    log.debug("Cache evicted key: %s", evicted[0])
            self._cache[key] = translation

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)


# Module-level singleton
_cache = TranslationCache()


def get_cache() -> TranslationCache:
    return _cache
