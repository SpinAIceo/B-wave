from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.logger import get_logger

# SQLite exception → 한국어/영어 원인 분류
_SQLITE_ERR_LABELS: dict[type, tuple[str, str]] = {
    sqlite3.OperationalError:  ("DB 연결/잠금 오류", "connection/lock error"),
    sqlite3.IntegrityError:    ("제약 조건 위반", "constraint violation"),
    sqlite3.DatabaseError:     ("DB 파일 손상 가능", "database corruption possible"),
    sqlite3.ProgrammingError:  ("SQL 쿼리 오류", "SQL programming error"),
    sqlite3.InterfaceError:    ("DB 인터페이스 오류", "interface error"),
}


def _classify_exc(exc: Exception) -> str:
    for exc_type, (ko, en) in _SQLITE_ERR_LABELS.items():
        if isinstance(exc, exc_type):
            return f"{type(exc).__name__} | KO: {ko} / EN: {en}"
    return f"{type(exc).__name__} | 알 수 없는 DB 오류 / unknown DB error"

log = get_logger("bwave.db")

DB_PATH = Path("/tmp/bwave.db")


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


VALID_ZONES = ("bow", "midship", "stern", "deck", "hull", "engine_room")
DEFAULT_ZONE = "midship"


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
                image_height INTEGER,
                zone        TEXT NOT NULL DEFAULT 'midship'
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
            CREATE INDEX IF NOT EXISTS idx_scans_zone ON scans(zone);
            CREATE INDEX IF NOT EXISTS idx_detections_scan ON detections(scan_id);
        """)
        # Idempotent migration for existing DBs (sqlite ALTER TABLE limitation).
        cols = [r[1] for r in conn.execute("PRAGMA table_info(scans)").fetchall()]
        if "zone" not in cols:
            conn.execute(
                "ALTER TABLE scans ADD COLUMN zone TEXT NOT NULL DEFAULT 'midship'"
            )
            log.info("migrated: scans.zone column added")
    log.info("DB schema ready (indexes: vessel_id, zone, scan_id)")


def save_scan(vessel_id: str, filename: str, result, zone: str = DEFAULT_ZONE) -> str:
    scan_id = "S" + str(uuid.uuid4())[:7].upper()
    now = datetime.now(timezone.utc).isoformat()
    if zone not in VALID_ZONES:
        log.warning(f"save_scan invalid zone='{zone}', falling back to '{DEFAULT_ZONE}'")
        zone = DEFAULT_ZONE
    log.info(f"save_scan scan={scan_id} vessel={vessel_id} zone={zone} file={filename} detections={len(result.detections)}")
    try:
        with _conn() as conn:
            conn.execute(
                "INSERT INTO scans VALUES (?,?,?,?,?,?,?,?,?)",
                (scan_id, vessel_id, now, filename,
                 result.inference_ms, result.model_version,
                 result.image_width, result.image_height, zone),
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
        log.error(f"save_scan FAILED scan={scan_id} {_classify_exc(exc)} detail={exc!r}")
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
        result = [dict(r) for r in rows]
        log.debug(f"get_scans op=SELECT vessel={vessel_id or 'all'} rows={len(result)}")
        return result
    except Exception as exc:
        log.error(f"get_scans FAILED op=SELECT vessel={vessel_id} {_classify_exc(exc)} detail={exc!r}")
        raise


def get_detections(scan_id: str) -> list[dict]:
    try:
        with _conn() as conn:
            rows = conn.execute(
                "SELECT * FROM detections WHERE scan_id=?", (scan_id,)
            ).fetchall()
        result = [dict(r) for r in rows]
        log.debug(f"get_detections op=SELECT scan={scan_id} rows={len(result)}")
        return result
    except Exception as exc:
        log.error(f"get_detections FAILED op=SELECT scan={scan_id} {_classify_exc(exc)} detail={exc!r}")
        raise


def defect_stats() -> dict[str, int]:
    try:
        with _conn() as conn:
            rows = conn.execute(
                "SELECT class_name, COUNT(*) cnt FROM detections GROUP BY class_name"
            ).fetchall()
        result = {r["class_name"]: r["cnt"] for r in rows}
        log.debug(f"defect_stats op=AGGREGATE rows={len(result)} result={result}")
        return result
    except Exception as exc:
        log.error(f"defect_stats FAILED op=AGGREGATE {_classify_exc(exc)} detail={exc!r}")
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
        log.debug(f"vessel_stats op=JOIN_AGGREGATE vessels={list(result.keys())}")
        return result
    except Exception as exc:
        log.error(f"vessel_stats FAILED op=JOIN_AGGREGATE {_classify_exc(exc)} detail={exc!r}")
        raise
