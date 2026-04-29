#!/usr/bin/env python3
"""B-Wave OTA Update Server.

Serves firmware/software updates to vessel edge servers over satellite link.
Runs on the shore server. Designed for bandwidth-constrained environments.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="B-Wave OTA Update Server", version="0.1.0")

UPDATES_DIR = Path(os.getenv("BWAVE_OTA_UPDATES_DIR", "/opt/bwave/ota/updates"))


class UpdateInfo(BaseModel):
    update_id: str
    version: str
    current_version: str
    size_bytes: int
    sha256: str
    changelog: str
    is_critical: bool
    released_at: str


class UpdateReport(BaseModel):
    vessel_id: str
    edge_server_id: str
    update_id: str
    status: str  # SUCCESS, FAILED, ROLLED_BACK
    error_message: str = ""
    applied_at: str = ""


# In-memory registry of available updates and reports
_updates: dict[str, dict] = {
    "update-0.2.0": {
        "update_id": "update-0.2.0",
        "version": "0.2.0",
        "min_version": "0.1.0",
        "size_bytes": 52_428_800,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "changelog": "Improved cargo securing detection accuracy, added CIC 2026 rules update",
        "is_critical": False,
        "released_at": "2026-05-01T00:00:00Z",
    },
}
_reports: list[dict] = []


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ota-server"}


@app.get("/api/v1/updates/check")
async def check_update(
    vessel_id: str = Query(...),
    current_version: str = Query(...),
):
    available = []
    for uid, info in _updates.items():
        if info["min_version"] <= current_version < info["version"]:
            available.append(
                UpdateInfo(
                    update_id=uid,
                    version=info["version"],
                    current_version=current_version,
                    size_bytes=info["size_bytes"],
                    sha256=info["sha256"],
                    changelog=info["changelog"],
                    is_critical=info["is_critical"],
                    released_at=info["released_at"],
                )
            )

    return {
        "vessel_id": vessel_id,
        "current_version": current_version,
        "updates_available": len(available),
        "updates": [u.model_dump() for u in available],
    }


@app.get("/api/v1/updates/download/{update_id}")
async def download_update(update_id: str):
    if update_id not in _updates:
        raise HTTPException(status_code=404, detail="Update not found")

    pkg_path = UPDATES_DIR / f"{update_id}.tar.gz"
    if not pkg_path.exists():
        return {
            "update_id": update_id,
            "status": "package_not_built",
            "message": "Run create-update.sh to build the package",
            "expected_path": str(pkg_path),
        }

    return {
        "update_id": update_id,
        "download_url": f"/static/updates/{update_id}.tar.gz",
        "sha256": _updates[update_id]["sha256"],
        "size_bytes": _updates[update_id]["size_bytes"],
    }


@app.post("/api/v1/updates/report")
async def report_update(report: UpdateReport):
    entry = report.model_dump()
    entry["received_at"] = datetime.now(timezone.utc).isoformat()
    _reports.append(entry)
    return {"status": "recorded", "report_id": len(_reports)}


@app.get("/api/v1/updates/reports")
async def list_reports(vessel_id: str | None = None):
    if vessel_id:
        filtered = [r for r in _reports if r["vessel_id"] == vessel_id]
    else:
        filtered = _reports
    return {"total": len(filtered), "reports": filtered}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8090)
