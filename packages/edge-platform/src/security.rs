use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tracing::info;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityConfig {
    pub tls_cert_path: String,
    pub tls_key_path: String,
    pub rbac_enabled: bool,
    pub audit_log_path: String,
}

impl Default for SecurityConfig {
    fn default() -> Self {
        Self {
            tls_cert_path: "/etc/bwave/tls/cert.pem".into(),
            tls_key_path: "/etc/bwave/tls/key.pem".into(),
            rbac_enabled: true,
            audit_log_path: "/var/log/bwave/audit.log".into(),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Role {
    Captain,
    ChiefEngineer,
    Officer,
    Crew,
    ReadOnly,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthContext {
    pub user_id: String,
    pub role: Role,
    pub vessel_id: String,
    pub authenticated_at: i64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum AuditResult {
    Success,
    Denied,
    Error,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditEvent {
    pub timestamp: i64,
    pub user_id: String,
    pub action: String,
    pub resource: String,
    pub result: AuditResult,
    pub details: String,
}

pub struct SecurityManager {
    config: SecurityConfig,
    audit_log: Mutex<Vec<AuditEvent>>,
}

impl SecurityManager {
    pub fn new(config: SecurityConfig) -> Self {
        info!(rbac = config.rbac_enabled, "SecurityManager initialized");
        Self {
            config,
            audit_log: Mutex::new(Vec::new()),
        }
    }

    /// Authenticate a user token. In production this would verify JWT/mTLS certificates.
    pub fn authenticate(&self, token: &str) -> anyhow::Result<AuthContext> {
        // Placeholder: parse "role:user_id:vessel_id" format
        let parts: Vec<&str> = token.split(':').collect();
        if parts.len() != 3 {
            anyhow::bail!("Invalid token format");
        }

        let role = match parts[0] {
            "captain" => Role::Captain,
            "chief_engineer" => Role::ChiefEngineer,
            "officer" => Role::Officer,
            "crew" => Role::Crew,
            "readonly" => Role::ReadOnly,
            _ => anyhow::bail!("Unknown role: {}", parts[0]),
        };

        Ok(AuthContext {
            user_id: parts[1].into(),
            role,
            vessel_id: parts[2].into(),
            authenticated_at: chrono::Utc::now().timestamp(),
        })
    }

    /// Check if the authenticated user is authorized for the given action.
    pub fn authorize(&self, ctx: &AuthContext, action: &str) -> bool {
        if !self.config.rbac_enabled {
            return true;
        }

        match ctx.role {
            Role::Captain => true,
            Role::ChiefEngineer => matches!(
                action,
                "inspection.create"
                    | "inspection.view"
                    | "defect.review"
                    | "report.view"
                    | "report.generate"
                    | "scan.run"
            ),
            Role::Officer => matches!(
                action,
                "inspection.create" | "inspection.view" | "report.view" | "scan.run"
            ),
            Role::Crew => matches!(action, "scan.run" | "scan.view_own"),
            Role::ReadOnly => matches!(
                action,
                "inspection.view" | "report.view" | "defect.view" | "dashboard.view"
            ),
        }
    }

    pub fn log_audit_event(&self, event: AuditEvent) {
        if let Ok(mut log) = self.audit_log.lock() {
            log.push(event);
        }
    }

    pub fn get_audit_log(&self, since: i64) -> Vec<AuditEvent> {
        self.audit_log
            .lock()
            .map(|log| {
                log.iter()
                    .filter(|e| e.timestamp >= since)
                    .cloned()
                    .collect()
            })
            .unwrap_or_default()
    }

    pub fn config(&self) -> &SecurityConfig {
        &self.config
    }
}
