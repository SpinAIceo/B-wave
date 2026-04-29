use serde::Serialize;
use std::time::Instant;
use tracing::info;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub enum ComponentStatus {
    Running,
    Stopped,
    Degraded,
    Failed,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub enum OverallStatus {
    Healthy,
    Degraded,
    Critical,
}

#[derive(Debug, Clone, Serialize)]
pub struct SystemHealth {
    pub overall_status: OverallStatus,
    pub ai_engine_status: ComponentStatus,
    pub rule_engine_status: ComponentStatus,
    pub storage_status: ComponentStatus,
    pub gateway_status: ComponentStatus,
    pub uptime_seconds: f64,
}

#[derive(Debug, Clone, Serialize)]
pub struct ResourceUsage {
    pub cpu_percent: f32,
    pub memory_used_mb: f64,
    pub memory_total_mb: f64,
    pub disk_used_mb: f64,
    pub disk_total_mb: f64,
    pub temperature_celsius: Option<f32>,
}

pub struct RuntimeManager {
    started_at: Option<Instant>,
    ai_engine_status: ComponentStatus,
    rule_engine_status: ComponentStatus,
    storage_status: ComponentStatus,
    gateway_status: ComponentStatus,
}

impl RuntimeManager {
    pub fn new() -> Self {
        Self {
            started_at: None,
            ai_engine_status: ComponentStatus::Stopped,
            rule_engine_status: ComponentStatus::Stopped,
            storage_status: ComponentStatus::Stopped,
            gateway_status: ComponentStatus::Stopped,
        }
    }

    pub fn start(&mut self) -> anyhow::Result<()> {
        info!("RuntimeManager starting all subsystems");
        self.started_at = Some(Instant::now());

        self.rule_engine_status = ComponentStatus::Running;
        info!("Rule engine: started");

        self.storage_status = ComponentStatus::Running;
        info!("Storage: started");

        self.gateway_status = ComponentStatus::Running;
        info!("OT gateway: started");

        self.ai_engine_status = ComponentStatus::Running;
        info!("AI engine: started");

        info!("All subsystems running");
        Ok(())
    }

    pub fn set_component_status(&mut self, component: &str, status: ComponentStatus) {
        match component {
            "ai_engine" => self.ai_engine_status = status,
            "rule_engine" => self.rule_engine_status = status,
            "storage" => self.storage_status = status,
            "gateway" => self.gateway_status = status,
            _ => {}
        }
    }

    pub fn health_check(&self) -> SystemHealth {
        let uptime = self
            .started_at
            .map(|s| s.elapsed().as_secs_f64())
            .unwrap_or(0.0);

        let statuses = [
            self.ai_engine_status,
            self.rule_engine_status,
            self.storage_status,
            self.gateway_status,
        ];

        let any_failed = statuses.iter().any(|s| *s == ComponentStatus::Failed);
        let any_degraded = statuses.iter().any(|s| *s == ComponentStatus::Degraded);

        let overall = if any_failed {
            OverallStatus::Critical
        } else if any_degraded {
            OverallStatus::Degraded
        } else {
            OverallStatus::Healthy
        };

        SystemHealth {
            overall_status: overall,
            ai_engine_status: self.ai_engine_status,
            rule_engine_status: self.rule_engine_status,
            storage_status: self.storage_status,
            gateway_status: self.gateway_status,
            uptime_seconds: uptime,
        }
    }

    pub fn get_resource_usage(&self) -> ResourceUsage {
        // Placeholder — in production, read from /proc or sysinfo crate
        ResourceUsage {
            cpu_percent: 0.0,
            memory_used_mb: 0.0,
            memory_total_mb: 0.0,
            disk_used_mb: 0.0,
            disk_total_mb: 0.0,
            temperature_celsius: None,
        }
    }
}

impl Default for RuntimeManager {
    fn default() -> Self {
        Self::new()
    }
}
