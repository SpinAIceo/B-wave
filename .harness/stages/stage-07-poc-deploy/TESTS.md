# Stage 07 PoC Deploy — Verification Checklist

## Mesh Network
- [x] bandwidth-test.sh — iperf3 TCP/UDP, latency, jitter, pass/fail, JSON output
- [x] signal-survey.sh — RSSI, noise, SNR, quality rating, CSV append
- [x] mesh-monitor.sh — daemon with alerting (peers, signal, loss, latency), JSONL log
- [x] validate-topology.sh — 7-point check (interface, mesh ID, encryption, peers, ping, DNS, gRPC)
- [x] Zone configs — bridge, engine room, deck, cargo hold with tuned parameters

## Edge Server Provisioning
- [x] Docker Compose — ai-engine, edge-platform, mesh-monitor services
- [x] provision.sh — one-click setup (prerequisites, Docker install, config, health check)
- [x] hardware-check.sh — CPU, RAM, disk, temperature validation against minimum specs

## OTA Update Pipeline
- [x] ota-update.sh — download, verify (SHA256 + GPG signature), backup, apply, rollback on failure
- [x] update manifest schema (version, checksum, signature, changelog)

## PKI / Security
- [x] pki-init.sh — CA generation, vessel cert + edge cert issuance, mTLS config
- [x] Certificate directory structure and RBAC integration points documented

## Documentation
- [x] Deployment guide updated with quick start, zone diagram, benchmarks, troubleshooting
- [x] HANDOFF.md written
