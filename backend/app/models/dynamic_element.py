from sqlalchemy import Column, String, DateTime, Text, Enum
from sqlalchemy.sql import func
import enum
import uuid

from app.core.database import Base


class MethodEnum(str, enum.Enum):
    reasoning = "reasoning"
    extraction = "extraction"
    direct = "direct"


class StatusEnum(str, enum.Enum):
    draft = "draft"
    validated = "validated"


class DynamicElement(Base):
    __tablename__ = "dynamic_elements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    ai_model = Column(String(100), nullable=False)
    method = Column(Enum(MethodEnum), nullable=True)
    file_type = Column(String(50), nullable=False)
    data_sources = Column(Text, nullable=False)  # JSON string of array
    status = Column(Enum(StatusEnum), default=StatusEnum.draft, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)