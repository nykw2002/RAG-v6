from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class DatasetEntry(Base):
    __tablename__ = "dataset_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    element_id = Column(String, ForeignKey("dynamic_elements.id", ondelete="CASCADE"), nullable=False)
    element_name = Column(String(255), nullable=False)
    json_config = Column(Text, nullable=False)  # JSON string of complete config
    ai_output = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationship with cascade delete
    element = relationship("DynamicElement", backref="dataset_entries")