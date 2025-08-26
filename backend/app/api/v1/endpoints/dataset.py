from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import dataset_entry
from app.schemas.dataset_entry import DatasetEntry, DatasetEntryCreate

router = APIRouter()


@router.get("/", response_model=List[DatasetEntry])
def read_dataset_entries(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve dataset entries.
    """
    entries = dataset_entry.get_multi(db, skip=skip, limit=limit)
    return entries


@router.post("/", response_model=DatasetEntry)
def create_dataset_entry(
    *,
    db: Session = Depends(get_db),
    entry_in: DatasetEntryCreate,
):
    """
    Create new dataset entry.
    """
    entry = dataset_entry.create(db=db, obj_in=entry_in)
    return entry


@router.get("/{entry_id}", response_model=DatasetEntry)
def read_dataset_entry(
    *,
    db: Session = Depends(get_db),
    entry_id: str,
):
    """
    Get dataset entry by ID.
    """
    entry = dataset_entry.get(db=db, id=entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset entry not found")
    return entry


@router.delete("/{entry_id}")
def delete_dataset_entry(
    *,
    db: Session = Depends(get_db),
    entry_id: str,
):
    """
    Delete a dataset entry.
    """
    entry = dataset_entry.get(db=db, id=entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset entry not found")
    dataset_entry.remove(db=db, id=entry_id)
    return {"message": "Dataset entry deleted successfully"}