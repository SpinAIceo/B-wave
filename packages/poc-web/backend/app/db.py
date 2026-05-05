from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.logger import get_logger

log = get_logger("bwave.db")

DB_PATH = Path("/tmp/bwave.db")


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    log.info(f"init DB at {DB_PATH}")
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS scans (
                id          TEXT PRIMARY KEY,
                vessel_id   TEXT NOT NULL,
                scanned_at  TEXT NOT NULL,
                filename    TEXT,
                inference_ms REAL,
                model_version TEXT,
                image_width  INTEGER,
                image_height INTEGER
            );
            CREATE TABLE IF NOT EXISTS detections (
                id          TEXT PRIMARY KEY,
                scan_id     TEXT NOT NULL,
                class_name  TEXT,
                confidence  REAL,
                psc_code    TEXT,
                psc_description TEXT,
                severity    TEXT,
                x_min REAL, y_min REAL, x_max REAL, y_max REAL
            );
            CREATE INDEX IF NOT EXISTS idx_scans_vessel ON scans(vessel_id);
            CREATE INDEX IF NOT EXISTS idx_detections_scan ON detections(scan_id);
        """)
    log.info("DB schema ready (indexes: vessel_id, scan_id)")


def save_scan(vessel_id: str, filename: str, result) -> str:
    scan_id = "S" + str(uuid.uuid4())[:7].upper()
    now = datetime.now(timezone.utc).isoformat()
    log.info(f"save_scan scan={scan_id} vessel={vessel_id} file={filename} detections={len(result.detections)}")
    try:
        with _conn() as conn:
            conn.execute(
                "INSERT INTO scans VALUES (?,?,?,?,?,?,?,?)",
                (scan_id, vessel_id, now, filename,
                 result.inference_ms, result.model_version,
                 result.image_width, result.image_height),
            )
            for det in result.detections:
                conn.execute(
                    "INSERT INTO detections VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (str(uuid.uuid4())[:8], scan_id,
                     det.class_name, det.confidence,
                     det.psc_code, det.psc_description, det.severity,
                     det.x_min, det.y_min, det.x_max, det.y_max),
                )
        log.debug(f"save_scan committed scan={scan_id}")
    except Exception as exc:
        log.error(f"save_scan FAILED scan={scan_id}: {exc!r}")
        raise
    return scan_id


def get_scans(vessel_id: str | None = None) -> list[dict]:
    try:
        with _conn() as conn:
            if vessel_id:
                rows = conn.execute(
                    "SELECT * FROM scans WHERE vessel_id=? ORDER BY scanned_at DESC",
                    (vessel_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM scans ORDER BY scanned_at DESC"
                ).fetchall()
        log.debug(f"get_scans vessel={vessel_id or 'all'} count={len(rows)}")
        return [dict(r) for r in rows]
    except Exception as exc:
        log.error(f"get_scans FAILED: {exc!r}")
        raise


def get_detections(scan_id: str) -> list[dict]:
    try:
        with _conn() as conn:
            rows = conn.execute(
                "SELECT * FROM detections WHERE scan_id=?", (scan_id,)
            ).fetchall()
        log.debug(f"get_detections scan={scan_id} count={len(rows)}")
        return [dict(r) for r in rows]
    except Exception as exc:
        log.error(f"get_detections FAILED scan={scan_id}: {exc!r}")
        raise


def defect_stats() -> dict[str, int]:
    try:
        with _conn() as conn:
            rows = conn.execute(
                "SELECT class_name, COUNT(*) cnt FROM detections GROUP BY class_name"
            ).fetchall()
        result = {r["class_name"]: r["cnt"] for r in rows}
        log.debug(f"defect_stats {result}")
        return result
    except Exception as exc:
        log.error(f"defect_stats FAILED: {exc!r}")
        raise


def vessel_stats() -> dict[str, dict]:
    try:
        with _conn() as conn:
            rows = conn.execute("""
                SELECT s.vessel_id,
                       COUNT(DISTINCT s.id)                                          AS scan_count,
                       SUM(CASE WHEN d.severity IN ('HIGH','CRITICAL') THEN 1 ELSE 0 END) AS critical_defects,
                       MAX(s.scanned_at)                                             AS last_inspection
                FROM scans s
                LEFT JOIN detections d ON d.scan_id = s.id
                GROUP BY s.vessel_id
            """).fetchall()
        result = {r["vessel_id"]: dict(r) for r in rows}
        log.debug(f"vessel_stats vessels={list(result.keys())}")
        return result
    except Exception as exc:
        log.error(f"vessel_stats FAILED: {exc!r}")
        raise
