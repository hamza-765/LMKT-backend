from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ROIRequest(BaseModel):
    """Request payload for the ROI calculator.

    The API keeps the original field names for compatibility while also
    accepting the camelCase frontend shape that the UI uses.
    """

    model_config = ConfigDict(populate_by_name=True)

    sector: str = Field(..., min_length=1, max_length=120)
    organization_size: str | int | None = Field(default=None, min_length=1, max_length=120)
    organizationSize: int | str | None = None
    modules: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_frontend_payload(cls, data: Any) -> Any:
        """Map the frontend camelCase organization field into the backend schema."""
        if isinstance(data, dict):
            data = dict(data)
            if "organization_size" not in data and "organizationSize" in data:
                data["organization_size"] = data["organizationSize"]
        return data


class ROIResponse(BaseModel):
    """Deterministic ROI calculation response.

    The original response fields remain intact for compatibility while the
    frontend-aligned metrics are added as optional, non-breaking fields.
    """

    estimated_roi: int
    annual_savings: int
    utility_efficiency: int
    implementation_time: str
    efficiency_gain: int | None = None
    digital_transformation_velocity: float | None = None
    projected_savings: dict[str, int] | None = None
    extras: dict[str, Any] | None = None
