"""Import du fichier Excel de fusion des bureaux de vote.

Colonnes attendues dans la feuille de données (voir feuille "Legende" du
fichier `Base_Fusion_Bureaux_Vote.xlsx`) :
    الرئيس, نائب الرئيس, رقم مكتب التصويت, الجماعة, عنوان مكتب التصويت,
    رقم المكتب المركزي, رئيس المكتب المركزي,
    العضو الأول, العضو الثاني, العضو الثالث,
    نائب العضو الأول, نائب العضو الثاني, نائب العضو الثالث
"""

import io

import openpyxl
from sqlalchemy.orm import Session

from app.models.bureau_central import BureauCentral
from app.models.bureau_vote import BureauVote
from app.schemas.import_report import ImportReport, ImportRowError

COLUMN_MAP = {
    "الرئيس": "president",
    "نائب الرئيس": "vice_president",
    "رقم مكتب التصويت": "numero_bureau",
    "الجماعة": "commune",
    "عنوان مكتب التصويت": "adresse_bureau",
    "رقم المكتب المركزي": "numero_bureau_central",
    "رئيس المكتب المركزي": "president_bureau_central",
    "العضو الأول": "membre_1",
    "العضو الثاني": "membre_2",
    "العضو الثالث": "membre_3",
    "نائب العضو الأول": "suppleant_1",
    "نائب العضو الثاني": "suppleant_2",
    "نائب العضو الثالث": "suppleant_3",
}

REQUIRED_FIELDS = list(COLUMN_MAP.values())

PREFERRED_SHEET_NAME = "Donnees_Fusion"


def _find_data_sheet(workbook: openpyxl.Workbook):
    if PREFERRED_SHEET_NAME in workbook.sheetnames:
        return workbook[PREFERRED_SHEET_NAME]
    for name in workbook.sheetnames:
        ws = workbook[name]
        header_row = [c.value for c in ws[1]]
        if any(h in COLUMN_MAP for h in header_row):
            return ws
    return workbook[workbook.sheetnames[0]]


def _clean(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def import_excel_file(db: Session, file_bytes: bytes) -> ImportReport:
    workbook = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    ws = _find_data_sheet(workbook)

    header_row = [c.value for c in ws[1]]
    header_index = {name: idx for idx, name in enumerate(header_row) if name in COLUMN_MAP}

    missing_columns = [h for h in COLUMN_MAP if h not in header_index]
    if missing_columns:
        raise ValueError(
            "Colonnes manquantes dans le fichier Excel : " + ", ".join(missing_columns)
        )

    created = 0
    updated = 0
    skipped_duplicates = 0
    bureaux_centraux_created = 0
    errors: list[ImportRowError] = []
    seen_keys: set[tuple[str, str]] = set()
    pending_centrals: dict[tuple[str, str], BureauCentral] = {}

    total_rows = 0
    for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
        values = [c.value for c in row]
        if all(v is None or str(v).strip() == "" for v in values):
            continue
        total_rows += 1

        record: dict[str, str | None] = {}
        for header, field in COLUMN_MAP.items():
            col = header_index[header]
            record[field] = _clean(values[col]) if col < len(values) else None

        row_errors = [field for field in REQUIRED_FIELDS if not record.get(field)]
        if row_errors:
            errors.append(
                ImportRowError(
                    row=row_idx,
                    message=f"Champs obligatoires manquants : {', '.join(row_errors)}",
                )
            )
            continue

        key = (record["commune"], record["numero_bureau"])
        if key in seen_keys:
            skipped_duplicates += 1
            continue
        seen_keys.add(key)

        existing = (
            db.query(BureauVote)
            .filter(BureauVote.commune == key[0], BureauVote.numero_bureau == key[1])
            .one_or_none()
        )
        if existing:
            for field, value in record.items():
                setattr(existing, field, value)
            updated += 1
        else:
            db.add(BureauVote(**record))
            created += 1

        central_key = (record["commune"], record["numero_bureau_central"])
        existing_central = pending_centrals.get(central_key) or (
            db.query(BureauCentral)
            .filter(
                BureauCentral.commune == central_key[0],
                BureauCentral.numero_bureau_central == central_key[1],
            )
            .one_or_none()
        )
        if existing_central:
            existing_central.president_bureau_central = record["president_bureau_central"]
            pending_centrals[central_key] = existing_central
        else:
            new_central = BureauCentral(
                numero_bureau_central=record["numero_bureau_central"],
                commune=record["commune"],
                president_bureau_central=record["president_bureau_central"],
            )
            db.add(new_central)
            pending_centrals[central_key] = new_central
            bureaux_centraux_created += 1

    db.commit()

    return ImportReport(
        total_rows=total_rows,
        created=created,
        updated=updated,
        skipped_duplicates=skipped_duplicates,
        errors=errors,
        bureaux_centraux_created=bureaux_centraux_created,
    )
