from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import SettingsDep
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])
logger = logging.getLogger("lmkt.backend")


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, settings: SettingsDep) -> ChatResponse:
    """Handle LMKT domain-restricted chat requests."""
    try:
        service = ChatService()
        result = service.answer(payload.message)
        return ChatResponse(**result)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected chatbot error")
        raise HTTPException(status_code=500, detail="Internal server error")
