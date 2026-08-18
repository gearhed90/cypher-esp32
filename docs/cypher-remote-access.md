# Cypher Remote Access & Recovery Guide

**Last Updated:** August 18, 2026  
**Phase:** Foundation  
**Priority:** Reliable access to the Pi dashboard + clean ESP32 recovery path

---

## Current Architecture (Important)

Control no longer goes through an ESP32 web UI.

- The **Raspberry Pi dashboard** (`http://<pi>:5000`) is the single control interface.
- The ESP32 is a pure motor controller that only listens on UART.
- Remote access means reaching the **Cypher Pi** (Tailscale, cyberdeck link, or recovery AP), not proxying an ESP32 web server.

**Primary controller (planned):** cyberdeck (Pi 5 + Touch Display).  
**Phone:** optional uplink (hotspot) or backup — not the main drive surface.  
**Ethernet:** recovery only on the rover when wireless is impossible.

---

## Access paths (priority)

| Situation | Path |
|-----------|------|
| Home / any network with internet | Cypher as Wi‑Fi station + **Tailscale** → `http://<tailscale-name-or-ip>:5000` |
| Field, cyberdeck present | **Cyberdeck AP** (`Cypher-Deck`) → Cypher joins as station → control from deck browser |
| Field, phone only | Phone hotspot → Cypher joins phone SSID → Tailscale if phone shares internet |
| No known Wi‑Fi at all | **Cypher-Setup** recovery AP (see §3) |
| Wireless dead | Ethernet (desk / last resort) |

Example Tailscale: `http://100.70.99.34:5000`

---

## 1. Cyberdeck ↔ Cypher (instant field link)

**Policy:** Deck is the AP; Cypher is the station. Ethernet is not normal rover use.

| Item | Value |
|------|--------|
| SSID | `Cypher-Deck` |
| Password | Set locally (≥8 chars); keep in sync on deck + Cypher |
| Deck AP IP | `192.168.5.1/24` |
| Cypher | DHCP on that subnet |
| Dashboard | `http://192.168.5.x:5000` |

### One-time setup — Cypher (robot Pi)

```bash
cd ~/cypher-esp32 && git pull
# Edit PSK in the script or pass as env:
export CYPHER_DECK_PSK='your-password-here'
sudo bash pi/wifi-setup/setup-cypher-deck-station.sh
```

Creates NetworkManager profile **Cypher-Deck** with `autoconnect=yes` and priority **80** (above typical home profiles).

### One-time setup — Cyberdeck (controller Pi)

```bash
# On the deck (clone or copy script from this repo):
export CYPHER_DECK_PSK='your-password-here'
sudo bash setup-deck-ap.sh   # or path to pi/wifi-setup/setup-deck-ap.sh
```

Creates profile **Cypher-Deck** in AP mode, `autoconnect=no` (start only when you want field link).

### Day-to-day field use

1. On deck: `sudo nmcli connection up Cypher-Deck`
2. Power Cypher (should associate to `Cypher-Deck`)
3. On deck, find Cypher and open dashboard:
   ```bash
   nmap -p 5000 192.168.5.0/24
   # then http://192.168.5.x:5000
   ```

### Leave field link / use real LAN

- Cypher: join home or phone hotspot (`nmcli device wifi connect ...` or future dashboard Wi‑Fi UI).
- Deck: `sudo nmcli connection down Cypher-Deck` then join the same network or use Tailscale.

Full commands: `pi/wifi-setup/README.md`.

---

## 2. Tailscale (normal remote)

When Cypher has uplink (home Wi‑Fi, phone hotspot, etc.):

```
Controller → Tailscale → Cypher Pi → Dashboard :5000
```

---

## 3. WiFi AP recovery (Cypher-Setup)

When Cypher has **no** known network and no deck AP:

1. Pi boots and waits ~90 s for normal WiFi.
2. If still offline, starts hotspot **Cypher-Setup** (see `pi/wifi-setup/` for current password).
3. Join **Cypher-Setup**, open the setup URL, enter venue SSID + password.
4. Pi joins that network and drops the hotspot; Tailscale can work again.
5. Default: if unused for ~2 minutes, hotspot drops and known networks are retried.

### Install / enable (once)

```bash
cd ~/cypher-esp32 && git pull
sudo cp pi/wifi-setup/cypher-wifi-setup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cypher-wifi-setup.service
```

### Force AP (test)

```bash
sudo systemctl stop cypher-wifi-setup.service
sudo python3 /home/sentry/cypher-esp32/pi/wifi-setup/watchdog.py --force-ap
```

---

## 4. ESP32 Recovery

If the ESP32 is unresponsive (no UART replies, motors stuck):

1. Power-cycle the robot (main power off ~10 s).
2. Serial from the Pi: `screen /dev/serial0 115200`
3. Soft recovery: dashboard `STOP` / restart `cypher-dashboard.service`
4. Hard recovery: USB serial + PlatformIO flash from `firmware/`

---

## 5. Dashboard service

```bash
sudo systemctl status cypher-dashboard.service
sudo systemctl restart cypher-dashboard.service
sudo journalctl -u cypher-dashboard.service -f
```

---

## 6. Change Log

| Date | Change |
|------|--------|
| June 23–24 | Original recovery + nginx proxy for ESP32 web UI (superseded) |
| July 24 2026 | Pi-centric architecture; dashboard is the control UI |
| Aug 11 2026 | WiFi AP recovery (Cypher-Setup) |
| Aug 18 2026 | Cyberdeck AP field link (`Cypher-Deck`); Ethernet = recovery only |

---

**Status:** Tailscale + cyberdeck field link + Cypher-Setup recovery documented.  
Dashboard Wi‑Fi manager UI (scan/join from browser) still optional follow-up.
