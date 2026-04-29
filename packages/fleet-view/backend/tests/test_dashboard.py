from fastapi.testclient import TestClient

from fleet_backend.main import app

client = TestClient(app)


def test_dashboard_overview_structure():
    resp = client.get("/api/v1/dashboard/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_vessels" in data
    assert "active_inspections" in data
    assert "critical_defects" in data
    assert "detention_risk_score" in data
    assert "vessels_by_status" in data
    assert "defect_type_distribution" in data


def test_dashboard_total_vessels():
    resp = client.get("/api/v1/dashboard/overview")
    data = resp.json()
    assert data["total_vessels"] == 5


def test_dashboard_has_critical_defects():
    resp = client.get("/api/v1/dashboard/overview")
    data = resp.json()
    assert data["critical_defects"] >= 1


def test_dashboard_defect_distribution():
    resp = client.get("/api/v1/dashboard/overview")
    data = resp.json()
    dist = data["defect_type_distribution"]
    assert "RUST" in dist
    assert "CARGO_LASHING" in dist


def test_dashboard_vessels_by_status():
    resp = client.get("/api/v1/dashboard/overview")
    data = resp.json()
    status = data["vessels_by_status"]
    assert sum(status.values()) == 5
