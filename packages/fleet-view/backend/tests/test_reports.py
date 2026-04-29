from fastapi.testclient import TestClient

from fleet_backend.main import app

client = TestClient(app)


def test_generate_psc_readiness_report():
    resp = client.post("/api/v1/reports/generate", json={
        "vessel_id": "V-001",
        "report_type": "psc_readiness",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["report_type"] == "psc_readiness"
    assert data["vessel_id"] == "V-001"
    assert data["status"] == "generated"
    assert "RPT-" in data["id"]


def test_generate_class_survey_report():
    resp = client.post("/api/v1/reports/generate", json={
        "vessel_id": "V-002",
        "report_type": "class_survey",
    })
    assert resp.status_code == 200
    assert resp.json()["report_type"] == "class_survey"


def test_generate_security_audit_report():
    resp = client.post("/api/v1/reports/generate", json={
        "vessel_id": "V-003",
        "report_type": "security_audit",
    })
    assert resp.status_code == 200
    assert resp.json()["report_type"] == "security_audit"


def test_generate_cic_compliance_report():
    resp = client.post("/api/v1/reports/generate", json={
        "vessel_id": "V-004",
        "report_type": "cic_compliance",
    })
    assert resp.status_code == 200
    assert resp.json()["report_type"] == "cic_compliance"


def test_generate_report_invalid_vessel():
    resp = client.post("/api/v1/reports/generate", json={
        "vessel_id": "NONEXISTENT",
        "report_type": "psc_readiness",
    })
    assert resp.status_code == 400


def test_generate_report_invalid_type():
    resp = client.post("/api/v1/reports/generate", json={
        "vessel_id": "V-001",
        "report_type": "nonexistent_type",
    })
    assert resp.status_code == 400


def test_get_report_by_id():
    create_resp = client.post("/api/v1/reports/generate", json={
        "vessel_id": "V-001",
        "report_type": "psc_readiness",
    })
    report_id = create_resp.json()["id"]

    resp = client.get(f"/api/v1/reports/{report_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == report_id


def test_get_report_not_found():
    resp = client.get("/api/v1/reports/RPT-nonexistent")
    assert resp.status_code == 404
