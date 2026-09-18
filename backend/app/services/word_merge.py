"""Génération des arrêtés Word (et PDF) à partir des templates docxtpl."""

import io
import re
import subprocess
import tempfile
import zipfile
from datetime import date
from pathlib import Path

from docxtpl import DocxTemplate

from app.models.bureau_central import BureauCentral
from app.models.bureau_vote import BureauVote

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates_word"
TEMPLATE_ORDINAIRE = TEMPLATES_DIR / "bureau_ordinaire.docx"
TEMPLATE_CENTRAL = TEMPLATES_DIR / "bureau_central.docx"

ARABIC_MONTHS = {
    1: "يناير",
    2: "فبراير",
    3: "مارس",
    4: "أبريل",
    5: "ماي",
    6: "يونيو",
    7: "يوليوز",
    8: "غشت",
    9: "شتنبر",
    10: "أكتوبر",
    11: "نونبر",
    12: "دجنبر",
}


def default_date_signature() -> str:
    today = date.today()
    return f"{today.day} {ARABIC_MONTHS[today.month]} {today.year}"


def sanitize_filename(value: str) -> str:
    value = re.sub(r"[^\w\-. ]+", "_", value, flags=re.UNICODE)
    return value.strip().replace(" ", "_")


class MissingFieldsError(ValueError):
    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__(f"Champs obligatoires manquants pour générer le document : {', '.join(missing)}")


def _render_docx(template_path: Path, context: dict) -> bytes:
    tpl = DocxTemplate(str(template_path))
    tpl.render(context)
    buf = io.BytesIO()
    tpl.save(buf)
    return buf.getvalue()


def bureau_vote_context(bureau: BureauVote) -> dict:
    return {
        "numero_decision": bureau.numero_decision or str(bureau.id),
        "date_signature": bureau.date_signature or default_date_signature(),
        "president": bureau.president,
        "numero_bureau": bureau.numero_bureau,
        "commune": bureau.commune,
        "adresse_bureau": bureau.adresse_bureau,
        "numero_bureau_central": bureau.numero_bureau_central,
        "president_bureau_central": bureau.president_bureau_central,
        "adresse_bureau_central": bureau.adresse_bureau_central or bureau.adresse_bureau,
        "vice_president": bureau.vice_president,
        "membre_1": bureau.membre_1,
        "membre_2": bureau.membre_2,
        "membre_3": bureau.membre_3,
        "suppleant_1": bureau.suppleant_1,
        "suppleant_2": bureau.suppleant_2,
        "suppleant_3": bureau.suppleant_3,
    }


def render_bureau_vote_docx(bureau: BureauVote) -> bytes:
    return _render_docx(TEMPLATE_ORDINAIRE, bureau_vote_context(bureau))


def bureau_vote_filename(bureau: BureauVote, ext: str) -> str:
    return sanitize_filename(f"arrete_bureau_{bureau.commune}_{bureau.numero_bureau}") + f".{ext}"


REQUIRED_CENTRAL_FIELDS = {
    "adresse_bureau_central": "Adresse du bureau central",
    "vice_president_bureau_central": "Vice-président du bureau central",
    "membre_central_1": "Membre 1",
    "membre_central_2": "Membre 2",
    "membre_central_3": "Membre 3",
    "suppleant_central_1": "Suppléant 1",
    "suppleant_central_2": "Suppléant 2",
    "suppleant_central_3": "Suppléant 3",
}


def bureau_central_context(bureau: BureauCentral) -> dict:
    missing = [label for field, label in REQUIRED_CENTRAL_FIELDS.items() if not getattr(bureau, field)]
    if missing:
        raise MissingFieldsError(missing)

    return {
        "numero_decision": bureau.numero_decision or str(bureau.id),
        "date_signature": bureau.date_signature or default_date_signature(),
        "president_bureau_central": bureau.president_bureau_central,
        "numero_bureau_central": bureau.numero_bureau_central,
        "commune": bureau.commune,
        "adresse_bureau_central": bureau.adresse_bureau_central,
        "vice_president_bureau_central": bureau.vice_president_bureau_central,
        "membre_central_1": bureau.membre_central_1,
        "membre_central_2": bureau.membre_central_2,
        "membre_central_3": bureau.membre_central_3,
        "suppleant_central_1": bureau.suppleant_central_1,
        "suppleant_central_2": bureau.suppleant_central_2,
        "suppleant_central_3": bureau.suppleant_central_3,
    }


def render_bureau_central_docx(bureau: BureauCentral) -> bytes:
    return _render_docx(TEMPLATE_CENTRAL, bureau_central_context(bureau))


def bureau_central_filename(bureau: BureauCentral, ext: str) -> str:
    return sanitize_filename(f"arrete_bureau_central_{bureau.commune}_{bureau.numero_bureau_central}") + f".{ext}"


def convert_docx_to_pdf(docx_bytes: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        docx_path = tmp_path / "input.docx"
        docx_path.write_bytes(docx_bytes)
        profile_dir = tmp_path / "lo_profile"
        result = subprocess.run(
            [
                "soffice",
                "--headless",
                "--norestore",
                f"-env:UserInstallation=file://{profile_dir}",
                "--convert-to",
                "pdf",
                "--outdir",
                str(tmp_path),
                str(docx_path),
            ],
            capture_output=True,
            timeout=60,
        )
        pdf_path = tmp_path / "input.pdf"
        if result.returncode != 0 or not pdf_path.exists():
            raise RuntimeError(
                "Échec de la conversion PDF (LibreOffice). "
                f"stdout={result.stdout.decode(errors='ignore')} stderr={result.stderr.decode(errors='ignore')}"
            )
        return pdf_path.read_bytes()


def build_zip(files: list[tuple[str, bytes]]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        used_names: set[str] = set()
        for name, data in files:
            final_name = name
            counter = 1
            while final_name in used_names:
                stem, dot, ext = name.rpartition(".")
                final_name = f"{stem}_{counter}.{ext}" if dot else f"{name}_{counter}"
                counter += 1
            used_names.add(final_name)
            zf.writestr(final_name, data)
    return buf.getvalue()
