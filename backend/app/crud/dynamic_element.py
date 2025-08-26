import json
from typing import List, Dict, Any, Union
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.dynamic_element import DynamicElement
from app.schemas.dynamic_element import DynamicElementCreate, DynamicElementUpdate


class CRUDDynamicElement(CRUDBase[DynamicElement, DynamicElementCreate, DynamicElementUpdate]):
    def create(self, db: Session, *, obj_in: DynamicElementCreate) -> DynamicElement:
        # Convert data_sources list to JSON string for storage
        obj_data = obj_in.dict()
        obj_data["data_sources"] = json.dumps(obj_data["data_sources"])
        
        db_obj = DynamicElement(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Convert JSON string back to list for response
        db_obj.data_sources = json.loads(db_obj.data_sources) if isinstance(db_obj.data_sources, str) else db_obj.data_sources
        return db_obj

    def get(self, db: Session, id: str) -> DynamicElement:
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            # Convert JSON string back to list
            db_obj.data_sources = json.loads(db_obj.data_sources) if isinstance(db_obj.data_sources, str) else db_obj.data_sources
        return db_obj

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[DynamicElement]:
        db_objs = db.query(self.model).offset(skip).limit(limit).all()
        for db_obj in db_objs:
            # Convert JSON string back to list
            db_obj.data_sources = json.loads(db_obj.data_sources) if isinstance(db_obj.data_sources, str) else db_obj.data_sources
        return db_objs

    def update(
        self,
        db: Session,
        *,
        db_obj: DynamicElement,
        obj_in: Union[DynamicElementUpdate, Dict[str, Any]]
    ) -> DynamicElement:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        # Convert data_sources list to JSON string if present
        if "data_sources" in update_data:
            update_data["data_sources"] = json.dumps(update_data["data_sources"])
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Convert JSON string back to list for response
        db_obj.data_sources = json.loads(db_obj.data_sources) if isinstance(db_obj.data_sources, str) else db_obj.data_sources
        return db_obj

    def validate_element(self, db: Session, *, id: str) -> DynamicElement:
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            db_obj.status = "validated"
            db.commit()
            db.refresh(db_obj)
            # Convert JSON string back to list
            db_obj.data_sources = json.loads(db_obj.data_sources) if isinstance(db_obj.data_sources, str) else db_obj.data_sources
        return db_obj


dynamic_element = CRUDDynamicElement(DynamicElement)