import logging
from django.conf import settings

logger = logging.getLogger(__name__)
SUPPORTED_LANGS = {code for code, _ in settings.LANGUAGES}

def normalize_lang(raw: str | None) -> str:
    """
    lang 값이 대문자면 소문자로 변환하고,
    지원하지 않는 값이면 DEFAULT_LANG으로 폴백
    """
    if not raw:
        return settings.DEFAULT_LANG

    lang = raw.lower()
    if lang in SUPPORTED_LANGS:
        return lang

    logger.warning(f"Unsupported lang '{raw}', fallback to {settings.DEFAULT_LANG}")
    return settings.DEFAULT_LANG