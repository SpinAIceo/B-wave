from __future__ import annotations

import logging
import sqlite3
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path

_LOG_DB = Path("/tmp/bwave_errors.db")

# ── Request-ID context variable ───────────────────────────────────────────────
# Set once per HTTP request in the middleware; auto-injected into every log line.
_req_id_var: ContextVar[str] = ContextVar("req_id", default="-")


def set_req_id(req_id: str) -> None:
    _req_id_var.set(req_id)


def get_req_id() -> str:
    return _req_id_var.get()


def _init_error_db() -> None:
    with sqlite3.connect(str(_LOG_DB)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                ts          TEXT NOT NULL,
                level       TEXT NOT NULL,
                req_id      TEXT,
                module      TEXT,
                message     TEXT,
                created_at  TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_el_level  ON error_logs(level)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_el_req_id ON error_logs(req_id)")


def _save_error_log(level: str, req_id: str, module: str, message: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    try:
        with sqlite3.connect(str(_LOG_DB)) as conn:
            conn.execute(
                "INSERT INTO error_logs(ts,level,req_id,module,message,created_at) VALUES(?,?,?,?,?,?)",
                (now, level, req_id, module, message, now),
            )
    except Exception:
        pass  # 로그 저장 실패가 앱을 중단시켜서는 안 됨


class _ReqIdFilter(logging.Filter):
    """Injects request-ID into every LogRecord AND persists WARNING/ERROR to SQLite."""
    def filter(self, record: logging.LogRecord) -> bool:
        req_id = _req_id_var.get()
        record.req_id = req_id
        if record.levelno >= logging.WARNING:
            _save_error_log(record.levelname, req_id, record.name, record.getMessage())
        return True


_error_db_ready = False


def get_logger(name: str) -> logging.Logger:
    global _error_db_ready
    if not _error_db_ready:
        _init_error_db()
        _error_db_ready = True

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s] [%(levelname)-5s] [%(name)s] [%(req_id)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        ))
        handler.addFilter(_ReqIdFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger


# ── Public helpers for error log query ───────────────────────────────────────

def query_error_logs(level: str | None = None, req_id: str | None = None,
                     limit: int = 100) -> list[dict]:
    """Return recent WARNING/ERROR logs from SQLite for the review endpoint."""
    try:
        with sqlite3.connect(str(_LOG_DB)) as conn:
            conn.row_factory = sqlite3.Row
            where, params = [], []
            if level:
                where.append("level = ?"); params.append(level.upper())
            if req_id:
                where.append("req_id = ?"); params.append(req_id)
            sql = "SELECT * FROM error_logs"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY id DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def clear_error_logs() -> int:
    """Delete all error log entries and return deleted count."""
    try:
        with sqlite3.connect(str(_LOG_DB)) as conn:
            n = conn.execute("SELECT COUNT(*) FROM error_logs").fetchone()[0]
            conn.execute("DELETE FROM error_logs")
        return n
    except Exception:
        return 0
