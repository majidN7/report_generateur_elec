SAMPLE = {
    "numero_bureau": "1",
    "commune": "الداخلة",
    "adresse_bureau": "المدرسة الابتدائية",
    "president": "أحمد بنعلي",
    "vice_president": "فاطمة العلوي",
    "numero_bureau_central": "1",
    "president_bureau_central": "عبد الحق بلعابد",
    "membre_1": "عضو 1",
    "membre_2": "عضو 2",
    "membre_3": "عضو 3",
    "suppleant_1": "نائب 1",
    "suppleant_2": "نائب 2",
    "suppleant_3": "نائب 3",
}


def test_create_get_update_delete_bureau(client):
    create_resp = client.post("/api/bureaux", json=SAMPLE)
    assert create_resp.status_code == 201
    bureau = create_resp.json()
    bureau_id = bureau["id"]

    get_resp = client.get(f"/api/bureaux/{bureau_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["president"] == "أحمد بنعلي"

    update_resp = client.put(f"/api/bureaux/{bureau_id}", json={"president": "رئيس جديد"})
    assert update_resp.status_code == 200
    assert update_resp.json()["president"] == "رئيس جديد"

    delete_resp = client.delete(f"/api/bureaux/{bureau_id}")
    assert delete_resp.status_code == 204

    assert client.get(f"/api/bureaux/{bureau_id}").status_code == 404


def test_duplicate_numero_bureau_rejected(client):
    assert client.post("/api/bureaux", json=SAMPLE).status_code == 201
    dup = client.post("/api/bureaux", json=SAMPLE)
    assert dup.status_code == 409


def test_missing_required_field_rejected(client):
    payload = dict(SAMPLE)
    del payload["president"]
    response = client.post("/api/bureaux", json=payload)
    assert response.status_code == 422


def test_list_pagination_and_search(client):
    for i in range(1, 6):
        payload = dict(SAMPLE, numero_bureau=str(i))
        client.post("/api/bureaux", json=payload)

    page1 = client.get("/api/bureaux?page=1&page_size=2").json()
    assert page1["total"] == 5
    assert len(page1["items"]) == 2

    search = client.get("/api/bureaux?search=بنعلي").json()
    assert search["total"] == 5


def test_delete_all_bureaux(client):
    for i in range(1, 4):
        client.post("/api/bureaux", json=dict(SAMPLE, numero_bureau=str(i)))

    response = client.delete("/api/bureaux/all")
    assert response.status_code == 200
    assert response.json()["deleted"] == 3

    listing = client.get("/api/bureaux").json()
    assert listing["total"] == 0


def test_delete_all_bureaux_when_empty(client):
    response = client.delete("/api/bureaux/all")
    assert response.status_code == 200
    assert response.json()["deleted"] == 0


def test_numero_decision_cannot_be_set_via_api(client):
    """قرار عاملي رقم .........../2026 must stay a static, non-fillable
    header: the API silently ignores any numero_decision sent in the
    payload (it is not part of the schema)."""
    payload = dict(SAMPLE, numero_decision="1234")
    create_resp = client.post("/api/bureaux", json=payload)
    assert create_resp.status_code == 201
    assert "numero_decision" not in create_resp.json()

    bureau_id = create_resp.json()["id"]
    update_resp = client.put(f"/api/bureaux/{bureau_id}", json={"numero_decision": "5678"})
    assert update_resp.status_code == 200
    assert "numero_decision" not in update_resp.json()
