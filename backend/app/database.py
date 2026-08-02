from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

settings = get_settings()

mongodb_uri = settings.mongodb_uri.strip() or "mongodb://localhost:27017"

client: AsyncIOMotorClient = AsyncIOMotorClient(mongodb_uri)

# Primary database handle for the application, named per the configured
# MongoDB database name (defaults to "lmkt_db").
lmkt_db: AsyncIOMotorDatabase = client[settings.mongodb_db_name]


def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency that provides the MongoDB database instance."""
    return lmkt_db


def close_mongo_connection() -> None:
    """Close the Motor client connection (used on application shutdown)."""
    client.close()
