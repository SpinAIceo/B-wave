use bwave_edge_platform::security::{
    AuditEvent, AuditResult, Role, SecurityConfig, SecurityManager,
};

fn make_manager() -> SecurityManager {
    SecurityManager::new(SecurityConfig::default())
}

fn make_manager_no_rbac() -> SecurityManager {
    SecurityManager::new(SecurityConfig {
        rbac_enabled: false,
        ..SecurityConfig::default()
    })
}

#[test]
fn authenticate_captain() {
    let mgr = make_manager();
    let ctx = mgr.authenticate("captain:kim:vessel-001").unwrap();
    assert_eq!(ctx.role, Role::Captain);
    assert_eq!(ctx.user_id, "kim");
    assert_eq!(ctx.vessel_id, "vessel-001");
}

#[test]
fn authenticate_all_roles() {
    let mgr = make_manager();
    for (token, expected) in [
        ("captain:a:v", Role::Captain),
        ("chief_engineer:b:v", Role::ChiefEngineer),
        ("officer:c:v", Role::Officer),
        ("crew:d:v", Role::Crew),
        ("readonly:e:v", Role::ReadOnly),
    ] {
        let ctx = mgr.authenticate(token).unwrap();
        assert_eq!(ctx.role, expected);
    }
}

#[test]
fn authenticate_invalid_token() {
    let mgr = make_manager();
    assert!(mgr.authenticate("bad-token").is_err());
}

#[test]
fn authenticate_unknown_role() {
    let mgr = make_manager();
    assert!(mgr.authenticate("admin:user:vessel").is_err());
}

#[test]
fn captain_can_do_anything() {
    let mgr = make_manager();
    let ctx = mgr.authenticate("captain:kim:v").unwrap();
    for action in [
        "inspection.create",
        "inspection.view",
        "defect.review",
        "report.view",
        "report.generate",
        "scan.run",
        "scan.view_own",
        "system.admin",
    ] {
        assert!(mgr.authorize(&ctx, action), "Captain should be allowed: {action}");
    }
}

#[test]
fn chief_engineer_permissions() {
    let mgr = make_manager();
    let ctx = mgr.authenticate("chief_engineer:park:v").unwrap();
    assert!(mgr.authorize(&ctx, "inspection.create"));
    assert!(mgr.authorize(&ctx, "defect.review"));
    assert!(mgr.authorize(&ctx, "report.generate"));
    assert!(!mgr.authorize(&ctx, "system.admin"));
}

#[test]
fn officer_permissions() {
    let mgr = make_manager();
    let ctx = mgr.authenticate("officer:lee:v").unwrap();
    assert!(mgr.authorize(&ctx, "inspection.create"));
    assert!(mgr.authorize(&ctx, "report.view"));
    assert!(!mgr.authorize(&ctx, "defect.review"));
    assert!(!mgr.authorize(&ctx, "report.generate"));
}

#[test]
fn crew_limited_to_scan() {
    let mgr = make_manager();
    let ctx = mgr.authenticate("crew:cho:v").unwrap();
    assert!(mgr.authorize(&ctx, "scan.run"));
    assert!(mgr.authorize(&ctx, "scan.view_own"));
    assert!(!mgr.authorize(&ctx, "inspection.create"));
    assert!(!mgr.authorize(&ctx, "report.view"));
}

#[test]
fn readonly_view_only() {
    let mgr = make_manager();
    let ctx = mgr.authenticate("readonly:auditor:v").unwrap();
    assert!(mgr.authorize(&ctx, "inspection.view"));
    assert!(mgr.authorize(&ctx, "report.view"));
    assert!(mgr.authorize(&ctx, "dashboard.view"));
    assert!(!mgr.authorize(&ctx, "scan.run"));
    assert!(!mgr.authorize(&ctx, "inspection.create"));
}

#[test]
fn rbac_disabled_allows_all() {
    let mgr = make_manager_no_rbac();
    let ctx = mgr.authenticate("readonly:guest:v").unwrap();
    assert!(mgr.authorize(&ctx, "system.admin"));
    assert!(mgr.authorize(&ctx, "scan.run"));
}

#[test]
fn audit_log_records_events() {
    let mgr = make_manager();
    let now = chrono::Utc::now().timestamp();

    mgr.log_audit_event(AuditEvent {
        timestamp: now,
        user_id: "kim".into(),
        action: "scan.run".into(),
        resource: "camera-1".into(),
        result: AuditResult::Success,
        details: "".into(),
    });
    mgr.log_audit_event(AuditEvent {
        timestamp: now + 1,
        user_id: "cho".into(),
        action: "report.generate".into(),
        resource: "report-42".into(),
        result: AuditResult::Denied,
        details: "Insufficient role".into(),
    });

    let log = mgr.get_audit_log(now);
    assert_eq!(log.len(), 2);
    assert_eq!(log[0].user_id, "kim");
    assert_eq!(log[1].result, AuditResult::Denied);
}

#[test]
fn audit_log_filters_by_timestamp() {
    let mgr = make_manager();
    mgr.log_audit_event(AuditEvent {
        timestamp: 100,
        user_id: "old".into(),
        action: "scan.run".into(),
        resource: "x".into(),
        result: AuditResult::Success,
        details: "".into(),
    });
    mgr.log_audit_event(AuditEvent {
        timestamp: 200,
        user_id: "new".into(),
        action: "scan.run".into(),
        resource: "y".into(),
        result: AuditResult::Success,
        details: "".into(),
    });

    let log = mgr.get_audit_log(150);
    assert_eq!(log.len(), 1);
    assert_eq!(log[0].user_id, "new");
}
