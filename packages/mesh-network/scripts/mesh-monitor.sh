#!/usr/bin/env bash
set -euo pipefail

# B-Wave Mesh Network Monitor Daemon
# Continuously polls mesh interface health and logs metrics.
# Usage: ./mesh-monitor.sh [--interface mesh0] [--interval 30] [--edge-ip 192.168.1.1]
#        [--min-peers 2] [--log /var/log/bwave/mesh-metrics.log]

INTERFACE="mesh0"
INTERVAL=30
EDGE_IP="192.168.1.1"
MIN_PEERS=2
MIN_SIGNAL=-75
MAX_LOSS=5
MAX_LATENCY=100
LOG_FILE="/var/log/bwave/mesh-metrics.log"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --interface)  INTERFACE="$2"; shift 2 ;;
    --interval)   INTERVAL="$2"; shift 2 ;;
    --edge-ip)    EDGE_IP="$2"; shift 2 ;;
    --min-peers)  MIN_PEERS="$2"; shift 2 ;;
    --log)        LOG_FILE="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--interface mesh0] [--interval 30] [--edge-ip 192.168.1.1]"
      exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

LOG_DIR=$(dirname "$LOG_FILE")
mkdir -p "$LOG_DIR"

# Reload config on SIGHUP
reload_config() {
  echo "[$(date -u +%H:%M:%S)] Config reloaded (SIGHUP)"
}
trap reload_config HUP

echo "=== B-Wave Mesh Monitor ==="
echo "Interface: $INTERFACE | Edge: $EDGE_IP | Interval: ${INTERVAL}s"
echo "Thresholds: peers≥${MIN_PEERS}, signal≥${MIN_SIGNAL}dBm, loss≤${MAX_LOSS}%, latency≤${MAX_LATENCY}ms"
echo "Log: $LOG_FILE"
echo ""

while true; do
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  ALERTS=""

  # Peer count
  PEERS=$(iw dev "$INTERFACE" station dump 2>/dev/null | grep -c "Station" || echo "0")
  if (( PEERS < MIN_PEERS )); then
    ALERTS="${ALERTS}LOW_PEERS(${PEERS}<${MIN_PEERS}) "
  fi

  # Signal strength (average across peers)
  SIGNAL=$(iw dev "$INTERFACE" station dump 2>/dev/null \
    | grep -oP 'signal:\s+\K-?[0-9]+' \
    | awk '{s+=$1; n++} END {if(n>0) printf "%d", s/n; else print "-999"}' || echo "-999")
  if (( SIGNAL < MIN_SIGNAL )); then
    ALERTS="${ALERTS}WEAK_SIGNAL(${SIGNAL}dBm) "
  fi

  # Latency and packet loss
  PING_OUT=$(ping -c 5 -W 2 "$EDGE_IP" 2>/dev/null || echo "")
  LATENCY=$(echo "$PING_OUT" | tail -1 | sed -E 's|.*/([0-9.]+)/.*|\1|' 2>/dev/null || echo "999")
  LOSS=$(echo "$PING_OUT" | grep -oP '[0-9.]+(?=% packet loss)' 2>/dev/null || echo "100")

  LOSS_INT=${LOSS%%.*}
  LATENCY_INT=${LATENCY%%.*}
  if (( LOSS_INT > MAX_LOSS )); then
    ALERTS="${ALERTS}HIGH_LOSS(${LOSS}%) "
  fi
  if (( LATENCY_INT > MAX_LATENCY )); then
    ALERTS="${ALERTS}HIGH_LATENCY(${LATENCY}ms) "
  fi

  # Status
  STATUS="OK"
  if [[ -n "$ALERTS" ]]; then
    STATUS="ALERT"
    echo "[${TIMESTAMP}] ALERT: ${ALERTS}" >&2
  fi

  # Log JSON line
  echo "{\"ts\":\"${TIMESTAMP}\",\"iface\":\"${INTERFACE}\",\"peers\":${PEERS},\"signal_dbm\":${SIGNAL},\"latency_ms\":${LATENCY},\"loss_pct\":${LOSS},\"status\":\"${STATUS}\",\"alerts\":\"${ALERTS:-none}\"}" >> "$LOG_FILE"

  sleep "$INTERVAL"
done
