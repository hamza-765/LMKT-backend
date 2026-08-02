from __future__ import annotations

from fastapi import APIRouter

from app.schemas.roi import ROIRequest, ROIResponse
from app.services.roi_service import ROIService

router = APIRouter(tags=["roi"])


@router.post("/roi-calculator", response_model=ROIResponse)
def roi_calculator(payload: ROIRequest) -> ROIResponse:
    """Return a deterministic ROI estimate for the requested sector and organization size."""
    service = ROIService()
    return service.calculate(payload)
