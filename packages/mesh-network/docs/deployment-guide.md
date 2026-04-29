# Mesh Network Deployment Guide

## AP Placement Strategy for Steel Hull Vessels

Steel bulkheads attenuate Wi-Fi signals by 15–30 dB per wall. Plan for line-of-sight through doorways and hatches rather than through-wall penetration.

### Recommended node positions
1. **Engine room** — mount near the entrance hatch, above head height to avoid machinery obstruction
2. **Main deck corridor** — central placement to relay between engine room and bridge nodes
3. **Bridge / wheelhouse** — near the chart table area where inspections are initiated
4. **Cargo hold access** — at the hatch coaming for cargo securing inspections

### Placement rules of thumb
- One node per watertight compartment boundary
- Maximum 2 hops between any tablet and the edge server
- Keep nodes at least 1m from large metal surfaces to reduce reflections
- Use bulkhead cable penetrations or open hatches as RF paths

## Recommended Hardware (COTS)

| Model | 802.11s | Form Factor | IP Rating | Notes |
|-------|---------|-------------|-----------|-------|
| GL.iNet GL-MT3000 | Yes (OpenWrt) | Compact | IP20 (enclose) | Low cost, proven OpenWrt mesh |
| Mikrotik RBD25G-5HPacQD2HPnD | Yes (RouterOS) | Weatherproof | IP55 | Outdoor-rated, high TX power |
| PC Engines APU4D4 + WLE900VX | Yes (OpenWrt) | Board + miniPCIe | Needs enclosure | Maximum flexibility |

All models support 802.11s via open firmware. Enclose non-IP-rated units in IP65 junction boxes for engine room deployment.

## Testing Procedure

### 1. Bench test (lab)
- Configure 3 nodes on a bench with mesh-node.conf
- Verify mesh peer formation: `iw dev mesh0 station dump`
- Measure throughput with iperf3: target ≥50 Mbps per hop

### 2. RF survey (docked vessel)
- Place nodes at planned positions
- Walk all inspection routes with a tablet running a Wi-Fi analyzer
- Confirm signal ≥ -70 dBm everywhere a camera scan may occur

### 3. Underway test
- Repeat RF survey while vessel is underway (engine vibration changes RF environment)
- Run a 30-minute sustained image transfer test at full frame rate
- Confirm latency < 100ms to edge server from all positions
