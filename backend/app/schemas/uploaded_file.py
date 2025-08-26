from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UploadedFileBase(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    content_type: str
    element_id: Optional[str] = None


class UploadedFileInDB(UploadedFileBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UploadedFile(UploadedFileInDB):
    pass