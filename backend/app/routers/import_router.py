from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.import_report import ImportReport
from app.services.excel_import import import_excel_file

router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/excel", response_model=ImportReport)
def import_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Le fichier doit être un fichier Excel (.xlsx)")

    content = file.file.read()
    try:
        return import_excel_file(db, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
