use bwave_edge_platform::rule_engine::{DetectedDefect, RuleEngine, Severity};

#[test]
fn loads_embedded_rules() {
    let engine = RuleEngine::new();
    assert!(engine.get_all_rules().len() >= 10);
}

#[test]
fn rust_defect_maps_to_hull_violation() {
    let engine = RuleEngine::new();
    let defects = vec![DetectedDefect {
        defect_type: "RUST".into(),
        confidence: 0.85,
        bbox: (0.1, 0.1, 0.4, 0.4),
    }];
    let violations = engine.map_defects_to_violations(&defects);
    assert!(!violations.is_empty());
    assert!(violations.iter().any(|v| v.rule.psc_code == "0615"));
}

#[test]
fn cargo_lashing_maps_to_cargo_rules() {
    let engine = RuleEngine::new();
    let defects = vec![DetectedDefect {
        defect_type: "CARGO_LASHING".into(),
        confidence: 0.92,
        bbox: (0.2, 0.2, 0.6, 0.6),
    }];
    let violations = engine.map_defects_to_violations(&defects);
    assert!(violations.iter().any(|v| v.rule.psc_code == "0725"));
    assert!(violations.iter().any(|v| v.rule.psc_code == "0728"));
}

#[test]
fn high_confidence_escalates_severity() {
    let engine = RuleEngine::new();
    let defects = vec![DetectedDefect {
        defect_type: "RUST".into(),
        confidence: 0.95,
        bbox: (0.0, 0.0, 0.5, 0.5),
    }];
    let violations = engine.map_defects_to_violations(&defects);
    let hull = violations.iter().find(|v| v.rule.psc_code == "0615").unwrap();
    assert_eq!(hull.effective_severity, Severity::Critical);
}

#[test]
fn low_confidence_downgrades_severity() {
    let engine = RuleEngine::new();
    let defects = vec![DetectedDefect {
        defect_type: "DAMAGE".into(),
        confidence: 0.3,
        bbox: (0.0, 0.0, 0.5, 0.5),
    }];
    let violations = engine.map_defects_to_violations(&defects);
    let nav = violations.iter().find(|v| v.rule.psc_code == "1110").unwrap();
    assert_eq!(nav.effective_severity, Severity::Low);
}

#[test]
fn cic_targets_are_cargo_related() {
    let engine = RuleEngine::new();
    let cic = engine.get_cic_targets();
    assert!(cic.len() >= 3);
    for rule in &cic {
        assert!(
            rule.category.contains("Cargo"),
            "CIC rule {} should be cargo-related",
            rule.psc_code
        );
    }
}

#[test]
fn port_focus_tokyo_includes_labour() {
    let engine = RuleEngine::new();
    let rules = engine.get_port_focus("Busan", "TOKYO");
    assert!(rules.iter().any(|r| r.psc_code == "1320"));
}

#[test]
fn port_focus_all_includes_universal_rules() {
    let engine = RuleEngine::new();
    let tokyo = engine.get_port_focus("Busan", "TOKYO");
    let paris = engine.get_port_focus("Rotterdam", "PARIS");
    // Universal rules (mou_regions = ["*"]) appear in both
    assert!(tokyo.iter().any(|r| r.psc_code == "0615"));
    assert!(paris.iter().any(|r| r.psc_code == "0615"));
}

#[test]
fn no_violations_for_unknown_defect_type() {
    let engine = RuleEngine::new();
    let defects = vec![DetectedDefect {
        defect_type: "UNKNOWN_TYPE".into(),
        confidence: 0.9,
        bbox: (0.0, 0.0, 0.5, 0.5),
    }];
    let violations = engine.map_defects_to_violations(&defects);
    assert!(violations.is_empty());
}
