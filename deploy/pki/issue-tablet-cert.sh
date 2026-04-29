#!/usr/bin/env bash
set -euo pipefail

# B-Wave PKI — Issue Tablet Client Certificate
# Creates a client certificate for BYOD tablet mTLS authentication.
# Outputs PKCS#12 (.p12) for easy import on Android/iOS.
#
# Usage: ./issue-tablet-cert.sh --device-id <ID> --crew-id <ID> --role <ROLE>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CA_DIR="${SCRIPT_DIR}/ca"
OUTPUT_DIR=""
DEVICE_ID=""
CREW_ID=""
ROLE=""
DAYS=365
P12_PASSWORD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --device-id)  DEVICE_ID="$2";    shift 2 ;;
        --crew-id)    CREW_ID="$2";      shift 2 ;;
        --role)       ROLE="$2";         shift 2 ;;
        --output-dir) OUTPUT_DIR="$2";   shift 2 ;;
        --password)   P12_PASSWORD="$2"; shift 2 ;;
        *)            echo "Usage: $0 --device-id <ID> --crew-id <ID> --role <ROLE>"; exit 1 ;;
    esac
done

[[ -z "$DEVICE_ID" ]] && echo "Error: --device-id required" && exit 1
[[ -z "$CREW_ID" ]]   && echo "Error: --crew-id required" && exit 1
[[ -z "$ROLE" ]]       && echo "Error: --role required (Captain|ChiefEngineer|Officer|Crew|ReadOnly)" && exit 1
[[ -z "$OUTPUT_DIR" ]] && OUTPUT_DIR="${CA_DIR}/issued/tablets/${DEVICE_ID}"
[[ -z "$P12_PASSWORD" ]] && P12_PASSWORD=$(openssl rand -hex 16)

case "$ROLE" in
    Captain|ChiefEngineer|Officer|Crew|ReadOnly) ;;
    *) echo "Error: Invalid role. Must be Captain|ChiefEngineer|Officer|Crew|ReadOnly"; exit 1 ;;
esac

echo "Issuing tablet client certificate:"
echo "  Device:   ${DEVICE_ID}"
echo "  Crew:     ${CREW_ID}"
echo "  Role:     ${ROLE}"

mkdir -p "$OUTPUT_DIR"

KEY_FILE="${OUTPUT_DIR}/tablet-${DEVICE_ID}-key.pem"
CSR_FILE="${OUTPUT_DIR}/tablet-${DEVICE_ID}.csr"
CERT_FILE="${OUTPUT_DIR}/tablet-${DEVICE_ID}.pem"
P12_FILE="${OUTPUT_DIR}/tablet-${DEVICE_ID}.p12"

# ── Generate key ──────────────────────────────────────────────────

openssl genrsa -out "$KEY_FILE" 2048
chmod 400 "$KEY_FILE"

# ── Create CSR ────────────────────────────────────────────────────

openssl req -new -key "$KEY_FILE" -out "$CSR_FILE" \
    -subj "/C=KR/O=Spinai Co., Ltd./OU=B-Wave Crew/${ROLE}/CN=${CREW_ID}@${DEVICE_ID}"

# ── Sign with intermediate CA ─────────────────────────────────────

CLIENT_EXT=$(mktemp)
cat > "$CLIENT_EXT" << EOF
basicConstraints       = CA:FALSE
nsCertType             = client
nsComment              = "B-Wave Tablet - ${CREW_ID} (${ROLE})"
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid,issuer:always
keyUsage               = critical,digitalSignature
extendedKeyUsage       = clientAuth
EOF

openssl x509 -req \
    -in "$CSR_FILE" \
    -CA "${CA_DIR}/certs/ca-intermediate.pem" \
    -CAkey "${CA_DIR}/private/ca-intermediate-key.pem" \
    -CAcreateserial \
    -out "$CERT_FILE" \
    -days "$DAYS" \
    -sha384 \
    -extfile "$CLIENT_EXT"

# ── Create PKCS#12 for mobile import ──────────────────────────────

openssl pkcs12 -export \
    -out "$P12_FILE" \
    -inkey "$KEY_FILE" \
    -in "$CERT_FILE" \
    -certfile "${CA_DIR}/certs/ca-chain.pem" \
    -name "B-Wave ${CREW_ID}" \
    -passout "pass:${P12_PASSWORD}"

# ── Cleanup ───────────────────────────────────────────────────────

rm -f "$CSR_FILE" "$CLIENT_EXT"

echo ""
echo "  ✓ Certificate: ${CERT_FILE}"
echo "  ✓ PKCS#12:     ${P12_FILE}"
echo "  ✓ Password:    ${P12_PASSWORD}"
echo "  ✓ Role:        ${ROLE}"
echo "  ✓ Valid:        ${DAYS} days"
echo ""
echo "  Import ${P12_FILE} on the tablet with the password above."
