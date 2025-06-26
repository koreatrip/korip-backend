SUPPORTED_LANGUAGES = {
    'ko': '한국어',
    'en': 'English',
    'jp': '日本語',
    'cn': '中文'
}

def validate_language(lang_code):
    if lang_code and lang_code in SUPPORTED_LANGUAGES:
        return lang_code
    return 'ko'

def get_supported_languages():
    return SUPPORTED_LANGUAGES

def get_language_name(lang_code):
    return SUPPORTED_LANGUAGES.get(lang_code, '한국어')