import shutil
import zipfile
from io import BytesIO

import pytest

from tests.test_bureaux_crud import SAMPLE

SOFFICE_AVAILABLE = shutil.which("soffice") is not None


def test_generate_bureau_docx(client):
    bureau_id = client.post("/api/bureaux", json=SAMPLE).json()["id"]
    response = client.get(f"/api/bureaux/{bureau_id}/document?format=docx")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/vnd.openxmlformats")
    assert len(response.content) > 1000


@pytest.mark.skipif(not SOFFICE_AVAILABLE, reason="LibreOffice n'est pas installé")
def test_generate_bureau_pdf(client):
    bureau_id = client.post("/api/bureaux", json=SAMPLE).json()["id"]
    response = client.get(f"/api/bureaux/{bureau_id}/document?format=pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


def test_generate_batch_zip(client):
    for i in range(1, 4):
        client.post("/api/bureaux", json=dict(SAMPLE, numero_bureau=str(i)))

    response = client.post("/api/bureaux/generate-batch?format=docx")
    assert response.status_code == 200
    zf = zipfile.ZipFile(BytesIO(response.content))
    assert len(zf.namelist()) == 3


def test_bureau_central_document_requires_complete_data(client):
    central = client.post(
        "/api/bureaux-centraux",
        json={
            "numero_bureau_central": "1",
            "commune": "الداخلة",
            "president_bureau_central": "عبد الحق بلعابد",
        },
    ).json()

    incomplete = client.get(f"/api/bureaux-centraux/{central['id']}/document?format=docx")
    assert incomplete.status_code == 422

    complete_payload = {
        "adresse_bureau_central": "مقر المكتب المركزي",
        "vice_president_bureau_central": "نائب الرئيس",
        "membre_central_1": "عضو 1",
        "membre_central_2": "عضو 2",
        "membre_central_3": "عضو 3",
        "suppleant_central_1": "نائب 1",
        "suppleant_central_2": "نائب 2",
        "suppleant_central_3": "نائب 3",
    }
    client.put(f"/api/bureaux-centraux/{central['id']}", json=complete_payload)

    complete = client.get(f"/api/bureaux-centraux/{central['id']}/document?format=docx")
    assert complete.status_code == 200
    assert len(complete.content) > 1000
