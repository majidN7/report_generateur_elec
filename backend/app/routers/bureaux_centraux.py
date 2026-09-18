from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bureau_central import BureauCentral
from app.schemas.bureau_central import (
    BureauCentralCreate,
    BureauCentralOut,
    BureauCentralPage,
    BureauCentralUpdate,
)
from app.services import word_merge

router = APIRouter(prefix="/api/bureaux-centraux", tags=["bureaux-centraux"])

SORTABLE_FIELDS = {
    "numero_bureau_central": BureauCentral.numero_bureau_central,
    "commune": BureauCentral.commune,
    "president_bureau_central": BureauCentral.president_bureau_central,
    "created_at": BureauCentral.created_at,
    "updated_at": BureauCentral.updated_at,
}

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PDF_MEDIA_TYPE = "application/pdf"
ZIP_MEDIA_TYPE = "application/zip"


def _stream(data: bytes, media_type: str, filename: str) -> StreamingResponse:
    ascii_fallback = filename.encode("ascii", "ignore").decode("ascii") or "document"
    quoted = quote(filename)
    disposition = f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{quoted}"
    return StreamingResponse(
        iter([data]),
        media_type=media_type,
        headers={"Content-Disposition": disposition},
    )


@router.get("", response_model=BureauCentralPage)
def list_bureaux_centraux(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: str | None = Query(None),
    commune: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
):
    query = db.query(BureauCentral)

    if commune:
        query = query.filter(BureauCentral.commune == commune)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                BureauCentral.numero_bureau_central.ilike(like),
                BureauCentral.commune.ilike(like),
                BureauCentral.president_bureau_central.ilike(like),
            )
        )

    total = query.count()

    sort_column = SORTABLE_FIELDS.get(sort_by, BureauCentral.created_at)
    sort_column = sort_column.desc() if sort_dir == "desc" else sort_column.asc()
    query = query.order_by(sort_column)

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return BureauCentralPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{bureau_id}", response_model=BureauCentralOut)
def get_bureau_central(bureau_id: int, db: Session = Depends(get_db)):
    bureau = db.get(BureauCentral, bureau_id)
    if not bureau:
        raise HTTPException(status_code=404, detail="Bureau central introuvable")
    return bureau


@router.post("", response_model=BureauCentralOut, status_code=201)
def create_bureau_central(payload: BureauCentralCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(BureauCentral)
        .filter(
            BureauCentral.commune == payload.commune,
            BureauCentral.numero_bureau_central == payload.numero_bureau_central,
        )
        .one_or_none()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Un bureau central avec ce numéro existe déjà pour cette commune",
        )

    bureau = BureauCentral(**payload.model_dump())
    db.add(bureau)
    db.commit()
    db.refresh(bureau)
    return bureau


@router.put("/{bureau_id}", response_model=BureauCentralOut)
def update_bureau_central(bureau_id: int, payload: BureauCentralUpdate, db: Session = Depends(get_db)):
    bureau = db.get(BureauCentral, bureau_id)
    if not bureau:
        raise HTTPException(status_code=404, detail="Bureau central introuvable")

    data = payload.model_dump(exclude_unset=True)

    new_commune = data.get("commune", bureau.commune)
    new_numero = data.get("numero_bureau_central", bureau.numero_bureau_central)
    if (new_commune, new_numero) != (bureau.commune, bureau.numero_bureau_central):
        conflict = (
            db.query(BureauCentral)
            .filter(
                BureauCentral.commune == new_commune,
                BureauCentral.numero_bureau_central == new_numero,
                BureauCentral.id != bureau_id,
            )
            .one_or_none()
        )
        if conflict:
            raise HTTPException(
                status_code=409,
                detail="Un bureau central avec ce numéro existe déjà pour cette commune",
            )

    for field, value in data.items():
        setattr(bureau, field, value)

    db.commit()
    db.refresh(bureau)
    return bureau


@router.delete("/{bureau_id}", status_code=204)
def delete_bureau_central(bureau_id: int, db: Session = Depends(get_db)):
    bureau = db.get(BureauCentral, bureau_id)
    if not bureau:
        raise HTTPException(status_code=404, detail="Bureau central introuvable")
    db.delete(bureau)
    db.commit()


@router.get("/{bureau_id}/document")
def download_document(bureau_id: int, format: str = Query("docx", pattern="^(docx|pdf)$"), db: Session = Depends(get_db)):
    bureau = db.get(BureauCentral, bureau_id)
    if not bureau:
        raise HTTPException(status_code=404, detail="Bureau central introuvable")

    try:
        docx_bytes = word_merge.render_bureau_central_docx(bureau)
    except word_merge.MissingFieldsError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if format == "docx":
        filename = word_merge.bureau_central_filename(bureau, "docx")
        return _stream(docx_bytes, DOCX_MEDIA_TYPE, filename)

    try:
        pdf_bytes = word_merge.convert_docx_to_pdf(docx_bytes)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    filename = word_merge.bureau_central_filename(bureau, "pdf")
    return _stream(pdf_bytes, PDF_MEDIA_TYPE, filename)


@router.post("/generate-batch")
def generate_batch(
    format: str = Query("docx", pattern="^(docx|pdf)$"),
    ids: str | None = Query(None, description="Liste d'identifiants séparés par des virgules, vide = tous"),
    db: Session = Depends(get_db),
):
    query = db.query(BureauCentral)
    if ids:
        id_list = [int(i) for i in ids.split(",") if i.strip()]
        query = query.filter(BureauCentral.id.in_(id_list))

    bureaux = query.order_by(BureauCentral.commune, BureauCentral.numero_bureau_central).all()
    if not bureaux:
        raise HTTPException(status_code=404, detail="Aucun bureau central à générer")

    files: list[tuple[str, bytes]] = []
    skipped: list[str] = []
    for bureau in bureaux:
        try:
            docx_bytes = word_merge.render_bureau_central_docx(bureau)
        except word_merge.MissingFieldsError:
            skipped.append(f"{bureau.commune} / {bureau.numero_bureau_central}")
            continue
        if format == "docx":
            files.append((word_merge.bureau_central_filename(bureau, "docx"), docx_bytes))
        else:
            try:
                pdf_bytes = word_merge.convert_docx_to_pdf(docx_bytes)
            except RuntimeError as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc
            files.append((word_merge.bureau_central_filename(bureau, "pdf"), pdf_bytes))

    if not files:
        raise HTTPException(
            status_code=422,
            detail="Aucun bureau central complet à générer (champs manquants pour tous)",
        )

    zip_bytes = word_merge.build_zip(files)
    response = _stream(zip_bytes, ZIP_MEDIA_TYPE, "arretes_bureaux_centraux.zip")
    if skipped:
        response.headers["X-Skipped-Incomplete"] = str(len(skipped))
    return response
