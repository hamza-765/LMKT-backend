from __future__ import annotations

import re

from fastapi import HTTPException

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_text(value: str | None, *, field_name: str, max_length: int = 500) -> str:
    """Normalize, trim, and validate user text input."""
    if value is None:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")

    cleaned = value.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    if len(cleaned) > max_length:
        raise HTTPException(status_code=400, detail=f"{field_name} exceeds maximum length")
    return cleaned


def validate_email(value: str) -> str:
    """Validate an email address string."""
    normalized = normalize_text(value, field_name="email", max_length=255)
    if not EMAIL_REGEX.match(normalized):
        raise HTTPException(status_code=422, detail="Invalid email format")
    return normalized


def validate_required_fields(payload: dict, required_fields: list[str]) -> None:
    """Ensure all required fields are present and non-empty."""
    for field in required_fields:
        if field not in payload or payload[field] is None or not str(payload[field]).strip():
            raise HTTPException(status_code=400, detail=f"{field} is required")
