from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request payload for the LMKT chatbot."""

    message: str = Field(..., min_length=1, max_length=500, description="User question about LMKT")


class ChatResponse(BaseModel):
    """Chatbot response payload."""

    reply: str
    success: bool = True
    timestamp: str
