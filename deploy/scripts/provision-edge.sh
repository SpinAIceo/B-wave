#!/usr/bin/env bash
set -euo pipefail

# B-Wave Edge Server Provisioning Script
# Usage: ./provision-edge.sh --vessel-id <ID> --vessel-name <NAME> [--edge-id <ID>]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$DEPLOY_DIR")"
INSTALL_DIR="/opt/bwave"

VESSEL_ID=""
VESSEL_NAME=""
EDGE_SERVER_ID=""

# ── Argument parsing ──────────────────────────────────────────────

usage() {
    echo "Usage: $0 --vessel-id <ID> --vessel-name <NAME> [--edge-id <ID>]"
    echo ""
    echo "Options:"
    echo "  --vessel-id    Unique vessel identifier (e.g., vessel-001)"
    echo "  --vessel-name  Human-readable vessel name (e.g., MV Pacific Star)"
    echo "  --edge-id      Edge server ID (auto-generated if omitted)"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --vessel-id)   VESSEL_ID="$2";   shift 2 ;;
        --vessel-name) VESSEL_NAME="$2"; shift 2 ;;
        --edge-id)     EDGE_SERVER_ID="$2"; shift 2 ;;
        -h|--help)     usage ;;
        *)             echo "Unknown option: $1"; usage ;;
    esac
done

[[ -z "$VESSEL_ID" ]]   && echo "Error: --vessel-id required" && usage
[[ -z "$VESSEL_NAME" ]] && echo "Error: --vessel-name required" && usage
[[ -z "$EDGE_SERVER_ID" ]] && EDGE_SERVER_ID="edge-${VESSEL_ID}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          B-Wave Edge Server Provisioning                    ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Vessel ID:    $VESSEL_ID"
echo "║  Vessel Name:  $VESSEL_NAME"
echo "║  Edge Server:  $EDGE_SERVER_ID"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── Step 1: System requirements check ─────────────────────────────

echo "▶ Step 1/9: Checking system requirements..."

CPU_CORES=$(nproc 2>/dev/null || echo "0")
RAM_MB=$(free -m 2>/dev/null | awk '/^Mem:/ {print $2}' || echo "0")
DISK_GB=$(df -BG / 2>/dev/null | awk 'NR==2 {gsub("G",""); print $4}' || echo "0")

FAIL=0
[[ "$CPU_CORES" -lt 2 ]] && echo "  ✗ CPU: ${CPU_CORES} cores (need ≥2)" && FAIL=1 || echo "  ✓ CPU: ${CPU_CORES} cores"
[[ "$RAM_MB" -lt 3800 ]] && echo "  ✗ RAM: ${RAM_MB}MB (need ≥4096MB)" && FAIL=1 || echo "  ✓ RAM: ${RAM_MB}MB"
[[ "$DISK_GB" -lt 30 ]]  && echo "  ✗ Disk: ${DISK_GB}GB free (need ≥32GB)" && FAIL=1 || echo "  ✓ Disk: ${DISK_GB}GB free"

command -v docker >/dev/null 2>&1 && echo "  ✓ Docker installed" || { echo "  ✗ Docker not found"; FAIL=1; }
docker compose version >/dev/null 2>&1 && echo "  ✓ Docker Compose installed" || { echo "  ✗ Docker Compose not found"; FAIL=1; }

[[ "$FAIL" -ne 0 ]] && echo "" && echo "System requirements not met. Aborting." && exit 1
echo ""

# ── Step 2: Create directory structure ────────────────────────────

echo "▶ Step 2/9: Creating directory structure..."
sudo mkdir -p "${INSTALL_DIR}"/{data,models,certs,configs,backups,logs}
sudo chown -R "$(id -u):$(id -g)" "${INSTALL_DIR}"
echo "  ✓ Created ${INSTALL_DIR}/{data,models,certs,configs,backups,logs}"
echo ""

# ── Step 3: Generate PKI certificates ────────────────────────────

echo "▶ Step 3/9: Generating PKI certificates..."
if [[ -f "${DEPLOY_DIR}/pki/issue-vessel-cert.sh" ]]; then
    bash "${DEPLOY_DIR}/pki/issue-vessel-cert.sh" \
        --vessel-id "$VESSEL_ID" \
        --vessel-name "$VESSEL_NAME" \
        --edge-id "$EDGE_SERVER_ID" \
        --output-dir "${INSTALL_DIR}/certs" \
        || echo "  ⚠ Certificate generation skipped (CA not initialized)"
else
    echo "  ⚠ PKI scripts not found — skipping certificate generation"
fi
echo ""

# ── Step 4: Copy Docker Compose and configs ───────────────────────

echo "▶ Step 4/9: Copying deployment files..."
cp "${DEPLOY_DIR}/edge/docker-compose.yml" "${INSTALL_DIR}/"
cp -r "${PROJECT_ROOT}/packages/mesh-network/configs/" "${INSTALL_DIR}/configs/mesh/" 2>/dev/null || true
echo "  ✓ Docker Compose and configs copied"
echo ""

# ── Step 5: Generate .env file ────────────────────────────────────

echo "▶ Step 5/9: Generating environment configuration..."
cat > "${INSTALL_DIR}/.env" << ENVEOF
BWAVE_VESSEL_ID=${VESSEL_ID}
BWAVE_VESSEL_NAME=${VESSEL_NAME}
BWAVE_EDGE_SERVER_ID=${EDGE_SERVER_ID}
BWAVE_MODEL_PATH=/opt/bwave/models/defect-yolov8.onnx
BWAVE_LOG_LEVEL=INFO
BWAVE_GRPC_PORT=50051
BWAVE_AI_ENGINE_ADDR=ai-engine:50051
BWAVE_DATA_DIR=/opt/bwave/data
BWAVE_CERT_DIR=/opt/bwave/certs
BWAVE_TLS_CERT=/opt/bwave/certs/vessel-${VESSEL_ID}.pem
BWAVE_TLS_KEY=/opt/bwave/certs/vessel-${VESSEL_ID}-key.pem
BWAVE_CA_CERT=/opt/bwave/certs/ca-chain.pem
RUST_LOG=bwave_edge_platform=info
ENVEOF
echo "  ✓ Environment file written to ${INSTALL_DIR}/.env"
echo ""

# ── Step 6: Build Docker images ───────────────────────────────────

echo "▶ Step 6/9: Building Docker images..."
cd "${INSTALL_DIR}"
docker compose build --no-cache 2>&1 | tail -5
echo "  ✓ Docker images built"
echo ""

# ── Step 7: Start services ────────────────────────────────────────

echo "▶ Step 7/9: Starting services..."
docker compose up -d
echo "  ✓ Services started"
echo ""

# ── Step 8: Health checks ─────────────────────────────────────────

echo "▶ Step 8/9: Running health checks..."
sleep 10

check_service() {
    local name=$1
    local container=$2
    if docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null | grep -q healthy; then
        echo "  ✓ ${name}: healthy"
    elif docker inspect --format='{{.State.Running}}' "$container" 2>/dev/null | grep -q true; then
        echo "  ~ ${name}: running (health check pending)"
    else
        echo "  ✗ ${name}: not running"
    fi
}

check_service "AI Engine"      "bwave-ai-engine"
check_service "Edge Platform"  "bwave-edge-platform"
check_service "Mesh Monitor"   "bwave-mesh-monitor"
echo ""

# ── Step 9: Summary ───────────────────────────────────────────────

echo "▶ Step 9/9: Provisioning complete!"
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  B-Wave Edge Server — Provisioning Summary                  ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Vessel:       ${VESSEL_NAME} (${VESSEL_ID})"
echo "║  Edge Server:  ${EDGE_SERVER_ID}"
echo "║  Install Dir:  ${INSTALL_DIR}"
echo "║  gRPC (AI):    localhost:50051"
echo "║  gRPC (Edge):  localhost:50052"
echo "║  HTTP (Edge):  localhost:8080"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Next steps:                                                ║"
echo "║  1. Copy AI model to ${INSTALL_DIR}/models/"
echo "║  2. Configure mesh network APs"
echo "║  3. Install B-Wave app on tablets"
echo "║  4. Run integration test suite"
echo "╚══════════════════════════════════════════════════════════════╝"
