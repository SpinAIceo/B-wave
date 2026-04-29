# Stage 07 PoC Deploy — Handoff

## 완료된 작업
- [x] Mesh network test tools (bandwidth, signal survey, monitor, topology validator)
- [x] Zone-specific AP configs (bridge, engine room, deck, cargo hold)
- [x] Edge server Docker Compose provisioning
- [x] One-click provision.sh and hardware-check.sh
- [x] OTA update pipeline with integrity verification and rollback
- [x] PKI certificate management (CA, vessel certs, mTLS)
- [x] Deployment guide with quick start, zone diagrams, benchmarks, troubleshooting

## 핵심 결정 사항

| 결정 | 근거 | 기각된 대안 |
|------|------|-------------|
| 2.4GHz for steel zones | Better penetration through bulkheads (-15dB vs -30dB at 5GHz) | 5GHz everywhere |
| Docker Compose over K3s for PoC | Simpler for single-node edge deployment, K3s for scale later | Full K3s from day 1 |
| GPG + SHA256 for OTA | Proven integrity chain, works offline | Custom signing |
| Self-signed CA per vessel | Offline operation requires self-contained PKI | Central CA (needs connectivity) |

## 다음 단계 (Production Readiness)
- Real vessel RF survey with actual hardware
- NMEA 2000 / Modbus TCP integration testing with real OT equipment
- Stress test: sustained 2 FPS image streaming over mesh for 8 hours
- mTLS certificate rotation automation
- K3s migration for multi-container orchestration at scale
- IACS Type Approval submission preparation

## 산출물 경로

| 산출물 | 경로 |
|--------|------|
| Mesh test scripts | `packages/mesh-network/scripts/` |
| Zone AP configs | `packages/mesh-network/configs/zones/` |
| Deployment guide | `packages/mesh-network/docs/deployment-guide.md` |
| Docker Compose | `deploy/docker/docker-compose.yml` |
| Provisioning scripts | `deploy/scripts/` |
| OTA pipeline | `deploy/ota/` |
| PKI scripts | `deploy/pki/` |
