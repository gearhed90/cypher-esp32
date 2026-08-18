#!/bin/bash
# Cypher robot: NetworkManager station profile to join cyberdeck AP "Cypher-Deck"
# Usage:
#   export CYPHER_DECK_PSK='your-password-here'
#   sudo bash setup-cypher-deck-station.sh

set -euo pipefail

SSID="${CYPHER_DECK_SSID:-Cypher-Deck}"
PSK="${CYPHER_DECK_PSK:-}"
IFACE="${CYPHER_WIFI_IFACE:-wlan0}"
CON_NAME="Cypher-Deck"
PRIORITY="${CYPHER_DECK_PRIORITY:-80}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo bash $0"
  exit 1
fi

if [[ -z "${PSK}" ]]; then
  echo "Set CYPHER_DECK_PSK to the deck AP password (≥8 characters)."
  exit 1
fi

if [[ "${#PSK}" -lt 8 ]]; then
  echo "WPA password must be at least 8 characters."
  exit 1
fi

if ! command -v nmcli >/dev/null 2>&1; then
  echo "nmcli not found. Install NetworkManager."
  exit 1
fi

nmcli connection delete "${CON_NAME}" 2>/dev/null || true

nmcli connection add type wifi ifname "${IFACE}" con-name "${CON_NAME}" \
  autoconnect yes \
  connection.autoconnect-priority "${PRIORITY}" \
  ssid "${SSID}" \
  wifi-sec.key-mgmt wpa-psk \
  wifi-sec.psk "${PSK}" \
  ipv4.method auto

echo "Created connection '${CON_NAME}' (SSID=${SSID}, priority=${PRIORITY})."
echo "Bring up when the deck AP is on:"
echo "  sudo nmcli connection up ${CON_NAME}"
nmcli connection show "${CON_NAME}" | head -20
