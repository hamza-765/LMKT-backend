from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LeadCreateRequest(BaseModel):
    """Lead submission payload."""

    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=40)
    company: str = Field(..., min_length=1, max_length=160)
    sector: str = Field(..., min_length=1, max_length=80)
    message: str = Field(..., min_length=1, max_length=1500)


class LeadCreateResponse(BaseModel):
    """Lead creation response."""

    success: bool = True
    lead_id: str


class LeadRead(BaseModel):
    """Lead retrieval model for testing."""

    id: str
    name: str
    email: str
    phone: str
    company: str
    sector: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
