# Mesh Network Deployment Guide

## Quick Start

```bash
# 1. Configure mesh nodes
cp configs/zones/zone-*.conf /etc/bwave/
vi /etc/bwave/zone-engine-room.conf   # adjust per vessel

# 2. Set up mesh on each node
./scripts/setup-mesh.sh --config /etc/bwave/zone-engine-room.conf

# 3. Validate topology
./scripts/validate-topology.sh --mesh-id bwave-vessel --edge-ip 192.168.1.1

# 4. Run signal survey at each location
./scripts/signal-survey.sh --location "Engine Room Aft" --output survey.csv

# 5. Bandwidth test
./scripts/bandwidth-test.sh --server 192.168.1.1 --duration 30 --output results.json

# 6. Start monitor daemon
./scripts/mesh-monitor.sh --edge-ip 192.168.1.1 &
```

---

## Zone-Based AP Placement

```
                    ┌─────────────────────────────────────────────┐
                    │                  BRIDGE                      │
                    │               [AP: zone-bridge]              │
                    │                 ch36 / 5GHz                  │
                    └─────────────────────┬───────────────────────┘
                                          │ (open stairway)
    ┌─────────────────────────────────────┴────────────────────────┐
    │                       MAIN DECK CORRIDOR                      │
    │                      [AP: zone-deck] x2                       │
    │                        ch44 / 5GHz                            │
    │    (weatherproof IP67 enclosures for outdoor APs)             │
    └───────┬─────────────────────────────────────┬────────────────┘
            │ (hatch coaming)                     │ (engine room hatch)
    ┌───────▼──────────────┐          ┌───────────▼────────────────┐
    │    CARGO HOLD(S)     │          │       ENGINE ROOM           │
    │  [AP: zone-cargo] x2 │          │   [AP: zone-engine-room]    │
    │   ch1 / 2.4GHz       │          │     ch6 / 2.4GHz            │
    │  (max TX, panel ant.) │          │   (max TX, high gain)       │
    └──────────────────────┘          └────────────────────────────┘
                                                │
                                      ┌─────────▼──────────┐
                                      │   EDGE SERVER       │
                                      │  (wired Ethernet)   │
                                      │  192.168.1.1:50051  │
                                      └────────────────────┘
```

### Placement Rules
- One AP per watertight compartment boundary
- Maximum 2 hops between any tablet and the edge server
- Keep APs at least 1m from large metal surfaces to reduce reflections
- Use bulkhead cable penetrations or open hatches as RF paths
- 2.4GHz for steel-enclosed spaces (engine room, cargo hold) — better penetration
- 5GHz for open areas (deck, bridge) — better bandwidth

---

## AP Placement Strategy for Steel Hull Vessels

Steel bulkheads attenuate Wi-Fi signals by 15–30 dB per wall. Plan for line-of-sight through doorways and hatches rather than through-wall penetration.

### Recommended node positions
1. **Engine room** — mount near the entrance hatch, above head height to avoid machinery obstruction
2. **Main deck corridor** — central placement to relay between engine room and bridge nodes
3. **Bridge / wheelhouse** — near the chart table area where inspections are initiated
4. **Cargo hold access** — at the hatch coaming for cargo securing inspections

---

## Recommended Hardware (COTS)

| Model | 802.11s | Form Factor | IP Rating | Notes |
|-------|---------|-------------|-----------|-------|
| GL.iNet GL-MT3000 | Yes (OpenWrt) | Compact | IP20 (enclose) | Low cost, proven OpenWrt mesh |
| Mikrotik RBD25G-5HPacQD2HPnD | Yes (RouterOS) | Weatherproof | IP55 | Outdoor-rated, high TX power |
| PC Engines APU4D4 + WLE900VX | Yes (OpenWrt) | Board + miniPCIe | Needs enclosure | Maximum flexibility |

All models support 802.11s via open firmware. Enclose non-IP-rated units in IP65 junction boxes for engine room deployment.

---

## Performance Benchmarks (Expected)

| Zone | Signal (dBm) | Throughput (Mbps) | Latency (ms) | Band |
|------|-------------|-------------------|--------------|------|
| Bridge | -35 to -50 | 80-150 | 5-15 | 5GHz |
| Main Deck | -45 to -60 | 50-100 | 10-25 | 5GHz |
| Engine Room | -55 to -75 | 15-50 | 20-60 | 2.4GHz |
| Cargo Hold | -65 to -85 | 10-30 | 30-80 | 2.4GHz |

**Pass criteria for B-Wave operation:**
- Throughput ≥ 10 Mbps (supports ~2 FPS JPEG at 720p)
- Latency ≤ 100 ms (within inference budget)
- Packet loss ≤ 5%

---

## Testing Procedure

### 1. Bench test (lab)
- Configure 3 nodes on a bench with mesh-node.conf
- Verify mesh peer formation: `iw dev mesh0 station dump`
- Measure throughput with iperf3: target ≥50 Mbps per hop

### 2. RF survey (docked vessel)
- Place nodes at planned positions
- Walk all inspection routes running `signal-survey.sh` at each stop
- Confirm signal ≥ -70 dBm everywhere a camera scan may occur
- Generate survey CSV for documentation

### 3. Underway test
- Repeat RF survey while vessel is underway (engine vibration changes RF environment)
- Run `bandwidth-test.sh` for 30 minutes at full frame rate
- Confirm latency < 100ms to edge server from all positions
- Start `mesh-monitor.sh` and observe 1 hour of metrics

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| No mesh peers | Wrong mesh_id or channel | Verify `iw dev mesh0 info`, match configs |
| High latency (>100ms) | Too many hops or weak signal | Add relay AP, adjust placement |
| Intermittent drops | Engine vibration shifting antenna | Secure mount with vibration dampeners |
| Low throughput in engine room | Steel interference on 5GHz | Switch to 2.4GHz (zone-engine-room.conf) |
| Tablet can't find mesh | AP not bridging to mesh | Check ap-bridge.conf, verify br0 interface |
| Signal survey shows POOR | AP too far from test point | Move AP closer or add intermediate node |
| Monitor shows HIGH_LOSS | Congested channel | Use `iw dev mesh0 survey dump` to find cleaner channel |
