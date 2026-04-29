#!/usr/bin/env bash
set -euo pipefail

# B-Wave Mesh Network Bandwidth Test Tool
# Tests TCP/UDP throughput, latency, and jitter against the edge server.
# Requires: iperf3, ping
# Usage: ./bandwidth-test.sh --server <edge-ip> [--duration 30] [--output results.json]

# --- Defaults ---
SERVER=""
DURATION=30
OUTPUT=""
PASS_THROUGHPUT_MBPS=10
PASS_LATENCY_MS=100
PASS_JITTER_MS=20

# --- Parse args ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --server)   SERVER="$2"; shift 2 ;;
    --duration) DURATION="$2"; shift 2 ;;
    --output)   OUTPUT="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 --server <edge-ip> [--duration 30] [--output results.json]"
      exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$SERVER" ]]; then
  echo "ERROR: --server is required"
  exit 1
fi

for cmd in iperf3 ping; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: $cmd not found. Install it first."
    exit 1
  fi
done

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "=== B-Wave Mesh Bandwidth Test ==="
echo "Server:   $SERVER"
echo "Duration: ${DURATION}s"
echo "Time:     $TIMESTAMP"
echo ""

# --- TCP Throughput ---
echo "[1/4] TCP throughput..."
TCP_JSON=$(iperf3 -c "$SERVER" -t "$DURATION" -J 2>/dev/null || echo '{}')
TCP_MBPS=$(echo "$TCP_JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"{d['end']['sum_received']['bits_per_second'] / 1e6:.2f}\")
except Exception:
    print('0.00')
" 2>/dev/null || echo "0.00")
echo "  TCP: ${TCP_MBPS} Mbps"

# --- UDP Throughput + Jitter ---
echo "[2/4] UDP throughput + jitter..."
UDP_JSON=$(iperf3 -c "$SERVER" -t "$DURATION" -u -b 50M -J 2>/dev/null || echo '{}')
UDP_MBPS=$(echo "$UDP_JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"{d['end']['sum']['bits_per_second'] / 1e6:.2f}\")
except Exception:
    print('0.00')
" 2>/dev/null || echo "0.00")
JITTER_MS=$(echo "$UDP_JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"{d['end']['sum']['jitter_ms']:.2f}\")
except Exception:
    print('0.00')
" 2>/dev/null || echo "0.00")
echo "  UDP: ${UDP_MBPS} Mbps, Jitter: ${JITTER_MS} ms"

# --- Latency ---
echo "[3/4] Latency (ping)..."
PING_OUT=$(ping -c 20 -W 2 "$SERVER" 2>/dev/null || echo "")
LATENCY_MS=$(echo "$PING_OUT" | tail -1 | sed -E 's|.*/([0-9.]+)/.*|\1|' || echo "0.00")
PACKET_LOSS=$(echo "$PING_OUT" | grep -oP '[0-9.]+(?=% packet loss)' || echo "0")
echo "  Avg latency: ${LATENCY_MS} ms, Packet loss: ${PACKET_LOSS}%"

# --- Evaluate ---
echo ""
echo "[4/4] Results:"

pass_tcp=$( echo "$TCP_MBPS $PASS_THROUGHPUT_MBPS" | awk '{print ($1 >= $2) ? "PASS" : "FAIL"}' )
pass_udp=$( echo "$UDP_MBPS $PASS_THROUGHPUT_MBPS" | awk '{print ($1 >= $2) ? "PASS" : "FAIL"}' )
pass_lat=$( echo "$LATENCY_MS $PASS_LATENCY_MS" | awk '{print ($1 <= $2) ? "PASS" : "FAIL"}' )
pass_jit=$( echo "$JITTER_MS $PASS_JITTER_MS" | awk '{print ($1 <= $2) ? "PASS" : "FAIL"}' )

printf "  %-25s %10s  [%s]\n" "TCP Throughput (≥${PASS_THROUGHPUT_MBPS}Mbps)" "${TCP_MBPS} Mbps" "$pass_tcp"
printf "  %-25s %10s  [%s]\n" "UDP Throughput (≥${PASS_THROUGHPUT_MBPS}Mbps)" "${UDP_MBPS} Mbps" "$pass_udp"
printf "  %-25s %10s  [%s]\n" "Latency (≤${PASS_LATENCY_MS}ms)" "${LATENCY_MS} ms" "$pass_lat"
printf "  %-25s %10s  [%s]\n" "Jitter (≤${PASS_JITTER_MS}ms)" "${JITTER_MS} ms" "$pass_jit"

overall="PASS"
for r in "$pass_tcp" "$pass_udp" "$pass_lat" "$pass_jit"; do
  [[ "$r" == "FAIL" ]] && overall="FAIL"
done
echo ""
echo "  Overall: $overall"

# --- JSON output ---
if [[ -n "$OUTPUT" ]]; then
  cat > "$OUTPUT" <<JSONEOF
{
  "timestamp": "$TIMESTAMP",
  "server": "$SERVER",
  "duration_seconds": $DURATION,
  "tcp_throughput_mbps": $TCP_MBPS,
  "udp_throughput_mbps": $UDP_MBPS,
  "latency_avg_ms": $LATENCY_MS,
  "jitter_ms": $JITTER_MS,
  "packet_loss_percent": $PACKET_LOSS,
  "overall": "$overall"
}
JSONEOF
  echo "Results saved to $OUTPUT"
fi
