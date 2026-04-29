use anyhow::Result;
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use tracing::{debug, info};

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[repr(i32)]
pub enum SyncPriority {
    Critical = 0,
    High = 1,
    Normal = 2,
    Low = 3,
}

impl SyncPriority {
    fn from_i32(v: i32) -> Self {
        match v {
            0 => Self::Critical,
            1 => Self::High,
            2 => Self::Normal,
            _ => Self::Low,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncQueueItem {
    pub record_id: String,
    pub record_type: String,
    pub priority: SyncPriority,
    pub created_at: String,
    pub retry_count: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncStats {
    pub pending_count: i64,
    pub synced_count: i64,
    pub failed_count: i64,
    pub last_sync_timestamp: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InspectionRecord {
    pub id: String,
    pub vessel_id: String,
    pub inspector_id: String,
    pub port_of_inspection: String,
    pub mou_region: String,
    pub started_at: String,
    pub completed_at: Option<String>,
    pub summary_json: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DetectionRecord {
    pub id: String,
    pub inspection_id: String,
    pub defect_type: String,
    pub confidence: f32,
    pub bbox_json: String,
    pub psc_code: Option<String>,
    pub severity: String,
    pub model_version: String,
    pub inference_time_ms: f32,
    pub timestamp: String,
}

pub struct SyncManager {
    conn: Connection,
}

impl SyncManager {
    pub fn new(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)?;
        conn.execute_batch("PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;")?;
        let mgr = Self { conn };
        mgr.init_db()?;
        Ok(mgr)
    }

    pub fn new_in_memory() -> Result<Self> {
        let conn = Connection::open_in_memory()?;
        conn.execute_batch("PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;")?;
        let mgr = Self { conn };
        mgr.init_db()?;
        Ok(mgr)
    }

    fn init_db(&self) -> Result<()> {
        self.conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS inspections (
                id TEXT PRIMARY KEY,
                vessel_id TEXT NOT NULL,
                inspector_id TEXT NOT NULL,
                port_of_inspection TEXT NOT NULL,
                mou_region TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                summary_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS detections (
                id TEXT PRIMARY KEY,
                inspection_id TEXT NOT NULL,
                defect_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                bbox_json TEXT NOT NULL,
                psc_code TEXT,
                severity TEXT NOT NULL,
                model_version TEXT NOT NULL,
                inference_time_ms REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (inspection_id) REFERENCES inspections(id)
            );

            CREATE TABLE IF NOT EXISTS sync_queue (
                record_id TEXT PRIMARY KEY,
                record_type TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 2,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                synced_at TEXT,
                retry_count INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_sync_queue_priority
                ON sync_queue(priority, created_at)
                WHERE status = 'pending';",
        )?;
        info!("SyncManager database initialized");
        Ok(())
    }

    pub fn store_inspection(&self, record: &InspectionRecord) -> Result<()> {
        self.conn.execute(
            "INSERT OR REPLACE INTO inspections
             (id, vessel_id, inspector_id, port_of_inspection, mou_region,
              started_at, completed_at, summary_json)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![
                record.id,
                record.vessel_id,
                record.inspector_id,
                record.port_of_inspection,
                record.mou_region,
                record.started_at,
                record.completed_at,
                record.summary_json,
            ],
        )?;
        debug!(id = %record.id, "Stored inspection record");
        Ok(())
    }

    pub fn store_detection(&self, detection: &DetectionRecord) -> Result<()> {
        self.conn.execute(
            "INSERT OR REPLACE INTO detections
             (id, inspection_id, defect_type, confidence, bbox_json, psc_code,
              severity, model_version, inference_time_ms, timestamp)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)",
            params![
                detection.id,
                detection.inspection_id,
                detection.defect_type,
                detection.confidence,
                detection.bbox_json,
                detection.psc_code,
                detection.severity,
                detection.model_version,
                detection.inference_time_ms,
                detection.timestamp,
            ],
        )?;
        debug!(id = %detection.id, "Stored detection record");
        Ok(())
    }

    pub fn queue_for_sync(
        &self,
        record_id: &str,
        record_type: &str,
        priority: SyncPriority,
    ) -> Result<()> {
        let now = chrono::Utc::now().to_rfc3339();
        self.conn.execute(
            "INSERT OR REPLACE INTO sync_queue (record_id, record_type, priority, status, created_at)
             VALUES (?1, ?2, ?3, 'pending', ?4)",
            params![record_id, record_type, priority as i32, now],
        )?;
        debug!(record_id, "Queued for sync");
        Ok(())
    }

    pub fn get_pending_sync(&self) -> Result<Vec<SyncQueueItem>> {
        let mut stmt = self.conn.prepare(
            "SELECT record_id, record_type, priority, created_at, retry_count
             FROM sync_queue WHERE status = 'pending'
             ORDER BY priority ASC, created_at ASC",
        )?;
        let items = stmt
            .query_map([], |row| {
                Ok(SyncQueueItem {
                    record_id: row.get(0)?,
                    record_type: row.get(1)?,
                    priority: SyncPriority::from_i32(row.get(2)?),
                    created_at: row.get(3)?,
                    retry_count: row.get(4)?,
                })
            })?
            .collect::<std::result::Result<Vec<_>, _>>()?;
        Ok(items)
    }

    pub fn mark_synced(&self, record_id: &str) -> Result<()> {
        let now = chrono::Utc::now().to_rfc3339();
        self.conn.execute(
            "UPDATE sync_queue SET status = 'synced', synced_at = ?1 WHERE record_id = ?2",
            params![now, record_id],
        )?;
        debug!(record_id, "Marked as synced");
        Ok(())
    }

    pub fn get_sync_stats(&self) -> Result<SyncStats> {
        let pending_count: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM sync_queue WHERE status = 'pending'",
            [],
            |r| r.get(0),
        )?;
        let synced_count: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM sync_queue WHERE status = 'synced'",
            [],
            |r| r.get(0),
        )?;
        let failed_count: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM sync_queue WHERE status = 'failed'",
            [],
            |r| r.get(0),
        )?;
        let last_sync_timestamp: Option<String> = self.conn.query_row(
            "SELECT MAX(synced_at) FROM sync_queue WHERE status = 'synced'",
            [],
            |r| r.get(0),
        )?;

        Ok(SyncStats {
            pending_count,
            synced_count,
            failed_count,
            last_sync_timestamp,
        })
    }

    pub fn get_inspection(&self, id: &str) -> Result<Option<InspectionRecord>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, vessel_id, inspector_id, port_of_inspection, mou_region,
                    started_at, completed_at, summary_json
             FROM inspections WHERE id = ?1",
        )?;
        let mut rows = stmt.query_map(params![id], |row| {
            Ok(InspectionRecord {
                id: row.get(0)?,
                vessel_id: row.get(1)?,
                inspector_id: row.get(2)?,
                port_of_inspection: row.get(3)?,
                mou_region: row.get(4)?,
                started_at: row.get(5)?,
                completed_at: row.get(6)?,
                summary_json: row.get(7)?,
            })
        })?;
        match rows.next() {
            Some(Ok(record)) => Ok(Some(record)),
            Some(Err(e)) => Err(e.into()),
            None => Ok(None),
        }
    }
}
