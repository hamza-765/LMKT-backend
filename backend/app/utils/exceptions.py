from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application exception for structured error handling."""

    def __init__(self, status_code: int, detail: str, *, headers: dict[str, Any] | None = None) -> None:
        self.status_code = status_code
        self.detail = detail
        self.headers = headers or {}
        super().__init__(detail)


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle application-level custom exceptions centrally."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return sanitized HTTP exceptions without exposing internals."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions centrally and keep the response sanitized."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
