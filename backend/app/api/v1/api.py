from fastapi import APIRouter

from app.api.v1.endpoints import elements, dataset, files

api_router = APIRouter()
api_router.include_router(elements.router, prefix="/elements", tags=["elements"])
api_router.include_router(dataset.router, prefix="/dataset", tags=["dataset"])
api_router.include_router(files.router, prefix="/files", tags=["files"])