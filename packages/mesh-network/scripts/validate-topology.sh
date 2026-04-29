#!/usr/bin/env bash
set -euo pipefail

# B-Wave Mesh Topology Validator
# Validates that the mesh network is correctly configured and operational.
# Usage: ./validate-topology.sh [--mesh-id bwave-vessel] [--edge-ip 192.168.1.1] [--interface mesh0]

MESH_ID="bwave-vessel"
EDGE_IP="192.168.1.1"
INTERFACE="mesh0"
GRPC_PORT=50051
PASS=0
FAIL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mesh-id)   MESH_ID="$2"; shift 2 ;;
    --edge-ip)   EDGE_IP="$2"; shift 2 ;;
    --interface) INTERFACE="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--mesh-id bwave-vessel] [--edge-ip 192.168.1.1] [--interface mesh0]"
      exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

check() {
  local name="$1"
  local result="$2"  # "PASS" or "FAIL"
  local detail="$3"
  if [[ "$result" == "PASS" ]]; then
    printf "  [PASS] %-40s %s\n" "$name" "$detail"
    ((PASS++))
  else
    printf "  [FAIL] %-40s %s\n" "$name" "$detail"
    ((FAIL++))
  fi
}

echo "=== B-Wave Mesh Topology Validation ==="
echo "Expected: mesh_id=$MESH_ID  edge=$EDGE_IP  iface=$INTERFACE"
echo ""

# 1. Interface exists and is up
if ip link show "$INTERFACE" &>/dev/null; then
  STATE=$(ip link show "$INTERFACE" | grep -oP 'state \K\w+')
  if [[ "$STATE" == "UP" ]]; then
    check "Interface $INTERFACE is UP" "PASS" "state=$STATE"
  else
    check "Interface $INTERFACE is UP" "FAIL" "state=$STATE"
  fi
else
  check "Interface $INTERFACE exists" "FAIL" "not found"
fi

# 2. Mesh ID matches
ACTUAL_MESH_ID=$(iw dev "$INTERFACE" info 2>/dev/null | grep -oP 'mesh id \K.*' || echo "")
if [[ "$ACTUAL_MESH_ID" == "$MESH_ID" ]]; then
  check "Mesh ID matches" "PASS" "id=$ACTUAL_MESH_ID"
else
  check "Mesh ID matches" "FAIL" "expected=$MESH_ID got=$ACTUAL_MESH_ID"
fi

# 3. Encryption enabled (SAE/WPA3)
MESH_INFO=$(iw dev "$INTERFACE" info 2>/dev/null || echo "")
if echo "$MESH_INFO" | grep -qi "SAE\|WPA3\|security"; then
  check "Encryption (SAE/WPA3)" "PASS" "secured"
else
  check "Encryption (SAE/WPA3)" "FAIL" "not detected in iw info"
fi

# 4. Peer connections
PEER_COUNT=$(iw dev "$INTERFACE" station dump 2>/dev/null | grep -c "Station" || echo "0")
if (( PEER_COUNT > 0 )); then
  check "Mesh peers connected" "PASS" "peers=$PEER_COUNT"
else
  check "Mesh peers connected" "FAIL" "no peers"
fi

# 5. Edge server reachable
if ping -c 3 -W 2 "$EDGE_IP" &>/dev/null; then
  check "Edge server reachable (ping)" "PASS" "$EDGE_IP"
else
  check "Edge server reachable (ping)" "FAIL" "$EDGE_IP unreachable"
fi

# 6. DNS resolution (edge server hostname)
if getent hosts edge-server.bwave.local &>/dev/null; then
  check "DNS resolution" "PASS" "edge-server.bwave.local"
else
  check "DNS resolution" "FAIL" "edge-server.bwave.local not resolved (may use IP directly)"
fi

# 7. gRPC port connectivity
if timeout 3 bash -c "echo >/dev/tcp/$EDGE_IP/$GRPC_PORT" 2>/dev/null; then
  check "gRPC port ($GRPC_PORT)" "PASS" "port open"
else
  check "gRPC port ($GRPC_PORT)" "FAIL" "port $GRPC_PORT closed on $EDGE_IP"
fi

# Summary
echo ""
TOTAL=$((PASS + FAIL))
echo "=== $PASS/$TOTAL checks passed ==="
if (( FAIL > 0 )); then
  echo "STATUS: FAIL — $FAIL issue(s) require attention"
  exit 1
else
  echo "STATUS: ALL PASS"
  exit 0
fi
