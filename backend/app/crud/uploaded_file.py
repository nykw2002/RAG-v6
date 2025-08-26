from app.crud.base import CRUDBase
from app.models.uploaded_file import UploadedFile
from app.schemas.uploaded_file import UploadedFileBase


class CRUDUploadedFile(CRUDBase[UploadedFile, UploadedFileBase, UploadedFileBase]):
    pass


uploaded_file = CRUDUploadedFile(UploadedFile)