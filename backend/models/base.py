from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from typing import Optional
from datetime import datetime
from pydantic_core import core_schema

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler: GetCoreSchemaHandler):
        # Use str validation, then convert to ObjectId
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def validate(cls, v: str) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        try:
            return str(ObjectId(v))
        except Exception:
            raise ValueError("Invalid ObjectId")


class MongoModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        # Allow both "_id" and "id" when creating model
        allow_population_by_field_name = True
        # Automatically convert ObjectId → str in JSON
        json_encoders = {ObjectId: str}
        # Extra fields ignored instead of breaking
        arbitrary_types_allowed = True
