#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_ENGINE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${AI_ENGINE_DIR}/../.." && pwd)"
CONFIG_PATH="${AI_ENGINE_DIR}/configs/train_next_best.yaml"

if [[ -f "${REPO_ROOT}/.venv/bin/activate" ]]; then
  source "${REPO_ROOT}/.venv/bin/activate"
elif [[ -f "${AI_ENGINE_DIR}/.venv/bin/activate" ]]; then
  source "${AI_ENGINE_DIR}/.venv/bin/activate"
elif [[ -f "${REPO_ROOT}/.venv/Scripts/activate" ]]; then
  source "${REPO_ROOT}/.venv/Scripts/activate"
elif [[ -f "${AI_ENGINE_DIR}/.venv/Scripts/activate" ]]; then
  source "${AI_ENGINE_DIR}/.venv/Scripts/activate"
else
  echo "No virtual environment found under repo root or packages/ai-engine." >&2
  exit 1
fi

if [[ -z "${DATA_YAML:-}" ]]; then
  if [[ -f "${REPO_ROOT}/data.yaml" ]]; then
    DATA_YAML="${REPO_ROOT}/data.yaml"
  elif [[ -f "${AI_ENGINE_DIR}/data.yaml" ]]; then
    DATA_YAML="${AI_ENGINE_DIR}/data.yaml"
  else
    DATA_YAML="$(find "${REPO_ROOT}" -path '*/.venv' -prune -o -name data.yaml -print -quit)"
  fi
fi

if [[ -z "${DATA_YAML}" || ! -f "${DATA_YAML}" ]]; then
  echo "Could not find data.yaml. Set DATA_YAML=/path/to/data.yaml and rerun." >&2
  exit 1
fi

mkdir -p "${REPO_ROOT}/runs/next_best"
cd "${REPO_ROOT}"

yolo detect train cfg="${CONFIG_PATH}" data="${DATA_YAML}" project="runs/next_best"
