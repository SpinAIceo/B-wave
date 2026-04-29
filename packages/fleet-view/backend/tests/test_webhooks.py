from fastapi.testclient import TestClient

from fleet_backend.main import app

client = TestClient(app)


def test_configure_webhook():
    resp = client.post("/api/v1/webhooks/configure", json={
        "url": "https://erp.example.com/webhook",
        "events": ["defect.critical", "inspection.completed"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "webhook_id" in data
    assert data["status"] == "configured"


def test_configure_webhook_invalid_event():
    resp = client.post("/api/v1/webhooks/configure", json={
        "url": "https://erp.example.com/webhook",
        "events": ["invalid.event"],
    })
    assert resp.status_code == 400


def test_test_webhook():
    create = client.post("/api/v1/webhooks/configure", json={
        "url": "https://test.example.com/hook",
        "events": ["sync.received"],
    })
    webhook_id = create.json()["webhook_id"]

    resp = client.post("/api/v1/webhooks/test", json={
        "webhook_id": webhook_id,
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "delivered"


def test_test_webhook_not_found():
    resp = client.post("/api/v1/webhooks/test", json={
        "webhook_id": "WH-nonexistent",
    })
    assert resp.status_code == 404
