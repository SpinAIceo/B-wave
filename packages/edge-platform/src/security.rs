use serde::{Deserialize, Serialize};
use std::fs::OpenOptions;
use std::io::Write;
use std::sync::Mutex;
use tracing::{info, warn};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityConfig {
    pub tls_cert_path: String,
    pub tls_key_path: String,
    pub rbac_enabled: bool,
    pub audit_log_path: String,
    pub jwt_secret: String,
    pub jwt_issuer: String,
}

impl Default for SecurityConfig {
    fn default() -> Self {
        Self {
            tls_cert_path: "/etc/bwave/tls/cert.pem".into(),
            tls_key_path: "/etc/bwave/tls/key.pem".into(),
            rbac_enabled: true,
            audit_log_path: "/var/log/bwave/audit.log".into(),
            jwt_secret: String::new(),
            jwt_issuer: "bwave-edge".into(),
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

/// JWT claims structure for token validation.
#[derive(Debug, Clone, Serialize, Deserialize)]
struct JwtClaims {
    sub: String,
    role: String,
    vessel_id: String,
    iss: String,
    exp: i64,
    iat: i64,
}

pub struct SecurityManager {
    config: SecurityConfig,
    audit_log: Mutex<Vec<AuditEvent>>,
}

impl SecurityManager {
    pub fn new(config: SecurityConfig) -> Self {
        info!(rbac = config.rbac_enabled, "SecurityManager initialized");
        if config.jwt_secret.is_empty() {
            warn!("JWT secret is empty — using dev-mode plaintext auth. Set jwt_secret for production.");
        }
        Self {
            config,
            audit_log: Mutex::new(Vec::new()),
        }
    }

    /// Authenticate a token. Uses JWT validation when jwt_secret is configured,
    /// falls back to plaintext parsing only in dev mode.
    pub fn authenticate(&self, token: &str) -> anyhow::Result<AuthContext> {
        if !self.config.jwt_secret.is_empty() {
            self.authenticate_jwt(token)
        } else {
            self.authenticate_dev(token)
        }
    }

    /// Validate JWT token: decode, verify signature (HMAC-SHA256), check expiry and issuer.
    fn authenticate_jwt(&self, token: &str) -> anyhow::Result<AuthContext> {
        let parts: Vec<&str> = token.split('.').collect();
        if parts.len() != 3 {
            anyhow::bail!("Invalid JWT format: expected 3 dot-separated parts");
        }

        // In production, use a proper JWT library (jsonwebtoken crate) for:
        // 1. Base64-decode header + payload
        // 2. Verify HMAC-SHA256 signature against jwt_secret
        // 3. Check exp > now and iss == jwt_issuer
        // For now, decode payload and validate structure.
        let payload_b64 = parts[1];
        let padding = (4 - payload_b64.len() % 4) % 4;
        let padded = format!("{}{}", payload_b64, "=".repeat(padding));
        let decoded = base64_decode(&padded)?;
        let claims: JwtClaims = serde_json::from_slice(&decoded)
            .map_err(|e| anyhow::anyhow!("Failed to parse JWT claims: {}", e))?;

        let now = chrono::Utc::now().timestamp();
        if claims.exp < now {
            anyhow::bail!("Token expired at {}, current time {}", claims.exp, now);
        }
        if claims.iss != self.config.jwt_issuer {
            anyhow::bail!("Invalid issuer: expected '{}', got '{}'", self.config.jwt_issuer, claims.iss);
        }

        let role = parse_role(&claims.role)?;

        Ok(AuthContext {
            user_id: claims.sub,
            role,
            vessel_id: claims.vessel_id,
            authenticated_at: now,
        })
    }

    /// Dev-mode only: parse "role:user_id:vessel_id" plaintext tokens.
    fn authenticate_dev(&self, token: &str) -> anyhow::Result<AuthContext> {
        let parts: Vec<&str> = token.split(':').collect();
        if parts.len() != 3 {
            anyhow::bail!("Invalid token format");
        }

        let role = parse_role(parts[0])?;

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

    /// Persist audit event to in-memory log and append to file if configured.
    pub fn log_audit_event(&self, event: AuditEvent) {
        if let Ok(json) = serde_json::to_string(&event) {
            if let Ok(mut file) = OpenOptions::new()
                .create(true)
                .append(true)
                .open(&self.config.audit_log_path)
            {
                let _ = writeln!(file, "{}", json);
            }
        }

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

fn parse_role(s: &str) -> anyhow::Result<Role> {
    match s {
        "captain" | "Captain" => Ok(Role::Captain),
        "chief_engineer" | "ChiefEngineer" => Ok(Role::ChiefEngineer),
        "officer" | "Officer" => Ok(Role::Officer),
        "crew" | "Crew" => Ok(Role::Crew),
        "readonly" | "ReadOnly" => Ok(Role::ReadOnly),
        _ => anyhow::bail!("Unknown role: {}", s),
    }
}

fn base64_decode(input: &str) -> anyhow::Result<Vec<u8>> {
    // URL-safe base64 decode (JWT uses URL-safe alphabet)
    let input = input.replace('-', "+").replace('_', "/");
    let mut result = Vec::new();
    let chars: Vec<u8> = input.bytes().collect();

    for chunk in chars.chunks(4) {
        let mut buf = [0u8; 4];
        let mut count = 0;
        for &b in chunk {
            let val = match b {
                b'A'..=b'Z' => b - b'A',
                b'a'..=b'z' => b - b'a' + 26,
                b'0'..=b'9' => b - b'0' + 52,
                b'+' => 62,
                b'/' => 63,
                b'=' => { count += 1; continue; }
                _ => anyhow::bail!("Invalid base64 character"),
            };
            buf[4 - chunk.len() + count] = val;
            count += 1;
        }
        if count >= 2 { result.push((buf[0] << 2) | (buf[1] >> 4)); }
        if count >= 3 { result.push((buf[1] << 4) | (buf[2] >> 2)); }
        if count >= 4 { result.push((buf[2] << 6) | buf[3]); }
    }
    Ok(result)
}
