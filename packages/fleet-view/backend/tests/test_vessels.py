from fastapi.testclient import TestClient

from fleet_backend.main import app

client = TestClient(app)


def test_list_vessels_returns_five():
    resp = client.get("/api/v1/vessels")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5


def test_list_vessels_has_required_fields():
    resp = client.get("/api/v1/vessels")
    vessel = resp.json()[0]
    assert "id" in vessel
    assert "name" in vessel
    assert "type" in vessel
    assert "flag" in vessel
    assert "latitude" in vessel
    assert "longitude" in vessel
    assert "status" in vessel


def test_get_vessel_by_id():
    resp = client.get("/api/v1/vessels/V-001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "MV Pacific Star"
    assert data["flag"] == "KR"


def test_get_vessel_not_found():
    resp = client.get("/api/v1/vessels/NONEXISTENT")
    assert resp.status_code == 404


def test_get_vessel_inspections():
    resp = client.get("/api/v1/vessels/V-001/inspections")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    assert all(i["vessel_id"] == "V-001" for i in data)


def test_get_vessel_inspections_not_found():
    resp = client.get("/api/v1/vessels/NONEXISTENT/inspections")
    assert resp.status_code == 404


def test_get_detections_for_inspection():
    resp = client.get("/api/v1/vessels/V-001/inspections/INS-001/detections")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    psc_codes = {d["psc_code"] for d in data}
    assert "0615" in psc_codes
    assert "0630" in psc_codes


def test_get_detections_not_found():
    resp = client.get("/api/v1/vessels/V-001/inspections/NONEXISTENT/detections")
    assert resp.status_code == 404
