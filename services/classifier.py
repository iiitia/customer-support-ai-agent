from schemas.response_schema import SupportResponse


def extract_classification(response: SupportResponse) -> dict:
    """
    Extract classification fields from a validated SupportResponse.
    Use this when you only need the classification part, not the reply.
    """
    return {
        "intent": response.intent,
        "urgency": response.urgency,
        "confidence": response.confidence,
        "needs_human": response.needs_human,
        "reasoning": response.reasoning,
    }
