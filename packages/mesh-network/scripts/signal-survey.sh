#!/usr/bin/env bash
set -euo pipefail

# B-Wave RF Signal Survey Tool
# Records Wi-Fi signal strength at labeled locations for mesh deployment planning.
# Requires: iw
# Usage: ./signal-survey.sh --location "Engine Room Aft" [--interface mesh0] [--output survey.csv]

INTERFACE="mesh0"
LOCATION=""
OUTPUT="survey.csv"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --location)  LOCATION="$2"; shift 2 ;;
    --interface) INTERFACE="$2"; shift 2 ;;
    --output)    OUTPUT="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 --location <label> [--interface mesh0] [--output survey.csv]"
      exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$LOCATION" ]]; then
  echo "ERROR: --location is required (e.g. --location 'Engine Room Aft')"
  exit 1
fi

if ! command -v iw &>/dev/null; then
  echo "ERROR: iw not found. Install with: apt install iw"
  exit 1
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Gather station info
STATION_DUMP=$(iw dev "$INTERFACE" station dump 2>/dev/null || echo "")
LINK_INFO=$(iw dev "$INTERFACE" link 2>/dev/null || echo "")
SURVEY_INFO=$(iw dev "$INTERFACE" survey dump 2>/dev/null || echo "")

# Parse signal strength (RSSI)
SIGNAL_DBM=$(echo "$STATION_DUMP" | grep -oP 'signal:\s+\K-?[0-9]+' | head -1 || echo "N/A")

# Parse noise floor from survey
NOISE_DBM=$(echo "$SURVEY_INFO" | grep -oP 'noise:\s+\K-?[0-9]+' | head -1 || echo "N/A")

# Compute SNR
if [[ "$SIGNAL_DBM" != "N/A" && "$NOISE_DBM" != "N/A" ]]; then
  SNR=$((SIGNAL_DBM - NOISE_DBM))
else
  SNR="N/A"
fi

# Link quality (tx bitrate as proxy)
TX_BITRATE=$(echo "$STATION_DUMP" | grep -oP 'tx bitrate:\s+\K[0-9.]+' | head -1 || echo "N/A")

# Connected peers
PEER_COUNT=$(echo "$STATION_DUMP" | grep -c "Station" || echo "0")

# Quality assessment
QUALITY="UNKNOWN"
if [[ "$SIGNAL_DBM" != "N/A" ]]; then
  if (( SIGNAL_DBM >= -50 )); then
    QUALITY="EXCELLENT"
  elif (( SIGNAL_DBM >= -65 )); then
    QUALITY="GOOD"
  elif (( SIGNAL_DBM >= -75 )); then
    QUALITY="FAIR"
  else
    QUALITY="POOR"
  fi
fi

# Print results
echo "=== B-Wave Signal Survey ==="
echo "Location:     $LOCATION"
echo "Interface:    $INTERFACE"
echo "Timestamp:    $TIMESTAMP"
echo "Signal:       ${SIGNAL_DBM} dBm"
echo "Noise Floor:  ${NOISE_DBM} dBm"
echo "SNR:          ${SNR} dB"
echo "TX Bitrate:   ${TX_BITRATE} Mbps"
echo "Mesh Peers:   ${PEER_COUNT}"
echo "Quality:      $QUALITY"

# Write CSV header if file doesn't exist
if [[ ! -f "$OUTPUT" ]]; then
  echo "timestamp,location,signal_dbm,noise_dbm,snr_db,tx_bitrate_mbps,peer_count,quality" > "$OUTPUT"
fi

# Append row
echo "${TIMESTAMP},\"${LOCATION}\",${SIGNAL_DBM},${NOISE_DBM},${SNR},${TX_BITRATE},${PEER_COUNT},${QUALITY}" >> "$OUTPUT"
echo ""
echo "Appended to $OUTPUT"
