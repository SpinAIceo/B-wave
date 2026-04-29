pub mod gateway;
pub mod rule_engine;
pub mod runtime;
pub mod security;
pub mod sync_manager;

pub use gateway::{GatewayConfig, OtGateway, Protocol, SensorReading};
pub use rule_engine::{DetectedDefect, PscRule, PscViolation, RuleEngine, Severity};
pub use runtime::{RuntimeManager, SystemHealth, ResourceUsage};
pub use security::{AuthContext, AuditEvent, Role, SecurityConfig, SecurityManager};
pub use sync_manager::{
    DetectionRecord, InspectionRecord, SyncManager, SyncPriority, SyncQueueItem, SyncStats,
};
