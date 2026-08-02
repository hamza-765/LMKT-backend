from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import close_mongo_connection, lmkt_db
from app.logger import configure_logging
from app.middleware import RequestLoggingMiddleware
from app.routers.chatbot import router as chatbot_router
from app.routers.leads import router as leads_router
from app.routers.roi import router as roi_router
from app.utils.exceptions import AppError, app_exception_handler, http_exception_handler, unhandled_exception_handler

logger = logging.getLogger("lmkt.backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    # Verify the MongoDB connection is reachable on startup.
    await lmkt_db.command("ping")
    logger.info("Application startup complete")
    yield
    close_mongo_connection()
    logger.info("Application shutdown complete")


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="LMKT landing page backend API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(AppError, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(chatbot_router, prefix="/api")
app.include_router(roi_router, prefix="/api")
app.include_router(leads_router, prefix="/api")

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "LMKT Backend is running"
    }

@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple health check response."""
    return {"status": "ok"}


@app.exception_handler(404)
async def not_found_handler(_, __):
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.exception_handler(422)
async def validation_handler(_, exc):
    return JSONResponse(status_code=422, content={"detail": exc.detail if hasattr(exc, "detail") else "Validation error"})


@app.exception_handler(400)
async def bad_request_handler(_, exc):
    return JSONResponse(status_code=400, content={"detail": exc.detail if hasattr(exc, "detail") else "Bad request"})
