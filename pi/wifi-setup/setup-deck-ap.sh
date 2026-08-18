#!/bin/bash
# Cyberdeck (controller): NetworkManager Wi-Fi Access Point "Cypher-Deck"
# Run on the Pi 5 cyberdeck, not on the robot.
# Usage:
#   export CYPHER_DECK_PSK='your-password-here'
#   sudo bash setup-deck-ap.sh

set -euo pipefail

SSID="${CYPHER_DECK_SSID:-Cypher-Deck}"
PSK="${CYPHER_DECK_PSK:-}"
IFACE="${CYPHER_WIFI_IFACE:-wlan0}"
CON_NAME="Cypher-Deck"
AP_ADDR="${CYPHER_DECK_AP_ADDR:-192.168.5.1/24}"
CHANNEL="${CYPHER_DECK_CHANNEL:-6}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo bash $0"
  exit 1
fi

if [[ -z "${PSK}" ]]; then
  echo "Set CYPHER_DECK_PSK to the AP password (≥8 characters)."
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
  autoconnect no \
  ssid "${SSID}" \
  mode ap \
  wifi.band bg \
  wifi.channel "${CHANNEL}" \
  ipv4.method shared \
  ipv4.addresses "${AP_ADDR}" \
  wifi-sec.key-mgmt wpa-psk \
  wifi-sec.psk "${PSK}"

echo "Created AP connection '${CON_NAME}' (SSID=${SSID}, ${AP_ADDR})."
echo "Start field link:"
echo "  sudo nmcli connection up ${CON_NAME}"
echo "Stop:"
echo "  sudo nmcli connection down ${CON_NAME}"
nmcli connection show "${CON_NAME}" | head -25
