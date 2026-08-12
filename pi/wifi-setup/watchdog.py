#!/usr/bin/env python3
"""
Cypher WiFi recovery watchdog.

After a boot grace period, if wlan0 is not connected, start a NetworkManager
hotspot (Cypher-Setup) and the setup web UI so a phone can provision WiFi.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time

from setup_server import run_server

HOTSPOT_SSID = "Cypher-Setup"
HOTSPOT_PASS = "cyphersetup"  # min 8 chars for WPA2
HOTSPOT_CON = "Cypher-Setup"
WLAN = "wlan0"
BOOT_GRACE_SEC = 90
CHECK_INTERVAL_SEC = 15


def run(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def wlan_connected() -> bool:
    """True if wlan0 is fully connected (not just associated)."""
    r = run(["nmcli", "-t", "-f", "DEVICE,STATE", "device"])
    if r.returncode != 0:
        return False
    for line in r.stdout.splitlines():
        parts = line.strip().split(":")
        if len(parts) >= 2 and parts[0] == WLAN and parts[1] == "connected":
            return True
    return False


def has_default_route() -> bool:
    r = run(["ip", "route", "show", "default"])
    return r.returncode == 0 and bool(r.stdout.strip())


def online() -> bool:
    return wlan_connected() and has_default_route()


def ensure_hotspot() -> bool:
    """Bring up (or create) the Cypher-Setup AP via NetworkManager."""
    # If connection profile exists, try up
    check = run(["nmcli", "-t", "-f", "NAME", "connection", "show"])
    names = {n.strip() for n in check.stdout.splitlines() if n.strip()}

    if HOTSPOT_CON not in names:
        print(f"[wifi-watch] Creating hotspot profile {HOTSPOT_CON}")
        r = run([
            "nmcli", "connection", "add",
            "type", "wifi",
            "ifname", WLAN,
            "con-name", HOTSPOT_CON,
            "autoconnect", "no",
            "ssid", HOTSPOT_SSID,
        ])
        if r.returncode != 0:
            print("[wifi-watch] create failed:", r.stderr or r.stdout)
            return False
        run([
            "nmcli", "connection", "modify", HOTSPOT_CON,
            "802-11-wireless.mode", "ap",
            "802-11-wireless.band", "bg",
            "ipv4.method", "shared",
            "wifi-sec.key-mgmt", "wpa-psk",
            "wifi-sec.psk", HOTSPOT_PASS,
        ])

    # Bring down other wifi client connections so the radio is free
    run(["nmcli", "device", "disconnect", WLAN])
    time.sleep(1)

    print(f"[wifi-watch] Starting hotspot SSID={HOTSPOT_SSID}")
    r = run(["nmcli", "connection", "up", HOTSPOT_CON], timeout=45)
    if r.returncode != 0:
        # Fallback: nmcli device wifi hotspot
        print("[wifi-watch] connection up failed, trying device wifi hotspot")
        r = run([
            "nmcli", "device", "wifi", "hotspot",
            "ifname", WLAN,
            "con-name", HOTSPOT_CON,
            "ssid", HOTSPOT_SSID,
            "password", HOTSPOT_PASS,
        ], timeout=45)
        if r.returncode != 0:
            print("[wifi-watch] hotspot failed:", r.stderr or r.stdout)
            return False

    print("[wifi-watch] Hotspot is up. Join WiFi 'Cypher-Setup' / password 'cyphersetup'")
    print("[wifi-watch] Then open http://10.42.0.1:8080")
    return True


def stop_hotspot() -> None:
    run(["nmcli", "connection", "down", HOTSPOT_CON])
    print("[wifi-watch] Hotspot stopped")


def enter_ap_mode() -> None:
    if not ensure_hotspot():
        print("[wifi-watch] Could not start AP; will retry later")
        return
    try:
        run_server(port=8080)
    finally:
        stop_hotspot()


def main() -> int:
    parser = argparse.ArgumentParser(description="Cypher WiFi recovery watchdog")
    parser.add_argument("--force-ap", action="store_true", help="Skip checks; enter AP mode now")
    parser.add_argument("--grace", type=int, default=BOOT_GRACE_SEC, help="Boot grace seconds")
    args = parser.parse_args()

    if args.force_ap:
        enter_ap_mode()
        return 0

    print(f"[wifi-watch] Boot grace {args.grace}s…")
    time.sleep(args.grace)

    while True:
        if online():
            print("[wifi-watch] Network OK")
            # Idle while healthy; re-check periodically in case we lose WiFi later
            time.sleep(60)
            continue

        print("[wifi-watch] No usable WiFi — entering setup AP mode")
        enter_ap_mode()
        # After setup server exits (success or crash), wait and re-evaluate
        time.sleep(CHECK_INTERVAL_SEC)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        stop_hotspot()
        sys.exit(0)
