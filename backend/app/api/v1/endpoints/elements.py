from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import json

from app.api.deps import get_db
from app.crud import dynamic_element
from app.schemas.dynamic_element import DynamicElement, DynamicElementCreate, DynamicElementUpdate
from app.services.openai_client import get_ai_engine

router = APIRouter()


@router.get("/", response_model=List[DynamicElement])
def read_elements(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve dynamic elements.
    """
    elements = dynamic_element.get_multi(db, skip=skip, limit=limit)
    return elements


@router.post("/", response_model=DynamicElement)
def create_element(
    *,
    db: Session = Depends(get_db),
    element_in: DynamicElementCreate,
):
    """
    Create new dynamic element.
    """
    element = dynamic_element.create(db=db, obj_in=element_in)
    return element


@router.get("/{element_id}", response_model=DynamicElement)
def read_element(
    *,
    db: Session = Depends(get_db),
    element_id: str,
):
    """
    Get dynamic element by ID.
    """
    element = dynamic_element.get(db=db, id=element_id)
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    return element


@router.put("/{element_id}", response_model=DynamicElement)
def update_element(
    *,
    db: Session = Depends(get_db),
    element_id: str,
    element_in: DynamicElementUpdate,
):
    """
    Update a dynamic element.
    """
    element = dynamic_element.get(db=db, id=element_id)
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    element = dynamic_element.update(db=db, db_obj=element, obj_in=element_in)
    return element


@router.delete("/{element_id}")
def delete_element(
    *,
    db: Session = Depends(get_db),
    element_id: str,
):
    """
    Delete a dynamic element.
    """
    element = dynamic_element.get(db=db, id=element_id)
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    dynamic_element.remove(db=db, id=element_id)
    return {"message": "Element deleted successfully"}


@router.post("/{element_id}/validate", response_model=DynamicElement)
def validate_element(
    *,
    db: Session = Depends(get_db),
    element_id: str,
):
    """
    Mark an element as validated.
    """
    element = dynamic_element.validate_element(db=db, id=element_id)
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    return element


@router.post("/{element_id}/analyze")
def analyze_element(
    *,
    db: Session = Depends(get_db),
    element_id: str,
    files: List[UploadFile] = File(...),
    additional_data: str = Form(default=""),
):
    """
    Process files with AI analysis for a dynamic element.
    """
    try:
        # Get the element configuration
        element = dynamic_element.get(db=db, id=element_id)
        if not element:
            raise HTTPException(status_code=404, detail="Element not found")
        
        # Initialize AI engine
        ai_engine = get_ai_engine()
        
        # Process uploaded files
        file_contents = []
        file_names = []
        
        for file in files:
            try:
                content = file.file.read().decode('utf-8')
                file_contents.append(content)
                file_names.append(file.filename)
            except UnicodeDecodeError:
                # Handle binary files or different encodings
                content = file.file.read().decode('latin-1', errors='ignore')
                file_contents.append(content)
                file_names.append(file.filename)
            except Exception as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Error reading file {file.filename}: {str(e)}"
                )
        
        # Combine all file contents
        combined_content = "\n\n--- FILE SEPARATOR ---\n\n".join([
            f"FILE: {name}\n{content}" 
            for name, content in zip(file_names, file_contents)
        ])
        
        # Add additional data if provided
        if additional_data.strip():
            combined_content += f"\n\n--- ADDITIONAL DATA ---\n\n{additional_data}"
        
        # Run AI analysis
        analysis_result = ai_engine.analyze(
            prompt=element.prompt,
            method=element.method,
            file_content=combined_content,
            filename=", ".join(file_names) if file_names else "uploaded_files"
        )
        
        return {
            "success": True,
            "analysis_result": analysis_result,
            "element_id": element_id,
            "files_processed": len(files),
            "method_used": element.method
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )