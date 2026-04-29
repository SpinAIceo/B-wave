#!/usr/bin/env bash
set -euo pipefail

PROTO_DIR="shared/proto"
OUT_PYTHON="shared/gen/python"
OUT_DART="shared/gen/dart"

mkdir -p "$OUT_PYTHON" "$OUT_DART"

echo "=== Generating Python gRPC stubs ==="
python -m grpc_tools.protoc \
  -I"$PROTO_DIR" \
  --python_out="$OUT_PYTHON" \
  --grpc_python_out="$OUT_PYTHON" \
  --pyi_out="$OUT_PYTHON" \
  "$PROTO_DIR"/bwave/v1/*.proto

echo "=== Proto compilation successful ==="
echo "Python stubs: $OUT_PYTHON/"
