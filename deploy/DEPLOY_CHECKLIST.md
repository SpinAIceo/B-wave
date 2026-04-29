# B-Wave PoC Deployment Checklist

## Pre-deployment
- [ ] Edge server hardware verified (CPU ≥2 cores, RAM ≥4GB, Disk ≥32GB, IP65 rated)
- [ ] Mesh AP hardware procured and bench-tested
- [ ] PKI CA initialized (`deploy/pki/init-ca.sh`)
- [ ] Vessel certificates issued (`deploy/pki/issue-vessel-cert.sh`)
- [ ] Tablet client certificates issued for all crew (`deploy/pki/issue-tablet-cert.sh`)
- [ ] AI model trained and exported to ONNX (<50MB)
- [ ] ONNX model validated on target hardware (Intel N100 or Jetson Orin Nano)

## Edge Server Setup
- [ ] Ubuntu Server 22.04 LTS installed on edge mini PC
- [ ] Docker Engine and Docker Compose plugin installed
- [ ] `provision-edge.sh` executed successfully
- [ ] All 3 services healthy: ai-engine, edge-platform, mesh-monitor
- [ ] gRPC inference verified on port 50051
- [ ] Edge API responding on port 8080
- [ ] SQLite database initialized at /opt/bwave/data/

## Mesh Network
- [ ] AP placement per vessel layout (engine room, deck, bridge)
- [ ] 802.11s mesh configured (`packages/mesh-network/configs/`)
- [ ] Tablet connectivity verified from all vessel zones
- [ ] Latency test: <100ms image transmission (engine room → edge server)
- [ ] Signal strength survey completed and documented
- [ ] Failover tested: AP removed, tablets reconnect via alternate path

## Security (UR E26/E27)
- [ ] mTLS certificates installed on edge server (/opt/bwave/certs/)
- [ ] Tablet client certificates enrolled (.p12 imported)
- [ ] RBAC roles configured: Captain, ChiefEngineer, Officer, Crew
- [ ] Audit logging active and writing to /opt/bwave/logs/
- [ ] OT network isolation verified — no write access from edge server
- [ ] CRL distribution mechanism tested
- [ ] Unauthenticated tablet access rejected

## Mobile App
- [ ] B-Wave app installed on all test tablets (Android 11+ / iOS 16+)
- [ ] Edge server connection established over mesh network
- [ ] Camera scan working: live preview + defect overlay
- [ ] Bounding box colors correct (rust=orange, damage=red, leak=blue)
- [ ] PSC code displayed for each detected defect
- [ ] Offline mode tested: disconnect satellite, all features work
- [ ] Glove-friendly UI verified (touch targets ≥48dp)
- [ ] Dark mode usable in engine room, light mode usable on deck

## Integration Verification
- [ ] E2E defect detection: camera → gRPC → AI → response → overlay (<500ms)
- [ ] PSC code mapping accurate for all 5 defect types
- [ ] Cargo Securing detection working (CIC 2026)
- [ ] Inspection checklist generation for target port
- [ ] Inspection report generation with defect images
- [ ] Offline data accumulation over 24-hour period

## Shore Server (if Enterprise tier)
- [ ] Fleet View backend deployed (`deploy/shore/docker-compose.yml`)
- [ ] PostgreSQL/TimescaleDB healthy
- [ ] Dashboard accessible at fleet.bwave.spinai.com
- [ ] Sync test: simulate satellite reconnect, verify data transfer
- [ ] Webhook alerts configured and tested
- [ ] Audit report generation working

## OTA Update Pipeline
- [ ] OTA server running on shore
- [ ] Edge client can check for updates when satellite available
- [ ] Update package created and signed
- [ ] Update download, verify, apply tested
- [ ] Rollback mechanism tested (kill service during update)

## Performance Benchmarks
- [ ] AI inference latency: ______ms (target <500ms)
- [ ] Mesh network latency: ______ms (target <100ms)
- [ ] End-to-end latency: ______ms (target <600ms)
- [ ] Concurrent tablet connections: ______ (target ≥3)
- [ ] 24h stability test passed (no crashes, no memory leaks)

## Sign-off
- [ ] Ship management company representative approval
- [ ] Class society notification (KR/DNV if required)
- [ ] Crew training completed (≤30 minutes per crew member)
- [ ] Training material delivered (quick-start guide)
- [ ] Support contact and escalation path established
- [ ] PoC success criteria documented and agreed
