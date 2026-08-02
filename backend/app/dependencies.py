from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import get_settings
from app.database import get_database

SettingsDep = Annotated[object, Depends(get_settings)]
DbDep = Annotated[AsyncIOMotorDatabase, Depends(get_database)]
