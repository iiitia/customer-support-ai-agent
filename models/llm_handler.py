import logging
from groq import Groq
from app.config import get_settings

logger = logging.getLogger(__name__)


def get_client():
    """Lazy-init Groq client so import doesn't fail without API key."""
    settings = get_settings()
    return Groq(api_key=settings.GROQ_API_KEY)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    settings = get_settings()
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},  # enforce JSON at API level
        )
        content = response.choices[0].message.content
        logger.info("LLM call succeeded. Tokens used: %s", response.usage.total_tokens)
        return content
    except Exception as e:
        logger.error("LLM call failed: %s", e)
        raise RuntimeError(f"LLM call failed: {e}")
