from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class MethodEnum(str, Enum):
    reasoning = "reasoning"
    extraction = "extraction"
    direct = "direct"


class StatusEnum(str, Enum):
    draft = "draft"
    validated = "validated"


class DynamicElementBase(BaseModel):
    name: str
    prompt: str
    ai_model: str
    method: Optional[MethodEnum] = None
    file_type: str
    data_sources: List[str]


class DynamicElementCreate(DynamicElementBase):
    pass


class DynamicElementUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    ai_model: Optional[str] = None
    method: Optional[MethodEnum] = None
    file_type: Optional[str] = None
    data_sources: Optional[List[str]] = None


class DynamicElementInDB(DynamicElementBase):
    id: str
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        # Convert JSON string to list if needed
        if hasattr(obj, 'data_sources') and isinstance(obj.data_sources, str):
            import json
            obj.data_sources = json.loads(obj.data_sources)
        return super().model_validate(obj)


class DynamicElement(DynamicElementInDB):
    pass