from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime


class DatasetEntryBase(BaseModel):
    element_id: str
    element_name: str
    json_config: Dict[str, Any]
    ai_output: str


class DatasetEntryCreate(DatasetEntryBase):
    pass


class DatasetEntryInDB(DatasetEntryBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetEntry(DatasetEntryInDB):
    pass