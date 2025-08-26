import json
from typing import List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.dataset_entry import DatasetEntry
from app.schemas.dataset_entry import DatasetEntryCreate


class CRUDDatasetEntry(CRUDBase[DatasetEntry, DatasetEntryCreate, DatasetEntryCreate]):
    def create(self, db: Session, *, obj_in: DatasetEntryCreate) -> DatasetEntry:
        # Convert json_config dict to JSON string
        obj_data = obj_in.dict()
        obj_data["json_config"] = json.dumps(obj_data["json_config"])
        
        db_obj = DatasetEntry(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: str) -> DatasetEntry:
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            # Convert JSON string back to dict
            db_obj.json_config = json.loads(db_obj.json_config) if isinstance(db_obj.json_config, str) else db_obj.json_config
        return db_obj

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[DatasetEntry]:
        db_objs = db.query(self.model).offset(skip).limit(limit).all()
        for db_obj in db_objs:
            # Convert JSON string back to dict
            db_obj.json_config = json.loads(db_obj.json_config) if isinstance(db_obj.json_config, str) else db_obj.json_config
        return db_objs


dataset_entry = CRUDDatasetEntry(DatasetEntry)