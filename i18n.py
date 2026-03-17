import json
import os
from functools import lru_cache

SUPPORTED_LOCALES = ("en", "ar")
DEFAULT_LOCALE = "en"
MESSAGES_DIR = os.path.join(os.path.dirname(__file__), "messages")


@lru_cache(maxsize=None)
def _load_messages(locale: str) -> dict:
    path = os.path.join(MESSAGES_DIR, f"{locale}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_translation_func(locale: str):
    """Return a t() function bound to the given locale.

    Supports dot-notation keys like ``t('nav.dashboard')``.
    Falls back to the default locale, then to the key itself.
    """
    if locale not in SUPPORTED_LOCALES:
        locale = DEFAULT_LOCALE

    messages = _load_messages(locale)
    fallback = _load_messages(DEFAULT_LOCALE) if locale != DEFAULT_LOCALE else {}

    def t(key: str) -> str:
        parts = key.split(".")
        val = messages
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                val = None
                break
        if val is not None and isinstance(val, str):
            return val

        val = fallback
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                val = None
                break
        if val is not None and isinstance(val, str):
            return val

        return key

    return t


def get_locale_dir(locale: str) -> str:
    return "rtl" if locale == "ar" else "ltr"
