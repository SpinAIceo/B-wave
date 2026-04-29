#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();
    tracing::info!("B-Wave Edge Platform starting...");
}
