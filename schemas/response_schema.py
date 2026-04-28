from pydantic import BaseModel, Field, field_validator
from typing import Literal


class SupportResponse(BaseModel):
    intent: Literal["refund", "exchange", "complaint", "inquiry"]
    urgency: Literal["high", "medium", "low"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    suggested_reply_en: str
    suggested_reply_ar: str
    needs_human: bool

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, v: str) -> str:
        allowed = {"refund", "exchange", "complaint", "inquiry"}
        if v not in allowed:
            raise ValueError(f"Invalid intent '{v}'. Must be one of: {allowed}")
        return v

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, v: str) -> str:
        allowed = {"low", "medium", "high"}
        if v not in allowed:
            raise ValueError(f"Invalid urgency '{v}'. Must be one of: {allowed}")
        return v

    @field_validator("reasoning")
    @classmethod
    def validate_reasoning_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("reasoning must not be empty")
        return v.strip()

    @field_validator("suggested_reply_en", "suggested_reply_ar")
    @classmethod
    def validate_reply_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Reply fields must not be empty")
        return v.strip()
