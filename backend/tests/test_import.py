from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "Base_Fusion_Bureaux_Vote.xlsx"
DUAL_FORMAT_FIXTURE = Path(__file__).parent / "fixtures" / "Base_Fusion_Bureaux_Vote_BV.xlsx"


def test_import_excel_success(client):
    with open(FIXTURE, "rb") as f:
        response = client.post(
            "/api/import/excel",
            files={"file": ("Base_Fusion_Bureaux_Vote.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    assert response.status_code == 200
    report = response.json()
    assert report["total_rows"] == 51
    assert report["created"] == 50
    assert report["skipped_duplicates"] == 1
    assert report["errors"] == []
    assert report["bureaux_centraux_created"] > 0

    listing = client.get("/api/bureaux?page_size=1").json()
    assert listing["total"] == 50


def test_import_rejects_non_excel_file(client):
    response = client.post(
        "/api/import/excel",
        files={"file": ("data.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_import_is_idempotent_upsert(client):
    with open(FIXTURE, "rb") as f:
        client.post("/api/import/excel", files={"file": ("f.xlsx", f, "application/octet-stream")})
    with open(FIXTURE, "rb") as f:
        response = client.post("/api/import/excel", files={"file": ("f.xlsx", f, "application/octet-stream")})
    report = response.json()
    assert report["created"] == 0
    assert report["updated"] == 50


def test_import_dual_sheet_format_2026(client):
    """Base_Fusion_Bureaux_Vote__BV.xlsx: bureaux ordinaires et bureaux
    centraux dans deux feuilles séparées du même classeur, chacune avec le
    CIN de chaque personne, et sans colonne de rattachement au bureau
    central sur la feuille des bureaux ordinaires."""
    with open(DUAL_FORMAT_FIXTURE, "rb") as f:
        response = client.post(
            "/api/import/excel",
            files={"file": ("Base_Fusion_Bureaux_Vote__BV.xlsx", f, "application/octet-stream")},
        )
    assert response.status_code == 200
    report = response.json()
    # 2 bureaux ordinaires + 1 bureau central = 3 total rows across both sheets
    assert report["total_rows"] == 3
    assert report["created"] == 3
    assert report["errors"] == []
    # the central sheet is imported directly (fully detailed), not stubbed
    # from the vote sheet, which no longer carries the link columns at all
    assert report["bureaux_centraux_created"] == 0

    votes = client.get("/api/bureaux?page_size=10").json()
    assert votes["total"] == 2
    full_vote = next(b for b in votes["items"] if b["numero_bureau"] == "12")
    assert full_vote["president_cin"] == "CIN001"
    assert full_vote["numero_bureau_central"] is None
    assert full_vote["president_bureau_central"] is None

    centraux = client.get("/api/bureaux-centraux?page_size=10").json()
    assert centraux["total"] == 1
    central = centraux["items"][0]
    assert central["president_bureau_central"] == "عبد الحق بلعابد"
    assert central["president_cin"] == "PC1"
    assert central["suppleant_central_3_cin"] == "PC8"

    # generation is blocked for the ordinary bureau: CIN is complete but the
    # central-bureau link is missing, with a clear message naming it
    incomplete = client.get(f"/api/bureaux/{full_vote['id']}/document?format=docx")
    assert incomplete.status_code == 422
    assert "bureau central" in incomplete.json()["detail"]

    # ... but the fully-detailed central bureau generates immediately
    central_doc = client.get(f"/api/bureaux-centraux/{central['id']}/document?format=docx")
    assert central_doc.status_code == 200
    assert len(central_doc.content) > 1000
