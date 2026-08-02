from __future__ import annotations

import logging
from typing import Sequence

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.lead import Lead
from app.schemas.lead import LeadCreateRequest, LeadCreateResponse, LeadRead
from app.utils.validators import validate_email, validate_required_fields

logger = logging.getLogger("lmkt.backend")

COLLECTION_NAME = "leads"


class LeadService:
    """Persistence logic for landing page lead submissions."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection = db[COLLECTION_NAME]

    async def create(self, payload: LeadCreateRequest) -> LeadCreateResponse:
        """Persist a new lead document and return the created ID."""
        required_fields = ["name", "email", "phone", "company", "sector", "message"]
        validate_required_fields(payload.model_dump(), required_fields)
        email = validate_email(payload.email)

        try:
            lead = Lead(
                name=payload.name.strip(),
                email=email,
                phone=payload.phone.strip(),
                company=payload.company.strip(),
                sector=payload.sector.strip(),
                message=payload.message.strip(),
            )
            document = lead.model_dump(by_alias=True, exclude={"id"})
            result = await self.collection.insert_one(document)
            return LeadCreateResponse(success=True, lead_id=str(result.inserted_id))
        except Exception:
            logger.exception("Failed to save lead")
            raise HTTPException(status_code=500, detail="Unable to save lead")

    async def list(self) -> Sequence[LeadRead]:
        """Return stored leads for testing and inspection."""
        cursor = self.collection.find().sort("_id", -1)
        leads = await cursor.to_list(length=None)
        return [
            LeadRead(
                id=str(document["_id"]),
                name=document["name"],
                email=document["email"],
                phone=document["phone"],
                company=document["company"],
                sector=document["sector"],
                message=document["message"],
                created_at=document["created_at"],
            )
            for document in leads
        ]
