#!/usr/bin/env python3
"""
Cypher WiFi recovery watchdog.

After a boot grace period, if wlan0 is not connected, start a NetworkManager
hotspot (Cypher-Setup) and the setup web UI so a phone can provision WiFi.

AP mode automatically ends after AP_TIMEOUT_SEC (default 120s) and client
WiFi is restored so the Pi is not stuck on the hotspot during home testing.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import threading
import time

from setup_server import PORT, SetupServer, Handler

HOTSPOT_SSID = "Cypher-Setup"
HOTSPOT_PASS = "cyphersetup"
HOTSPOT_CON = "Cypher-Setup"
WLAN = "wlan0"
BOOT_GRACE_SEC = 90
CHECK_INTERVAL_SEC = 15
AP_TIMEOUT_SEC = 120  # revert to normal WiFi if setup not completed


def run(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def wlan_connected() -> bool:
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

    run(["nmcli", "device", "disconnect", WLAN])
    time.sleep(1)

    print(f"[wifi-watch] Starting hotspot SSID={HOTSPOT_SSID}")
    r = run(["nmcli", "connection", "up", HOTSPOT_CON], timeout=45)
    if r.returncode != 0:
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
    print(f"[wifi-watch] Then open http://10.42.0.1:{PORT}  (auto-reverts in {AP_TIMEOUT_SEC}s)")
    return True


def stop_hotspot() -> None:
    run(["nmcli", "connection", "down", HOTSPOT_CON])
    print("[wifi-watch] Hotspot stopped")


def restore_client_wifi() -> None:
    """Drop AP and try to bring back any known non-hotspot WiFi profile."""
    stop_hotspot()
    run(["nmcli", "radio", "wifi", "on"])

    r = run(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"])
    for line in r.stdout.splitlines():
        parts = line.strip().split(":")
        if len(parts) < 2:
            continue
        name, typ = parts[0], parts[1]
        if typ != "802-11-wireless":
            continue
        if name == HOTSPOT_CON:
            continue
        print(f"[wifi-watch] Restoring WiFi profile: {name}")
        up = run(["nmcli", "connection", "up", name], timeout=45)
        if up.returncode == 0:
            print(f"[wifi-watch] Connected via {name}")
            return
        print(f"[wifi-watch] Could not up {name}:", up.stderr or up.stdout)

    # Last resort: ask NM to connect the device
    run(["nmcli", "device", "connect", WLAN])
    print("[wifi-watch] Requested nmcli device connect wlan0")


def enter_ap_mode(timeout_sec: int = AP_TIMEOUT_SEC) -> None:
    if not ensure_hotspot():
        print("[wifi-watch] Could not start AP; will retry later")
        return

    server = SetupServer(("0.0.0.0", PORT), Handler)

    def serve() -> None:
        try:
            server.serve_until_done()
        finally:
            try:
                server.server_close()
            except Exception:
                pass

    th = threading.Thread(target=serve, daemon=True)
    th.start()
    print(f"[wifi-watch] Setup server listening; timeout={timeout_sec}s")

    deadline = time.time() + timeout_sec
    while time.time() < deadline and not server._stop:
        time.sleep(0.5)

    if not server._stop:
        print(f"[wifi-watch] AP timeout ({timeout_sec}s) — no successful setup; restoring home WiFi")
        server.request_shutdown()
        time.sleep(0.6)
    else:
        print("[wifi-watch] Setup finished successfully")

    restore_client_wifi()
    th.join(timeout=3)


def main() -> int:
    parser = argparse.ArgumentParser(description="Cypher WiFi recovery watchdog")
    parser.add_argument("--force-ap", action="store_true", help="Skip checks; enter AP mode now")
    parser.add_argument("--grace", type=int, default=BOOT_GRACE_SEC, help="Boot grace seconds")
    parser.add_argument(
        "--ap-timeout",
        type=int,
        default=AP_TIMEOUT_SEC,
        help="Seconds in AP mode before reverting to client WiFi (default 120)",
    )
    args = parser.parse_args()

    if args.force_ap:
        enter_ap_mode(timeout_sec=args.ap_timeout)
        return 0

    print(f"[wifi-watch] Boot grace {args.grace}s…")
    time.sleep(args.grace)

    while True:
        if online():
            print("[wifi-watch] Network OK")
            time.sleep(60)
            continue

        print("[wifi-watch] No usable WiFi — entering setup AP mode")
        enter_ap_mode(timeout_sec=args.ap_timeout)
        time.sleep(CHECK_INTERVAL_SEC)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        stop_hotspot()
        restore_client_wifi()
        sys.exit(0)
