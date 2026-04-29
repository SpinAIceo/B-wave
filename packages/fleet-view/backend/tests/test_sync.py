from fastapi.testclient import TestClient

from fleet_backend.main import app

client = TestClient(app)


def test_sync_receive_basic():
    resp = client.post("/api/v1/sync/receive", json={
        "vessel_id": "V-001",
        "edge_server_id": "EDGE-001",
        "inspection_id": "INS-NEW-001",
        "inspector_id": "CREW-101",
        "port_of_inspection": "Busan",
        "mou_region": "TOKYO",
        "detections": [],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["records_received"] == 1


def test_sync_receive_with_detections():
    resp = client.post("/api/v1/sync/receive", json={
        "vessel_id": "V-002",
        "edge_server_id": "EDGE-002",
        "inspection_id": "INS-NEW-002",
        "detections": [
            {
                "id": "DET-SYNC-001",
                "defect_type": "RUST",
                "confidence": 0.85,
                "psc_code": "0615",
                "severity": "HIGH",
                "bbox": {"x_min": 0.1, "y_min": 0.2, "x_max": 0.3, "y_max": 0.4},
            }
        ],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["records_received"] == 2
    assert data["status"] == "SUCCESS"


def test_sync_receive_missing_fields():
    resp = client.post("/api/v1/sync/receive", json={
        "vessel_id": "",
        "edge_server_id": "",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "FAILED"


def test_sync_conflict_resolution():
    client.post("/api/v1/sync/receive", json={
        "vessel_id": "V-003",
        "edge_server_id": "EDGE-003",
        "inspection_id": "INS-004",
        "port_of_inspection": "Singapore Updated",
        "timestamp": "2099-01-01T00:00:00",
    })
    resp = client.get("/api/v1/vessels/V-003/inspections")
    data = resp.json()
    ins = [i for i in data if i["id"] == "INS-004"]
    assert len(ins) == 1
    assert ins[0]["synced"] is True
