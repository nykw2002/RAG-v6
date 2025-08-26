import os
import aiofiles
import uuid
from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.crud import uploaded_file
from app.schemas.uploaded_file import UploadedFile as UploadedFileSchema

router = APIRouter()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)


def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file"""
    if not file.filename:
        return False
    
    # Check file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        return False
    
    return True


@router.post("/upload", response_model=List[UploadedFileSchema])
async def upload_files(
    files: List[UploadFile] = File(...),
    element_id: str = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload files and store metadata in database.
    """
    uploaded_files = []
    
    for file in files:
        if not validate_file(file):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type for {file.filename}. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is too large. Maximum size: {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB"
            )
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
        
        # Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Save metadata to database
        file_data = {
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_size": len(file_content),
            "content_type": file.content_type or "application/octet-stream",
            "element_id": element_id
        }
        
        db_file = uploaded_file.create(db=db, obj_in=file_data)
        uploaded_files.append(db_file)
        
        # Reset file position for next iteration
        await file.seek(0)
    
    return uploaded_files


@router.get("/{file_id}", response_class=FileResponse)
async def get_file(
    file_id: str,
    db: Session = Depends(get_db),
):
    """
    Download a file by ID.
    """
    db_file = uploaded_file.get(db=db, id=file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=db_file.file_path,
        filename=db_file.original_filename,
        media_type=db_file.content_type
    )


@router.get("/", response_model=List[UploadedFileSchema])
def list_files(
    element_id: str = None,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    List uploaded files, optionally filtered by element_id.
    """
    if element_id:
        files = db.query(uploaded_file.model).filter(
            uploaded_file.model.element_id == element_id
        ).offset(skip).limit(limit).all()
    else:
        files = uploaded_file.get_multi(db, skip=skip, limit=limit)
    
    return files


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a file and its metadata.
    """
    db_file = uploaded_file.get(db=db, id=file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete file from disk
    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)
    
    # Delete metadata from database
    uploaded_file.remove(db=db, id=file_id)
    
    return {"message": "File deleted successfully"}