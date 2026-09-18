from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bureau_vote import BureauVote
from app.schemas.bureau_vote import (
    BureauVoteCreate,
    BureauVoteOut,
    BureauVotePage,
    BureauVoteUpdate,
)
from app.services import word_merge

router = APIRouter(prefix="/api/bureaux", tags=["bureaux"])

SORTABLE_FIELDS = {
    "numero_bureau": BureauVote.numero_bureau,
    "commune": BureauVote.commune,
    "president": BureauVote.president,
    "created_at": BureauVote.created_at,
    "updated_at": BureauVote.updated_at,
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


@router.get("", response_model=BureauVotePage)
def list_bureaux(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: str | None = Query(None),
    commune: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
):
    query = db.query(BureauVote)

    if commune:
        query = query.filter(BureauVote.commune == commune)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                BureauVote.numero_bureau.ilike(like),
                BureauVote.commune.ilike(like),
                BureauVote.president.ilike(like),
                BureauVote.vice_president.ilike(like),
                BureauVote.adresse_bureau.ilike(like),
            )
        )

    total = query.count()

    sort_column = SORTABLE_FIELDS.get(sort_by, BureauVote.created_at)
    sort_column = sort_column.desc() if sort_dir == "desc" else sort_column.asc()
    query = query.order_by(sort_column)

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return BureauVotePage(items=items, total=total, page=page, page_size=page_size)


@router.get("/communes", response_model=list[str])
def list_communes(db: Session = Depends(get_db)):
    rows = db.query(BureauVote.commune).distinct().order_by(BureauVote.commune).all()
    return [r[0] for r in rows]


@router.get("/{bureau_id}", response_model=BureauVoteOut)
def get_bureau(bureau_id: int, db: Session = Depends(get_db)):
    bureau = db.get(BureauVote, bureau_id)
    if not bureau:
        raise HTTPException(status_code=404, detail="Bureau de vote introuvable")
    return bureau


@router.post("", response_model=BureauVoteOut, status_code=201)
def create_bureau(payload: BureauVoteCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(BureauVote)
        .filter(BureauVote.commune == payload.commune, BureauVote.numero_bureau == payload.numero_bureau)
        .one_or_none()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Un bureau de vote avec ce numéro existe déjà pour cette commune",
        )

    bureau = BureauVote(**payload.model_dump())
    db.add(bureau)
    db.commit()
    db.refresh(bureau)
    return bureau


@router.put("/{bureau_id}", response_model=BureauVoteOut)
def update_bureau(bureau_id: int, payload: BureauVoteUpdate, db: Session = Depends(get_db)):
    bureau = db.get(BureauVote, bureau_id)
    if not bureau:
        raise HTTPException(status_code=404, detail="Bureau de vote introuvable")

    data = payload.model_dump(exclude_unset=True)

    new_commune = data.get("commune", bureau.commune)
    new_numero = data.get("numero_bureau", bureau.numero_bureau)
    if (new_commune, new_numero) != (bureau.commune, bureau.numero_bureau):
        conflict = (
            db.query(BureauVote)
            .filter(
                BureauVote.commune == new_commune,
                BureauVote.numero_bureau == new_numero,
                BureauVote.id != bureau_id,
            )
            .one_or_none()
        )
        if conflict:
            raise HTTPException(
                status_code=409,
                detail="Un bureau de vote avec ce numéro existe déjà pour cette commune",
            )

    for field, value in data.items():
        setattr(bureau, field, value)

    db.commit()
    db.refresh(bureau)
    return bureau


@router.delete("/{bureau_id}", status_code=204)
def delete_bureau(bureau_id: int, db: Session = Depends(get_db)):
    bureau = db.get(BureauVote, bureau_id)
    if not bureau:
        raise HTTPException(status_code=404, detail="Bureau de vote introuvable")
    db.delete(bureau)
    db.commit()


@router.get("/{bureau_id}/document")
def download_document(bureau_id: int, format: str = Query("docx", pattern="^(docx|pdf)$"), db: Session = Depends(get_db)):
    bureau = db.get(BureauVote, bureau_id)
    if not bureau:
        raise HTTPException(status_code=404, detail="Bureau de vote introuvable")

    docx_bytes = word_merge.render_bureau_vote_docx(bureau)
    if format == "docx":
        filename = word_merge.bureau_vote_filename(bureau, "docx")
        return _stream(docx_bytes, DOCX_MEDIA_TYPE, filename)

    try:
        pdf_bytes = word_merge.convert_docx_to_pdf(docx_bytes)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    filename = word_merge.bureau_vote_filename(bureau, "pdf")
    return _stream(pdf_bytes, PDF_MEDIA_TYPE, filename)


@router.post("/generate-batch")
def generate_batch(
    format: str = Query("docx", pattern="^(docx|pdf)$"),
    ids: str | None = Query(None, description="Liste d'identifiants séparés par des virgules, vide = tous"),
    db: Session = Depends(get_db),
):
    query = db.query(BureauVote)
    if ids:
        id_list = [int(i) for i in ids.split(",") if i.strip()]
        query = query.filter(BureauVote.id.in_(id_list))

    bureaux = query.order_by(BureauVote.commune, BureauVote.numero_bureau).all()
    if not bureaux:
        raise HTTPException(status_code=404, detail="Aucun bureau de vote à générer")

    files: list[tuple[str, bytes]] = []
    for bureau in bureaux:
        docx_bytes = word_merge.render_bureau_vote_docx(bureau)
        if format == "docx":
            files.append((word_merge.bureau_vote_filename(bureau, "docx"), docx_bytes))
        else:
            try:
                pdf_bytes = word_merge.convert_docx_to_pdf(docx_bytes)
            except RuntimeError as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc
            files.append((word_merge.bureau_vote_filename(bureau, "pdf"), pdf_bytes))

    zip_bytes = word_merge.build_zip(files)
    return _stream(zip_bytes, ZIP_MEDIA_TYPE, "arretes_bureaux_vote.zip")
