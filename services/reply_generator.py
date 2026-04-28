from schemas.response_schema import SupportResponse


def extract_replies(response: SupportResponse) -> dict:
    """
    Extract suggested replies from a validated SupportResponse.
    Use this when you only need the reply part, not the classification.
    """
    return {
        "suggested_reply_en": response.suggested_reply_en,
        "suggested_reply_ar": response.suggested_reply_ar,
    }
