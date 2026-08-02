from __future__ import annotations

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.schemas.lead import LeadCreateRequest, LeadCreateResponse, LeadRead
from app.services.lead_service import LeadService

router = APIRouter(tags=["leads"])


@router.post("/leads", response_model=LeadCreateResponse)
async def create_lead(
    payload: LeadCreateRequest, db: AsyncIOMotorDatabase = Depends(get_database)
) -> LeadCreateResponse:
    """Create a lead record with request validation and persistence."""
    service = LeadService(db)
    return await service.create(payload)


@router.get("/leads", response_model=list[LeadRead])
async def list_leads(db: AsyncIOMotorDatabase = Depends(get_database)) -> list[LeadRead]:
    """List persisted leads for testing and local verification."""
    service = LeadService(db)
    return list(await service.list())
