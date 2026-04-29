#!/usr/bin/env bash
# B-Wave 802.11s Mesh Setup Script
# TEMPLATE — customize per vessel before running.
# Tested on Ubuntu Server 22.04 with iw >= 5.19.
set -euo pipefail

MESH_IF="mesh0"
PHY_DEV="phy0"
CONF="../configs/mesh-node.conf"

echo "=== B-Wave Mesh Network Setup ==="

# --- Step 1: Check prerequisites ---
echo "[1/5] Checking prerequisites..."
for cmd in iw ip hostapd dnsmasq brctl; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: '$cmd' not found. Install it before proceeding."
    exit 1
  fi
done
echo "  All tools available."

# --- Step 2: Load configuration ---
echo "[2/5] Loading configuration from $CONF..."
if [ ! -f "$CONF" ]; then
  echo "ERROR: Config file not found at $CONF"
  exit 1
fi
source "$CONF"
echo "  mesh_id=$mesh_id  channel=$channel"

# --- Step 3: Create mesh interface ---
echo "[3/5] Creating mesh interface $MESH_IF..."
# Remove existing mesh interface if present
iw dev "$MESH_IF" del 2>/dev/null || true
# Create new mesh point interface
iw phy "$PHY_DEV" interface add "$MESH_IF" type mesh
ip link set "$MESH_IF" up
echo "  Interface $MESH_IF created."

# --- Step 4: Join mesh network ---
echo "[4/5] Joining mesh network '$mesh_id' on channel $channel..."
iw dev "$MESH_IF" mesh join "$mesh_id" freq "$((5000 + channel * 5))" HT40+
# Set mesh parameters
iw dev "$MESH_IF" set mesh_param mesh_fwding "$mesh_fwding"
iw dev "$MESH_IF" set mesh_param mesh_hwmp_active_path_timeout "$mesh_hwmp_active_path_timeout"
# Set TX power for bulkhead penetration
iw dev "$MESH_IF" set txpower fixed "$((tx_power * 100))"
echo "  Joined mesh '$mesh_id'."

# --- Step 5: Verify ---
echo "[5/5] Verifying mesh status..."
iw dev "$MESH_IF" mesh info
iw dev "$MESH_IF" station dump
echo ""
echo "=== Mesh setup complete ==="
echo "Next: run setup-bridge.sh to bridge mesh to edge server LAN."
