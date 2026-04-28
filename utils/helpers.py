import json
from schemas.response_schema import SupportResponse


def response_to_dict(response: SupportResponse) -> dict:
    """Convert a SupportResponse to a plain dict for display or serialization."""
    return {
        "intent": response.intent,
        "urgency": response.urgency,
        "confidence": response.confidence,
        "reasoning": response.reasoning,
        "suggested_reply_en": response.suggested_reply_en,
        "suggested_reply_ar": response.suggested_reply_ar,
        "needs_human": response.needs_human,
    }


def format_confidence_label(confidence: float) -> str:
    """Return a human-readable confidence label."""
    if confidence >= 0.8:
        return "High"
    elif confidence >= 0.5:
        return "Medium"
    else:
        return "Low (flagged for human review)"


def urgency_color(urgency: str) -> str:
    """Return a hex color for urgency level (useful for UI styling)."""
    return {"high": "#e53e3e", "medium": "#dd6b20", "low": "#38a169"}.get(urgency, "#718096")


def pretty_print_response(response: SupportResponse) -> str:
    """Return a pretty-printed JSON string of the response."""
    return json.dumps(response_to_dict(response), ensure_ascii=False, indent=2)
