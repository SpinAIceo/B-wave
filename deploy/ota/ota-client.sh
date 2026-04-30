#!/usr/bin/env bash
set -euo pipefail

# B-Wave OTA Update Client
# Runs on the edge server. Checks for updates when satellite link is available,
# downloads, verifies, applies, and rolls back on failure.
#
# Usage: ./ota-client.sh [--check-only] [--force]

INSTALL_DIR="/opt/bwave"
BACKUP_DIR="${INSTALL_DIR}/backups"
OTA_SERVER="${BWAVE_OTA_SERVER:-https://ota.bwave.spinai.com}"
VESSEL_ID="${BWAVE_VESSEL_ID:-unknown}"
EDGE_SERVER_ID="${BWAVE_EDGE_SERVER_ID:-unknown}"
CURRENT_VERSION="${BWAVE_VERSION:-0.1.0}"
HEALTH_CHECK_TIMEOUT=300  # 5 minutes
CHECK_ONLY=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --check-only) CHECK_ONLY=true; shift ;;
        --force)      FORCE=true; shift ;;
        *)            echo "Unknown option: $1"; exit 1 ;;
    esac
done

log() { echo "[$(date -Iseconds)] OTA: $*"; }

# ── Step 1: Check connectivity ────────────────────────────────────

log "Checking satellite link to OTA server..."
if ! curl -sf --connect-timeout 10 "${OTA_SERVER}/health" >/dev/null 2>&1; then
    log "OTA server unreachable. Satellite link may be down. Exiting."
    exit 0
fi
log "Satellite link available."

# ── Step 2: Check for updates ─────────────────────────────────────

log "Checking for updates (current: v${CURRENT_VERSION})..."
RESPONSE=$(curl -sf "${OTA_SERVER}/api/v1/updates/check?vessel_id=${VESSEL_ID}&current_version=${CURRENT_VERSION}")

UPDATE_COUNT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['updates_available'])" 2>/dev/null || echo "0")

if [[ "$UPDATE_COUNT" -eq 0 ]]; then
    log "No updates available. System is up to date."
    exit 0
fi

UPDATE_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['updates'][0]['update_id'])")
NEW_VERSION=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['updates'][0]['version'])")
EXPECTED_SHA=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['updates'][0]['sha256'])")
IS_CRITICAL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['updates'][0]['is_critical'])")

log "Update available: ${UPDATE_ID} (v${CURRENT_VERSION} → v${NEW_VERSION})"
[[ "$IS_CRITICAL" == "True" ]] && log "⚠ This is a CRITICAL update"

if [[ "$CHECK_ONLY" == "true" ]]; then
    log "Check-only mode. Exiting."
    exit 0
fi

# ── Step 3: Download update package ───────────────────────────────

log "Downloading update package..."
DOWNLOAD_DIR=$(mktemp -d)
PACKAGE_FILE="${DOWNLOAD_DIR}/${UPDATE_ID}.tar.gz"

curl -sf -o "$PACKAGE_FILE" "${OTA_SERVER}/api/v1/updates/download/${UPDATE_ID}" || {
    log "Download failed. Aborting."
    rm -rf "$DOWNLOAD_DIR"
    exit 1
}

# ── Step 4: Verify integrity ──────────────────────────────────────

log "Verifying package integrity..."
ACTUAL_SHA=$(sha256sum "$PACKAGE_FILE" | awk '{print $1}')
if [[ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]]; then
    log "SHA-256 mismatch! Expected: ${EXPECTED_SHA}, Got: ${ACTUAL_SHA}"
    log "Package may be corrupted. Aborting."
    rm -rf "$DOWNLOAD_DIR"
    curl -sf -X POST "${OTA_SERVER}/api/v1/updates/report" \
        -H "Content-Type: application/json" \
        -d "{\"vessel_id\":\"${VESSEL_ID}\",\"edge_server_id\":\"${EDGE_SERVER_ID}\",\"update_id\":\"${UPDATE_ID}\",\"status\":\"FAILED\",\"error_message\":\"SHA-256 mismatch\"}" \
        >/dev/null 2>&1 || true
    exit 1
fi
log "Integrity verified (SHA-256 match)."

# ── Step 4b: Verify GPG signature (mandatory) ────────────────────

SIGNATURE_FILE="${PACKAGE_FILE}.sig"
curl -sf -o "$SIGNATURE_FILE" "${OTA_SERVER}/api/v1/updates/download/${UPDATE_ID}.sig" || {
    log "CRITICAL: Signature file download failed. Rejecting update."
    rm -rf "$DOWNLOAD_DIR"
    curl -sf -X POST "${OTA_SERVER}/api/v1/updates/report" \
        -H "Content-Type: application/json" \
        -d "{\"vessel_id\":\"${VESSEL_ID}\",\"edge_server_id\":\"${EDGE_SERVER_ID}\",\"update_id\":\"${UPDATE_ID}\",\"status\":\"FAILED\",\"error_message\":\"Signature download failed\"}" \
        >/dev/null 2>&1 || true
    exit 1
}

GPG_KEYRING="${INSTALL_DIR}/certs/bwave-release.gpg"
if [[ ! -f "$GPG_KEYRING" ]]; then
    log "CRITICAL: GPG release keyring not found at ${GPG_KEYRING}. Cannot verify update."
    rm -rf "$DOWNLOAD_DIR"
    exit 1
fi

gpg --no-default-keyring --keyring "$GPG_KEYRING" --verify "$SIGNATURE_FILE" "$PACKAGE_FILE" 2>/dev/null || {
    log "CRITICAL: GPG signature verification FAILED. Update rejected — possible tampering."
    rm -rf "$DOWNLOAD_DIR"
    curl -sf -X POST "${OTA_SERVER}/api/v1/updates/report" \
        -H "Content-Type: application/json" \
        -d "{\"vessel_id\":\"${VESSEL_ID}\",\"edge_server_id\":\"${EDGE_SERVER_ID}\",\"update_id\":\"${UPDATE_ID}\",\"status\":\"FAILED\",\"error_message\":\"GPG signature verification failed\"}" \
        >/dev/null 2>&1 || true
    exit 1
}
log "GPG signature verified."

# ── Step 5: Create backup ─────────────────────────────────────────

log "Creating backup of current version..."
BACKUP_TAG="v${CURRENT_VERSION}-$(date +%Y%m%d%H%M%S)"
mkdir -p "${BACKUP_DIR}"

cd "${INSTALL_DIR}"
docker compose config > "${BACKUP_DIR}/docker-compose.${BACKUP_TAG}.yml" 2>/dev/null || true
cp .env "${BACKUP_DIR}/.env.${BACKUP_TAG}" 2>/dev/null || true

RUNNING_IMAGES=$(docker compose images -q 2>/dev/null || true)
if [[ -n "$RUNNING_IMAGES" ]]; then
    echo "$RUNNING_IMAGES" > "${BACKUP_DIR}/images.${BACKUP_TAG}.txt"
fi
log "Backup created: ${BACKUP_TAG}"

# ── Step 6: Apply update ──────────────────────────────────────────

log "Applying update ${UPDATE_ID}..."
cd "${INSTALL_DIR}"
tar xzf "$PACKAGE_FILE" -C "${INSTALL_DIR}/" 2>/dev/null || {
    log "Failed to extract update package."
    rm -rf "$DOWNLOAD_DIR"
    exit 1
}

docker compose pull 2>/dev/null || true
docker compose up -d
log "Services restarted with new version."

# ── Step 7: Health check (with rollback) ──────────────────────────

log "Waiting for services to become healthy (timeout: ${HEALTH_CHECK_TIMEOUT}s)..."
HEALTHY=false
ELAPSED=0
INTERVAL=15

while [[ $ELAPSED -lt $HEALTH_CHECK_TIMEOUT ]]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))

    ALL_HEALTHY=true
    for SVC in bwave-ai-engine bwave-edge-platform; do
        STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$SVC" 2>/dev/null || echo "missing")
        if [[ "$STATUS" != "healthy" ]]; then
            ALL_HEALTHY=false
            break
        fi
    done

    if [[ "$ALL_HEALTHY" == "true" ]]; then
        HEALTHY=true
        break
    fi
    log "  Health check: waiting... (${ELAPSED}s/${HEALTH_CHECK_TIMEOUT}s)"
done

if [[ "$HEALTHY" == "true" ]]; then
    log "All services healthy. Update successful!"
    STATUS="SUCCESS"
else
    log "⚠ Health check failed after ${HEALTH_CHECK_TIMEOUT}s. Rolling back..."

    # Rollback
    if [[ -f "${BACKUP_DIR}/docker-compose.${BACKUP_TAG}.yml" ]]; then
        cp "${BACKUP_DIR}/docker-compose.${BACKUP_TAG}.yml" "${INSTALL_DIR}/docker-compose.yml"
        cp "${BACKUP_DIR}/.env.${BACKUP_TAG}" "${INSTALL_DIR}/.env" 2>/dev/null || true
        docker compose up -d
        log "Rollback complete. Reverted to v${CURRENT_VERSION}."
    else
        log "⚠ No backup found. Manual intervention required."
    fi
    STATUS="ROLLED_BACK"
fi

# ── Step 8: Report to shore ───────────────────────────────────────

log "Reporting update status to shore server..."
curl -sf -X POST "${OTA_SERVER}/api/v1/updates/report" \
    -H "Content-Type: application/json" \
    -d "{\"vessel_id\":\"${VESSEL_ID}\",\"edge_server_id\":\"${EDGE_SERVER_ID}\",\"update_id\":\"${UPDATE_ID}\",\"status\":\"${STATUS}\",\"applied_at\":\"$(date -Iseconds)\"}" \
    >/dev/null 2>&1 || log "Failed to report status (satellite may be down)"

rm -rf "$DOWNLOAD_DIR"
log "OTA update process complete. Status: ${STATUS}"
