from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "Bureaux_Centraux.xlsx"


def test_import_bureaux_centraux_success(client):
    with open(FIXTURE, "rb") as f:
        response = client.post(
            "/api/bureaux-centraux/import",
            files={"file": ("Bureaux_Centraux.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    assert response.status_code == 200
    report = response.json()
    # 5 data rows: row1 ok, row2 ok, row3 ok, row4 duplicate of row1, row5 missing numero -> error
    assert report["total_rows"] == 5
    assert report["created"] == 3
    assert report["updated"] == 0
    assert report["skipped_duplicates"] == 1
    assert len(report["errors"]) == 1

    listing = client.get("/api/bureaux-centraux?page_size=10").json()
    assert listing["total"] == 3

    full = next(b for b in listing["items"] if b["numero_bureau_central"] == "1")
    assert full["president_bureau_central"] == "عبد الحق بلعابد"
    assert full["adresse_bureau_central"] == "المدرسة المركزية"
    assert full["vice_president_bureau_central"] == "نائب الرئيس"
    assert full["membre_central_1"] == "عضو أ"
    assert full["suppleant_central_3"] == "نائب ج"
    assert full["president_cin"] == "P1"
    assert full["suppleant_central_3_cin"] == "P8"

    partial = next(b for b in listing["items"] if b["numero_bureau_central"] == "8")
    assert partial["president_bureau_central"] == "الحبيب العسري"
    assert partial["adresse_bureau_central"] is None


def test_import_bureaux_centraux_upsert_does_not_erase_existing_optional_fields(client):
    with open(FIXTURE, "rb") as f:
        client.post("/api/bureaux-centraux/import", files={"file": ("f.xlsx", f, "application/octet-stream")})

    # Re-import the same file: existing optional fields are already set and
    # the same values are provided again, so nothing should regress.
    with open(FIXTURE, "rb") as f:
        response = client.post("/api/bureaux-centraux/import", files={"file": ("f.xlsx", f, "application/octet-stream")})
    report = response.json()
    assert report["created"] == 0
    assert report["updated"] == 3

    listing = client.get("/api/bureaux-centraux?page_size=10").json()
    full = next(b for b in listing["items"] if b["numero_bureau_central"] == "1")
    assert full["adresse_bureau_central"] == "المدرسة المركزية"


def test_import_bureaux_centraux_generates_document_after_import(client):
    with open(FIXTURE, "rb") as f:
        client.post("/api/bureaux-centraux/import", files={"file": ("f.xlsx", f, "application/octet-stream")})

    listing = client.get("/api/bureaux-centraux?page_size=10").json()
    full = next(b for b in listing["items"] if b["numero_bureau_central"] == "1")

    response = client.get(f"/api/bureaux-centraux/{full['id']}/document?format=docx")
    assert response.status_code == 200
    assert len(response.content) > 1000

    partial = next(b for b in listing["items"] if b["numero_bureau_central"] == "8")
    incomplete_response = client.get(f"/api/bureaux-centraux/{partial['id']}/document?format=docx")
    assert incomplete_response.status_code == 422


def test_import_bureaux_centraux_rejects_non_excel_file(client):
    response = client.post(
        "/api/bureaux-centraux/import",
        files={"file": ("data.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
