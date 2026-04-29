#!/usr/bin/env bash
set -euo pipefail

# B-Wave PKI — Initialize Certificate Authority
# Creates a root CA and an intermediate CA for issuing vessel/tablet certificates.
#
# Usage: ./init-ca.sh [--output-dir <DIR>]
# Idempotent: skips if CA already exists.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${1:-${SCRIPT_DIR}/ca}"
OPENSSL_CNF="${SCRIPT_DIR}/openssl.cnf"
KEY_ALGO="rsa"
KEY_SIZE=4096
DAYS_ROOT=7300       # 20 years
DAYS_INTERMEDIATE=3650  # 10 years

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  B-Wave PKI — Certificate Authority Initialization          ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# ── Create directory structure ────────────────────────────────────

mkdir -p "${OUTPUT_DIR}"/{certs,crl,newcerts,private,csr}
chmod 700 "${OUTPUT_DIR}/private"

if [[ ! -f "${OUTPUT_DIR}/index.txt" ]]; then
    touch "${OUTPUT_DIR}/index.txt"
fi
if [[ ! -f "${OUTPUT_DIR}/serial" ]]; then
    echo 1000 > "${OUTPUT_DIR}/serial"
fi
if [[ ! -f "${OUTPUT_DIR}/crlnumber" ]]; then
    echo 1000 > "${OUTPUT_DIR}/crlnumber"
fi

# ── Root CA ───────────────────────────────────────────────────────

if [[ -f "${OUTPUT_DIR}/private/ca-root-key.pem" ]]; then
    echo "Root CA already exists. Skipping."
else
    echo "▶ Generating Root CA key (${KEY_ALGO} ${KEY_SIZE})..."
    openssl genrsa -out "${OUTPUT_DIR}/private/ca-root-key.pem" "$KEY_SIZE"
    chmod 400 "${OUTPUT_DIR}/private/ca-root-key.pem"

    echo "▶ Generating Root CA certificate (valid ${DAYS_ROOT} days)..."
    openssl req -config "$OPENSSL_CNF" \
        -key "${OUTPUT_DIR}/private/ca-root-key.pem" \
        -new -x509 -days "$DAYS_ROOT" -sha384 \
        -extensions v3_ca \
        -out "${OUTPUT_DIR}/certs/ca-root.pem" \
        -subj "/C=KR/ST=Gyeonggi-do/L=Seongnam/O=Spinai Co., Ltd./OU=B-Wave Maritime Security/CN=B-Wave Root CA"

    echo "  ✓ Root CA created: ${OUTPUT_DIR}/certs/ca-root.pem"
fi

# ── Intermediate CA ───────────────────────────────────────────────

if [[ -f "${OUTPUT_DIR}/private/ca-intermediate-key.pem" ]]; then
    echo "Intermediate CA already exists. Skipping."
else
    echo "▶ Generating Intermediate CA key..."
    openssl genrsa -out "${OUTPUT_DIR}/private/ca-intermediate-key.pem" "$KEY_SIZE"
    chmod 400 "${OUTPUT_DIR}/private/ca-intermediate-key.pem"

    echo "▶ Creating Intermediate CA CSR..."
    openssl req -config "$OPENSSL_CNF" \
        -new -sha384 \
        -key "${OUTPUT_DIR}/private/ca-intermediate-key.pem" \
        -out "${OUTPUT_DIR}/csr/ca-intermediate.csr.pem" \
        -subj "/C=KR/ST=Gyeonggi-do/L=Seongnam/O=Spinai Co., Ltd./OU=B-Wave Maritime Security/CN=B-Wave Intermediate CA"

    echo "▶ Signing Intermediate CA with Root CA (valid ${DAYS_INTERMEDIATE} days)..."
    openssl ca -config "$OPENSSL_CNF" \
        -extensions v3_intermediate_ca \
        -days "$DAYS_INTERMEDIATE" -notext -md sha384 \
        -in "${OUTPUT_DIR}/csr/ca-intermediate.csr.pem" \
        -out "${OUTPUT_DIR}/certs/ca-intermediate.pem" \
        -cert "${OUTPUT_DIR}/certs/ca-root.pem" \
        -keyfile "${OUTPUT_DIR}/private/ca-root-key.pem" \
        -batch

    echo "  ✓ Intermediate CA created: ${OUTPUT_DIR}/certs/ca-intermediate.pem"

    # Create certificate chain
    cat "${OUTPUT_DIR}/certs/ca-intermediate.pem" \
        "${OUTPUT_DIR}/certs/ca-root.pem" \
        > "${OUTPUT_DIR}/certs/ca-chain.pem"
    echo "  ✓ CA chain: ${OUTPUT_DIR}/certs/ca-chain.pem"
fi

# ── Initial CRL ───────────────────────────────────────────────────

if [[ ! -f "${OUTPUT_DIR}/crl/crl.pem" ]]; then
    echo "▶ Generating initial CRL..."
    openssl ca -config "$OPENSSL_CNF" \
        -gencrl -out "${OUTPUT_DIR}/crl/crl.pem" \
        -cert "${OUTPUT_DIR}/certs/ca-intermediate.pem" \
        -keyfile "${OUTPUT_DIR}/private/ca-intermediate-key.pem" \
        2>/dev/null || echo "  ⚠ CRL generation skipped (CA database not ready)"
fi

echo ""
echo "PKI initialization complete."
echo "  Root CA:         ${OUTPUT_DIR}/certs/ca-root.pem"
echo "  Intermediate CA: ${OUTPUT_DIR}/certs/ca-intermediate.pem"
echo "  CA Chain:        ${OUTPUT_DIR}/certs/ca-chain.pem"
echo "  Root Key:        ${OUTPUT_DIR}/private/ca-root-key.pem (PROTECT THIS)"
