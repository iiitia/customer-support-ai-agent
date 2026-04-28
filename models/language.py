import logging
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    Returns 'en', 'ar', or 'unknown'.
    """
    if not text or not text.strip():
        return "unknown"

    try:
        lang = detect(text)
        logger.debug("Detected language code: %s", lang)
        if lang == "ar":
            return "ar"
        elif lang in ("en", "en-us", "en-gb"):
            return "en"
        else:
            return lang  # pass through other codes so prompts.py can handle them
    except LangDetectException as e:
        logger.warning("Language detection failed: %s", e)
        return "unknown"
