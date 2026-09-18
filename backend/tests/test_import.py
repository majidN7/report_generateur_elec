from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "Base_Fusion_Bureaux_Vote.xlsx"


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
