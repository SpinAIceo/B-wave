#!/usr/bin/env bash
set -euo pipefail

# B-Wave PKI — Revoke Certificate
# Revokes a compromised or decommissioned certificate and updates the CRL.
#
# Usage: ./revoke-cert.sh --cert <PATH_TO_CERT>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CA_DIR="${SCRIPT_DIR}/ca"
OPENSSL_CNF="${SCRIPT_DIR}/openssl.cnf"
CERT_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --cert) CERT_PATH="$2"; shift 2 ;;
        *)      echo "Usage: $0 --cert <PATH_TO_CERT>"; exit 1 ;;
    esac
done

[[ -z "$CERT_PATH" ]] && echo "Error: --cert required" && exit 1
[[ ! -f "$CERT_PATH" ]] && echo "Error: Certificate not found: ${CERT_PATH}" && exit 1

# Show certificate details before revoking
echo "Certificate to revoke:"
openssl x509 -in "$CERT_PATH" -noout -subject -serial -dates
echo ""

read -p "Are you sure you want to revoke this certificate? [y/N] " -r
[[ ! $REPLY =~ ^[Yy]$ ]] && echo "Aborted." && exit 0

# ── Revoke ────────────────────────────────────────────────────────

echo "▶ Revoking certificate..."
openssl ca -config "$OPENSSL_CNF" \
    -revoke "$CERT_PATH" \
    -cert "${CA_DIR}/certs/ca-intermediate.pem" \
    -keyfile "${CA_DIR}/private/ca-intermediate-key.pem" \
    -batch

# ── Update CRL ────────────────────────────────────────────────────

echo "▶ Updating Certificate Revocation List..."
openssl ca -config "$OPENSSL_CNF" \
    -gencrl -out "${CA_DIR}/crl/crl.pem" \
    -cert "${CA_DIR}/certs/ca-intermediate.pem" \
    -keyfile "${CA_DIR}/private/ca-intermediate-key.pem"

echo ""
echo "  ✓ Certificate revoked"
echo "  ✓ CRL updated: ${CA_DIR}/crl/crl.pem"
echo ""
echo "  Distribute the updated CRL to all edge servers."
