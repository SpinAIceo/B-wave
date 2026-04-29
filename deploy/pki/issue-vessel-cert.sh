#!/usr/bin/env bash
set -euo pipefail

# B-Wave PKI — Issue Vessel Edge Server Certificate
# Creates a server certificate for mTLS between edge server and tablets.
#
# Usage: ./issue-vessel-cert.sh --vessel-id <ID> --vessel-name <NAME> --edge-id <ID> [--output-dir <DIR>]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CA_DIR="${SCRIPT_DIR}/ca"
OPENSSL_CNF="${SCRIPT_DIR}/openssl.cnf"
OUTPUT_DIR=""
VESSEL_ID=""
VESSEL_NAME=""
EDGE_ID=""
DAYS=825  # ~2.25 years (Apple/browser limit)

while [[ $# -gt 0 ]]; do
    case $1 in
        --vessel-id)   VESSEL_ID="$2";   shift 2 ;;
        --vessel-name) VESSEL_NAME="$2"; shift 2 ;;
        --edge-id)     EDGE_ID="$2";     shift 2 ;;
        --output-dir)  OUTPUT_DIR="$2";  shift 2 ;;
        *)             echo "Usage: $0 --vessel-id <ID> --vessel-name <NAME> --edge-id <ID>"; exit 1 ;;
    esac
done

[[ -z "$VESSEL_ID" ]]   && echo "Error: --vessel-id required" && exit 1
[[ -z "$VESSEL_NAME" ]] && echo "Error: --vessel-name required" && exit 1
[[ -z "$EDGE_ID" ]]     && EDGE_ID="edge-${VESSEL_ID}"
[[ -z "$OUTPUT_DIR" ]]  && OUTPUT_DIR="${CA_DIR}/issued/vessels/${VESSEL_ID}"

echo "Issuing vessel certificate: ${VESSEL_ID} (${VESSEL_NAME})"

mkdir -p "$OUTPUT_DIR"

# ── Generate key ──────────────────────────────────────────────────

KEY_FILE="${OUTPUT_DIR}/vessel-${VESSEL_ID}-key.pem"
CSR_FILE="${OUTPUT_DIR}/vessel-${VESSEL_ID}.csr"
CERT_FILE="${OUTPUT_DIR}/vessel-${VESSEL_ID}.pem"
CHAIN_FILE="${OUTPUT_DIR}/vessel-${VESSEL_ID}-chain.pem"

openssl genrsa -out "$KEY_FILE" 2048
chmod 400 "$KEY_FILE"

# ── Create CSR with SAN ──────────────────────────────────────────

SAN_CNF=$(mktemp)
cat > "$SAN_CNF" << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha384
distinguished_name = dn
req_extensions = v3_req

[dn]
C  = KR
ST = Gyeonggi-do
O  = Spinai Co., Ltd.
OU = B-Wave Vessel Fleet
CN = edge.${VESSEL_ID}.bwave.local

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = edge.${VESSEL_ID}.bwave.local
DNS.2 = ${EDGE_ID}.bwave.local
DNS.3 = localhost
IP.1  = 192.168.1.1
IP.2  = 127.0.0.1
EOF

openssl req -new -key "$KEY_FILE" -out "$CSR_FILE" -config "$SAN_CNF"

# ── Sign with intermediate CA ─────────────────────────────────────

openssl x509 -req \
    -in "$CSR_FILE" \
    -CA "${CA_DIR}/certs/ca-intermediate.pem" \
    -CAkey "${CA_DIR}/private/ca-intermediate-key.pem" \
    -CAcreateserial \
    -out "$CERT_FILE" \
    -days "$DAYS" \
    -sha384 \
    -extfile "$SAN_CNF" \
    -extensions v3_req

# ── Create full chain ─────────────────────────────────────────────

cat "$CERT_FILE" \
    "${CA_DIR}/certs/ca-intermediate.pem" \
    "${CA_DIR}/certs/ca-root.pem" \
    > "$CHAIN_FILE"

# ── Cleanup ───────────────────────────────────────────────────────

rm -f "$SAN_CNF" "$CSR_FILE"

echo "  ✓ Certificate: ${CERT_FILE}"
echo "  ✓ Private Key: ${KEY_FILE}"
echo "  ✓ Full Chain:  ${CHAIN_FILE}"
echo "  SAN: edge.${VESSEL_ID}.bwave.local, ${EDGE_ID}.bwave.local, 192.168.1.1"
echo "  Valid: ${DAYS} days"
