//! OT Data Collection Gateway — UNIDIRECTIONAL (READ-ONLY)
//!
//! This module collects sensor data from the vessel's OT network.
//! All operations are strictly read-only. No write path to OT exists.
//! This is a hard safety requirement per IMO UR E26/E27.

use anyhow::Result;
use chrono::Utc;
use serde::{Deserialize, Serialize};
use tracing::{debug, info, warn};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Protocol {
    Nmea2000,
    ModbusTcp,
    OpcUa,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GatewayConfig {
    pub poll_interval_secs: u64,
    pub enabled_protocols: Vec<Protocol>,
    pub read_timeout_ms: u64,
}

impl Default for GatewayConfig {
    fn default() -> Self {
        Self {
            poll_interval_secs: 5,
            enabled_protocols: vec![Protocol::Nmea2000, Protocol::ModbusTcp],
            read_timeout_ms: 3000,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SensorReading {
    pub sensor_id: String,
    pub value: f64,
    pub unit: String,
    pub timestamp: i64,
    pub protocol: Protocol,
}

/// OT network gateway — read-only by design.
///
/// This struct intentionally exposes NO methods that accept mutable data destined
/// for the OT network. All data flows one way: OT → Edge.
pub struct OtGateway {
    config: GatewayConfig,
    running: std::sync::atomic::AtomicBool,
}

impl OtGateway {
    pub fn new(config: GatewayConfig) -> Self {
        Self {
            config,
            running: std::sync::atomic::AtomicBool::new(false),
        }
    }

    /// Read sensor data from the OT network (READ-ONLY).
    ///
    /// In production this connects to NMEA 2000, Modbus TCP, or OPC-UA
    /// endpoints and reads current values. The current implementation returns
    /// simulated data for development/testing.
    pub fn read_sensor_data(&self) -> Result<Vec<SensorReading>> {
        let now = Utc::now().timestamp();
        let mut readings = Vec::new();

        for protocol in &self.config.enabled_protocols {
            match protocol {
                Protocol::Nmea2000 => {
                    readings.push(SensorReading {
                        sensor_id: "nmea-gps-lat".into(),
                        value: 35.1028,
                        unit: "degrees".into(),
                        timestamp: now,
                        protocol: Protocol::Nmea2000,
                    });
                    readings.push(SensorReading {
                        sensor_id: "nmea-gps-lon".into(),
                        value: 129.0403,
                        unit: "degrees".into(),
                        timestamp: now,
                        protocol: Protocol::Nmea2000,
                    });
                    readings.push(SensorReading {
                        sensor_id: "nmea-sog".into(),
                        value: 12.4,
                        unit: "knots".into(),
                        timestamp: now,
                        protocol: Protocol::Nmea2000,
                    });
                }
                Protocol::ModbusTcp => {
                    readings.push(SensorReading {
                        sensor_id: "modbus-engine-rpm".into(),
                        value: 95.0,
                        unit: "rpm".into(),
                        timestamp: now,
                        protocol: Protocol::ModbusTcp,
                    });
                    readings.push(SensorReading {
                        sensor_id: "modbus-engine-temp".into(),
                        value: 82.5,
                        unit: "celsius".into(),
                        timestamp: now,
                        protocol: Protocol::ModbusTcp,
                    });
                    readings.push(SensorReading {
                        sensor_id: "modbus-fuel-level".into(),
                        value: 67.3,
                        unit: "percent".into(),
                        timestamp: now,
                        protocol: Protocol::ModbusTcp,
                    });
                }
                Protocol::OpcUa => {
                    readings.push(SensorReading {
                        sensor_id: "opcua-ballast-port".into(),
                        value: 45.2,
                        unit: "percent".into(),
                        timestamp: now,
                        protocol: Protocol::OpcUa,
                    });
                }
            }
        }

        debug!(count = readings.len(), "Read sensor data from OT network");
        Ok(readings)
    }

    /// Start continuous polling loop (async, read-only).
    pub async fn start_polling(&self, interval_secs: u64) {
        use std::sync::atomic::Ordering;
        self.running.store(true, Ordering::SeqCst);
        info!(interval_secs, "OT gateway polling started (READ-ONLY)");

        while self.running.load(Ordering::SeqCst) {
            match self.read_sensor_data() {
                Ok(readings) => {
                    debug!(count = readings.len(), "Polled OT sensor data");
                }
                Err(e) => {
                    warn!(error = %e, "Failed to read OT sensor data");
                }
            }
            tokio::time::sleep(tokio::time::Duration::from_secs(interval_secs)).await;
        }
    }

    /// Gracefully stop the polling loop.
    pub fn stop(&self) {
        self.running
            .store(false, std::sync::atomic::Ordering::SeqCst);
        info!("OT gateway polling stopped");
    }

    pub fn config(&self) -> &GatewayConfig {
        &self.config
    }
}
