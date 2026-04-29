use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Severity {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PscRule {
    pub psc_code: String,
    pub category: String,
    pub description: String,
    pub severity: Severity,
    pub cic_target_2026: bool,
    pub mou_regions: Vec<String>,
    pub related_defect_types: Vec<String>,
    pub recommended_action: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DetectedDefect {
    pub defect_type: String,
    pub confidence: f32,
    pub bbox: (f32, f32, f32, f32),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PscViolation {
    pub rule: PscRule,
    pub defect: DetectedDefect,
    pub effective_severity: Severity,
}

pub struct RuleEngine {
    rules: Vec<PscRule>,
}

impl RuleEngine {
    pub fn new() -> Self {
        Self {
            rules: Self::load_embedded_rules(),
        }
    }

    pub fn map_defects_to_violations(&self, defects: &[DetectedDefect]) -> Vec<PscViolation> {
        let mut violations = Vec::new();
        for defect in defects {
            for rule in &self.rules {
                let type_upper = defect.defect_type.to_uppercase();
                if rule
                    .related_defect_types
                    .iter()
                    .any(|t| t.to_uppercase() == type_upper)
                {
                    let effective_severity =
                        Self::compute_severity(&rule.severity, defect.confidence);
                    violations.push(PscViolation {
                        rule: rule.clone(),
                        defect: defect.clone(),
                        effective_severity,
                    });
                }
            }
        }
        violations
    }

    pub fn get_port_focus(&self, _port_name: &str, mou_region: &str) -> Vec<PscRule> {
        let region_upper = mou_region.to_uppercase();
        self.rules
            .iter()
            .filter(|r| {
                r.mou_regions
                    .iter()
                    .any(|m| m.to_uppercase() == region_upper || m == "*")
            })
            .cloned()
            .collect()
    }

    pub fn get_cic_targets(&self) -> Vec<PscRule> {
        self.rules
            .iter()
            .filter(|r| r.cic_target_2026)
            .cloned()
            .collect()
    }

    pub fn get_all_rules(&self) -> &[PscRule] {
        &self.rules
    }

    fn compute_severity(base: &Severity, confidence: f32) -> Severity {
        if confidence >= 0.9 {
            match base {
                Severity::Low => Severity::Medium,
                Severity::Medium => Severity::High,
                Severity::High | Severity::Critical => Severity::Critical,
            }
        } else if confidence < 0.5 {
            match base {
                Severity::Critical => Severity::High,
                Severity::High => Severity::Medium,
                Severity::Medium | Severity::Low => Severity::Low,
            }
        } else {
            *base
        }
    }

    fn load_embedded_rules() -> Vec<PscRule> {
        vec![
            PscRule {
                psc_code: "0615".into(),
                category: "Hull and Structure".into(),
                description: "Hull corrosion — significant wastage of hull plating".into(),
                severity: Severity::High,
                cic_target_2026: false,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["RUST".into()],
                recommended_action:
                    "Assess structural integrity; arrange thickness measurement survey".into(),
            },
            PscRule {
                psc_code: "0630".into(),
                category: "Hull and Structure".into(),
                description: "Watertight / weathertight integrity deficiency".into(),
                severity: Severity::Critical,
                cic_target_2026: false,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["RUST".into(), "DAMAGE".into(), "LEAK".into()],
                recommended_action:
                    "Restore watertight integrity immediately; verify gaskets and closures".into(),
            },
            PscRule {
                psc_code: "0725".into(),
                category: "Cargo Operations".into(),
                description: "Cargo securing arrangements — lashing equipment defective or missing"
                    .into(),
                severity: Severity::High,
                cic_target_2026: true,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["CARGO_LASHING".into(), "DAMAGE".into()],
                recommended_action: "Replace defective lashing equipment before departure; verify Cargo Securing Manual compliance".into(),
            },
            PscRule {
                psc_code: "0726".into(),
                category: "Cargo Operations".into(),
                description: "Cargo securing manual — not on board or not followed".into(),
                severity: Severity::Medium,
                cic_target_2026: true,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["CARGO_LASHING".into(), "MISSING_LABEL".into()],
                recommended_action: "Ensure Cargo Securing Manual is available and crew is familiar with contents".into(),
            },
            PscRule {
                psc_code: "0740".into(),
                category: "Safety Equipment".into(),
                description: "Life-saving appliances — defective or missing equipment".into(),
                severity: Severity::Critical,
                cic_target_2026: false,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["DAMAGE".into(), "MISSING_LABEL".into()],
                recommended_action:
                    "Replace or repair life-saving equipment; verify servicing dates".into(),
            },
            PscRule {
                psc_code: "0750".into(),
                category: "Safety Equipment".into(),
                description: "Fire-fighting equipment — extinguishers expired or missing".into(),
                severity: Severity::High,
                cic_target_2026: false,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["DAMAGE".into(), "MISSING_LABEL".into()],
                recommended_action:
                    "Replace expired extinguishers; ensure inspection tags are current".into(),
            },
            PscRule {
                psc_code: "0785".into(),
                category: "Fire Safety".into(),
                description: "Fire detection and alarm system deficiency".into(),
                severity: Severity::Critical,
                cic_target_2026: false,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["DAMAGE".into()],
                recommended_action:
                    "Repair fire detection system; test all zones and verify alarm panels".into(),
            },
            PscRule {
                psc_code: "0950".into(),
                category: "Pollution Prevention".into(),
                description: "Oil leakage — visible oil leaks from machinery or piping".into(),
                severity: Severity::High,
                cic_target_2026: false,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["LEAK".into()],
                recommended_action:
                    "Identify and repair source of leak; clean affected area; check SOPEP".into(),
            },
            PscRule {
                psc_code: "1110".into(),
                category: "Navigation".into(),
                description:
                    "Navigation equipment deficiency — damaged or non-functional instruments"
                        .into(),
                severity: Severity::Medium,
                cic_target_2026: false,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["DAMAGE".into()],
                recommended_action:
                    "Repair or replace defective navigation equipment before departure".into(),
            },
            PscRule {
                psc_code: "1320".into(),
                category: "Labour / Living Conditions".into(),
                description: "Crew accommodation — corrosion, damage or unsanitary conditions"
                    .into(),
                severity: Severity::Medium,
                cic_target_2026: false,
                mou_regions: vec!["TOKYO".into(), "PARIS".into()],
                related_defect_types: vec!["RUST".into(), "DAMAGE".into(), "LEAK".into()],
                recommended_action:
                    "Repair or restore crew accommodation to MLC-compliant standard".into(),
            },
            PscRule {
                psc_code: "0727".into(),
                category: "Cargo Operations".into(),
                description: "Cargo hold — structural deficiency or corrosion in cargo hold".into(),
                severity: Severity::High,
                cic_target_2026: true,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["RUST".into(), "DAMAGE".into()],
                recommended_action: "Conduct structural assessment of cargo hold; address corrosion before loading".into(),
            },
            PscRule {
                psc_code: "0728".into(),
                category: "Cargo Operations".into(),
                description:
                    "Cargo securing devices — turnbuckles, lashing rods, or wires defective"
                        .into(),
                severity: Severity::Critical,
                cic_target_2026: true,
                mou_regions: vec!["*".into()],
                related_defect_types: vec!["CARGO_LASHING".into(), "DAMAGE".into()],
                recommended_action:
                    "Replace all defective securing devices; perform load test on replacements"
                        .into(),
            },
        ]
    }
}

impl Default for RuleEngine {
    fn default() -> Self {
        Self::new()
    }
}
