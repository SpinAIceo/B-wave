#!/usr/bin/env bash
set -euo pipefail

# B-Wave OTA Update Package Creator
# Creates a signed, integrity-verified update package for distribution.
#
# Usage: ./create-update.sh --version <VER> --changelog <MSG> [--output-dir <DIR>]

VERSION=""
CHANGELOG=""
OUTPUT_DIR="./updates"

while [[ $# -gt 0 ]]; do
    case $1 in
        --version)    VERSION="$2";    shift 2 ;;
        --changelog)  CHANGELOG="$2";  shift 2 ;;
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        *)            echo "Usage: $0 --version <VER> --changelog <MSG>"; exit 1 ;;
    esac
done

[[ -z "$VERSION" ]]   && echo "Error: --version required" && exit 1
[[ -z "$CHANGELOG" ]] && echo "Error: --changelog required" && exit 1

UPDATE_ID="update-${VERSION}"
STAGING_DIR=$(mktemp -d)
PACKAGE_FILE="${OUTPUT_DIR}/${UPDATE_ID}.tar.gz"
MANIFEST_FILE="${OUTPUT_DIR}/${UPDATE_ID}.manifest"

mkdir -p "$OUTPUT_DIR"

echo "Creating update package: ${UPDATE_ID}"
echo "  Version:   ${VERSION}"
echo "  Changelog: ${CHANGELOG}"
echo ""

# ── Collect artifacts ─────────────────────────────────────────────

echo "▶ Collecting Docker image exports..."
mkdir -p "${STAGING_DIR}/images" "${STAGING_DIR}/configs"

# Export current Docker images (if running locally)
for IMAGE in bwave-ai-engine bwave-edge-platform; do
    if docker image inspect "${IMAGE}:latest" >/dev/null 2>&1; then
        echo "  Saving ${IMAGE}..."
        docker save "${IMAGE}:latest" | gzip > "${STAGING_DIR}/images/${IMAGE}.tar.gz"
    else
        echo "  ⚠ ${IMAGE} image not found — skipping"
    fi
done

echo "▶ Collecting configuration updates..."
if [[ -d "../../packages/mesh-network/configs" ]]; then
    cp -r ../../packages/mesh-network/configs/* "${STAGING_DIR}/configs/" 2>/dev/null || true
fi

# Version metadata
cat > "${STAGING_DIR}/update-meta.json" << EOF
{
    "update_id": "${UPDATE_ID}",
    "version": "${VERSION}",
    "changelog": "${CHANGELOG}",
    "created_at": "$(date -Iseconds)",
    "created_by": "$(whoami)@$(hostname)"
}
EOF

# ── Create tarball ────────────────────────────────────────────────

echo "▶ Creating tarball..."
tar czf "$PACKAGE_FILE" -C "$STAGING_DIR" .

# ── Generate manifest ─────────────────────────────────────────────

SIZE_BYTES=$(stat -c%s "$PACKAGE_FILE" 2>/dev/null || stat -f%z "$PACKAGE_FILE" 2>/dev/null || echo "0")
SHA256=$(sha256sum "$PACKAGE_FILE" | awk '{print $1}')

cat > "$MANIFEST_FILE" << EOF
{
    "update_id": "${UPDATE_ID}",
    "version": "${VERSION}",
    "changelog": "${CHANGELOG}",
    "size_bytes": ${SIZE_BYTES},
    "sha256": "${SHA256}",
    "is_critical": false,
    "released_at": "$(date -Iseconds)",
    "files": [
        "${UPDATE_ID}.tar.gz",
        "${UPDATE_ID}.manifest"
    ]
}
EOF

# ── GPG signing (placeholder) ─────────────────────────────────────

echo "▶ Signing package..."
# TODO: Enable when GPG key is configured
# gpg --detach-sign --armor -o "${PACKAGE_FILE}.sig" "$PACKAGE_FILE"
echo "  ⚠ GPG signing skipped (key not configured)"

# ── Cleanup & summary ─────────────────────────────────────────────

rm -rf "$STAGING_DIR"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Update package created successfully                        ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Package:  ${PACKAGE_FILE}"
echo "║  Manifest: ${MANIFEST_FILE}"
echo "║  Size:     ${SIZE_BYTES} bytes"
echo "║  SHA-256:  ${SHA256}"
echo "╚══════════════════════════════════════════════════════════════╝"
