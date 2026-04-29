use anyhow::Result;
use bwave_edge_platform::{
    GatewayConfig, OtGateway, RuleEngine, RuntimeManager, SecurityConfig, SecurityManager,
    SyncManager,
};
use tracing::info;

const VERSION: &str = env!("CARGO_PKG_VERSION");

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt::init();

    info!("╔══════════════════════════════════════╗");
    info!("║  B-Wave Edge Platform v{}         ║", VERSION);
    info!("║  PSC Defect Diagnosis — Edge Server  ║");
    info!("╚══════════════════════════════════════╝");

    let mut runtime = RuntimeManager::new();
    runtime.start()?;

    let rule_engine = RuleEngine::new();
    info!(
        rule_count = rule_engine.get_all_rules().len(),
        "Rule engine loaded"
    );

    let sync_manager = SyncManager::new("bwave_edge.db")?;
    let stats = sync_manager.get_sync_stats()?;
    info!(pending = stats.pending_count, "Sync manager ready");

    let gateway = OtGateway::new(GatewayConfig::default());
    info!(
        protocols = ?gateway.config().enabled_protocols,
        "OT gateway configured (READ-ONLY)"
    );

    let security = SecurityManager::new(SecurityConfig::default());
    info!(
        rbac = security.config().rbac_enabled,
        "Security module active"
    );

    info!("Edge platform fully operational — awaiting Ctrl+C");
    tokio::signal::ctrl_c().await?;
    info!("Shutdown signal received — stopping");

    gateway.stop();
    info!("Edge platform stopped");
    Ok(())
}
