from __future__ import annotations

from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """ObjectId wrapper that lets Pydantic v2 validate and serialize MongoDB's `_id`.

    Accepts a `bson.ObjectId` or a valid ObjectId string on input, and
    serializes to a plain string (so it converts cleanly to `id` in JSON
    responses).
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate(value: Any) -> ObjectId:
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str) and ObjectId.is_valid(value):
                return ObjectId(value)
            raise ValueError("Invalid ObjectId")

        return core_schema.no_info_plain_validator_function(
            validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                str, return_schema=core_schema.str_schema()
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        json_schema = handler(core_schema.str_schema())
        json_schema.update(type="string", example="66f1a2b3c4d5e6f7a8b9c0d1")
        return json_schema


class Lead(BaseModel):
    """MongoDB document model for collected leads (`leads` collection)."""

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: str
    phone: str
    company: str
    sector: str
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }
