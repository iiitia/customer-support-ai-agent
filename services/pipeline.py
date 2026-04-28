import json
import logging

from models.llm_handler import call_llm
from models.prompts import SYSTEM_PROMPT, build_user_prompt
from models.language import detect_language
from schemas.response_schema import SupportResponse
from app.config import get_settings

logger = logging.getLogger(__name__)


def extract_json(text: str) -> dict:
    """
    Parse JSON from LLM output. With response_format=json_object this should
    rarely be needed, but kept as a safety net.
    """
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: find the outermost {...} block
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in LLM response")

    json_text = text[start:end]
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse extracted JSON: {e}\nRaw text: {json_text[:300]}")


def process_email(email: str) -> SupportResponse:
    settings = get_settings()

    # Detect language and pass as hint to prompt builder
    language = detect_language(email)
    logger.info("Detected language: %s", language)

    user_prompt = build_user_prompt(email, language=language)

    last_error = None
    for attempt in range(1, 3):  # up to 2 attempts
        logger.info("Pipeline attempt %d/2", attempt)
        try:
            raw_output = call_llm(SYSTEM_PROMPT, user_prompt)
            logger.debug("Raw LLM output: %s", raw_output[:500])

            parsed = extract_json(raw_output)
            validated = SupportResponse(**parsed)

            # Override needs_human based on confidence threshold
            if validated.confidence < settings.CONFIDENCE_THRESHOLD:
                logger.info(
                    "Confidence %.2f below threshold %.2f — flagging for human review",
                    validated.confidence,
                    settings.CONFIDENCE_THRESHOLD,
                )
                validated.needs_human = True

            logger.info(
                "Email processed: intent=%s urgency=%s confidence=%.2f needs_human=%s",
                validated.intent,
                validated.urgency,
                validated.confidence,
                validated.needs_human,
            )
            return validated

        except Exception as e:
            last_error = e
            logger.warning("Attempt %d failed: %s", attempt, e)

    raise ValueError(f"Failed to get a valid response after 2 attempts. Last error: {last_error}")
