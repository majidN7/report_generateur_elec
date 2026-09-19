"""Import dédié du fichier Excel des bureaux de vote centraux.

Contrairement à l'import du fichier principal des bureaux de vote (qui ne
fait que créer des fiches "bureau central" minimales — numéro, commune et
président — à compléter manuellement), ce fichier est la source dédiée et
complète des bureaux centraux : il alimente donc tous les champs de
`BureauCentral` (upsert complet), y compris le vice-président, les membres,
les suppléants, l'adresse et le CIN de chaque personne.

Colonnes attendues dans la feuille de données (en-têtes exacts du modèle
Excel officiel "Base_Fusion_Bureaux_Vote__BV.xlsx", feuille
"مكاتب التصويت المركزية") :
    رئيس المكتب المركزي, بطاقة التعريف الوطنية رئيس المكتب المركزي,
    رقم المكتب المركزي, الجماعة, عنوان مكتب التصويت,
    نائب رئيس المكتب المركزي, بطاقة التعريف الوطنية نائب رئيس المكتب المركزي,
    العضو الأول/الثاني/الثالث + بطاقة التعريف الوطنية عضو الأول/الثاني/الثالث,
    نائب العضو الأول/الثاني/الثالث + بطاقة التعريف الوطنية نائب العضو
    الأول/الثاني/الثالث

Seules الجماعة, رقم المكتب المركزي et رئيس المكتب المركزي sont obligatoires
pour l'import ; le reste (CIN compris) est optionnel au stockage mais
requis pour générer l'arrêté (voir word_merge.py). Si les en-têtes de votre
fichier diffèrent de cette liste, adaptez `COLUMN_MAP` ci-dessous.
"""

import io

import openpyxl
from sqlalchemy.orm import Session

from app.models.bureau_central import BureauCentral
from app.schemas.import_report import ImportReport, ImportRowError

COLUMN_MAP = {
    "رئيس المكتب المركزي": "president_bureau_central",
    "بطاقة التعريف الوطنية رئيس المكتب المركزي": "president_cin",
    "رقم المكتب المركزي": "numero_bureau_central",
    "الجماعة": "commune",
    "عنوان مكتب التصويت": "adresse_bureau_central",
    "نائب رئيس المكتب المركزي": "vice_president_bureau_central",
    "بطاقة التعريف الوطنية نائب رئيس المكتب المركزي": "vice_president_cin",
    "العضو الأول": "membre_central_1",
    "بطاقة التعريف الوطنية عضو الأول": "membre_central_1_cin",
    "العضو الثاني": "membre_central_2",
    "بطاقة التعريف الوطنية عضو الثاني": "membre_central_2_cin",
    "العضو الثالث": "membre_central_3",
    "بطاقة التعريف الوطنية عضو الثالث": "membre_central_3_cin",
    "نائب العضو الأول": "suppleant_central_1",
    "بطاقة التعريف الوطنية نائب العضو الأول": "suppleant_central_1_cin",
    "نائب العضو الثاني": "suppleant_central_2",
    "بطاقة التعريف الوطنية نائب العضو الثاني": "suppleant_central_2_cin",
    "نائب العضو الثالث": "suppleant_central_3",
    "بطاقة التعريف الوطنية نائب العضو الثالث": "suppleant_central_3_cin",
}

REQUIRED_FIELDS = ["commune", "numero_bureau_central", "president_bureau_central"]
OPTIONAL_FIELDS = [f for f in COLUMN_MAP.values() if f not in REQUIRED_FIELDS]

PREFERRED_SHEET_NAMES = ["مكاتب التصويت المركزية", "Bureaux_Centraux", "Donnees_Bureaux_Centraux"]


def find_central_sheet(workbook: openpyxl.Workbook):
    """Locate the central-bureaux worksheet, tolerant of trailing/leading
    whitespace in sheet names (the official file has some)."""
    stripped = {name.strip(): name for name in workbook.sheetnames}
    for preferred in PREFERRED_SHEET_NAMES:
        if preferred in stripped:
            return workbook[stripped[preferred]]
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


def import_central_worksheet(db: Session, ws) -> ImportReport:
    """Core import loop, reusable on any worksheet object — including one
    found inside a workbook that also contains the ordinary bureaux sheet
    (see excel_import.py's dual-sheet format)."""
    header_row = [c.value for c in ws[1]]
    header_index = {name: idx for idx, name in enumerate(header_row) if name in COLUMN_MAP}

    missing_required_columns = [
        h for h, field in COLUMN_MAP.items() if field in REQUIRED_FIELDS and h not in header_index
    ]
    if missing_required_columns:
        raise ValueError(
            "Colonnes obligatoires manquantes dans le fichier Excel (bureaux centraux) : "
            + ", ".join(missing_required_columns)
        )

    created = 0
    updated = 0
    skipped_duplicates = 0
    errors: list[ImportRowError] = []
    seen_keys: set[tuple[str, str]] = set()
    pending: dict[tuple[str, str], BureauCentral] = {}

    total_rows = 0
    for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
        values = [c.value for c in row]
        if all(v is None or str(v).strip() == "" for v in values):
            continue
        total_rows += 1

        record: dict[str, str | None] = {}
        for header, field in COLUMN_MAP.items():
            col = header_index.get(header)
            record[field] = _clean(values[col]) if col is not None and col < len(values) else None

        missing = [field for field in REQUIRED_FIELDS if not record.get(field)]
        if missing:
            errors.append(
                ImportRowError(row=row_idx, message=f"Champs obligatoires manquants : {', '.join(missing)}")
            )
            continue

        key = (record["commune"], record["numero_bureau_central"])
        if key in seen_keys:
            skipped_duplicates += 1
            continue
        seen_keys.add(key)

        existing = pending.get(key) or (
            db.query(BureauCentral)
            .filter(BureauCentral.commune == key[0], BureauCentral.numero_bureau_central == key[1])
            .one_or_none()
        )
        if existing:
            existing.president_bureau_central = record["president_bureau_central"]
            for field in OPTIONAL_FIELDS:
                if record.get(field):
                    setattr(existing, field, record[field])
            pending[key] = existing
            updated += 1
        else:
            new_bureau = BureauCentral(
                commune=record["commune"],
                numero_bureau_central=record["numero_bureau_central"],
                president_bureau_central=record["president_bureau_central"],
                **{field: record.get(field) for field in OPTIONAL_FIELDS},
            )
            db.add(new_bureau)
            pending[key] = new_bureau
            created += 1

    db.commit()

    return ImportReport(
        total_rows=total_rows,
        created=created,
        updated=updated,
        skipped_duplicates=skipped_duplicates,
        errors=errors,
        bureaux_centraux_created=0,
    )


def import_excel_bureaux_centraux(db: Session, file_bytes: bytes) -> ImportReport:
    workbook = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    ws = find_central_sheet(workbook)
    return import_central_worksheet(db, ws)
