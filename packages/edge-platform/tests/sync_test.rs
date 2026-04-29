use bwave_edge_platform::sync_manager::{
    DetectionRecord, InspectionRecord, SyncManager, SyncPriority,
};

fn make_manager() -> SyncManager {
    SyncManager::new_in_memory().expect("Failed to create in-memory SyncManager")
}

fn sample_inspection() -> InspectionRecord {
    InspectionRecord {
        id: "insp-001".into(),
        vessel_id: "vessel-abc".into(),
        inspector_id: "crew-42".into(),
        port_of_inspection: "Busan".into(),
        mou_region: "TOKYO".into(),
        started_at: "2026-04-29T10:00:00Z".into(),
        completed_at: None,
        summary_json: "{}".into(),
    }
}

fn sample_detection() -> DetectionRecord {
    DetectionRecord {
        id: "det-001".into(),
        inspection_id: "insp-001".into(),
        defect_type: "RUST".into(),
        confidence: 0.87,
        bbox_json: r#"{"x_min":0.1,"y_min":0.1,"x_max":0.4,"y_max":0.4}"#.into(),
        psc_code: Some("0615".into()),
        severity: "HIGH".into(),
        model_version: "0.1.0".into(),
        inference_time_ms: 42.5,
        timestamp: "2026-04-29T10:05:00Z".into(),
    }
}

#[test]
fn init_creates_tables() {
    let mgr = make_manager();
    let stats = mgr.get_sync_stats().unwrap();
    assert_eq!(stats.pending_count, 0);
    assert_eq!(stats.synced_count, 0);
}

#[test]
fn store_and_retrieve_inspection() {
    let mgr = make_manager();
    let record = sample_inspection();
    mgr.store_inspection(&record).unwrap();

    let retrieved = mgr.get_inspection("insp-001").unwrap();
    assert!(retrieved.is_some());
    let r = retrieved.unwrap();
    assert_eq!(r.vessel_id, "vessel-abc");
    assert_eq!(r.port_of_inspection, "Busan");
}

#[test]
fn store_detection() {
    let mgr = make_manager();
    mgr.store_inspection(&sample_inspection()).unwrap();
    mgr.store_detection(&sample_detection()).unwrap();
}

#[test]
fn sync_queue_priority_ordering() {
    let mgr = make_manager();

    mgr.queue_for_sync("low-item", "log", SyncPriority::Low).unwrap();
    mgr.queue_for_sync("critical-item", "defect_alert", SyncPriority::Critical).unwrap();
    mgr.queue_for_sync("normal-item", "inspection", SyncPriority::Normal).unwrap();

    let pending = mgr.get_pending_sync().unwrap();
    assert_eq!(pending.len(), 3);
    assert_eq!(pending[0].record_id, "critical-item");
    assert_eq!(pending[1].record_id, "normal-item");
    assert_eq!(pending[2].record_id, "low-item");
}

#[test]
fn mark_synced_updates_stats() {
    let mgr = make_manager();
    mgr.queue_for_sync("item-1", "inspection", SyncPriority::Normal).unwrap();
    mgr.queue_for_sync("item-2", "inspection", SyncPriority::Normal).unwrap();

    let stats_before = mgr.get_sync_stats().unwrap();
    assert_eq!(stats_before.pending_count, 2);
    assert_eq!(stats_before.synced_count, 0);

    mgr.mark_synced("item-1").unwrap();

    let stats_after = mgr.get_sync_stats().unwrap();
    assert_eq!(stats_after.pending_count, 1);
    assert_eq!(stats_after.synced_count, 1);
    assert!(stats_after.last_sync_timestamp.is_some());
}

#[test]
fn nonexistent_inspection_returns_none() {
    let mgr = make_manager();
    let result = mgr.get_inspection("does-not-exist").unwrap();
    assert!(result.is_none());
}
