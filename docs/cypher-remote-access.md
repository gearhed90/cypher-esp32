# Cypher Remote Access & Recovery Guide

**Last Updated:** August 11, 2026  
**Phase:** Foundation  
**Priority:** Reliable remote access to the Pi dashboard + clean ESP32 recovery path

---

## Current Architecture (Important)

Control no longer goes through an ESP32 web UI.

- The **Raspberry Pi dashboard** (`http://<pi>:5000`) is the single control interface.
- The ESP32 is a pure motor controller that only listens on UART.
- Remote access therefore means reaching the **Pi** (via Tailscale or similar), not proxying an ESP32 web server.

The older reverse-proxy configuration that pointed at the ESP32 web UI is obsolete and should not be used.

---

## 1. Remote Access Goal

Make the Pi dashboard reliably reachable from outside the local network with:

- Tailscale (preferred) or equivalent zero-config VPN
- Clear status of the dashboard service and UART link
- **WiFi recovery** when the Pi is at a new location with no known network

### Recommended Access Path

```
Your machine → Tailscale → Raspberry Pi → Dashboard on port 5000
```

Once Tailscale is healthy you can simply open:

```
http://<pi-tailscale-name-or-ip>:5000
```

Example: `http://100.70.99.34:5000`

---

## 2. WiFi AP Recovery (new location / unknown network)

Tailscale needs an underlying network. If the Pi has no known WiFi, use setup mode.

### Automatic flow

1. Pi boots and waits ~90 s for normal WiFi.
2. If still offline, it starts hotspot **Cypher-Setup** (password **`cyphersetup`**).
3. On your phone, join **Cypher-Setup**.
4. Open **http://10.42.0.1:8080**
5. Enter the venue SSID + password → Pi joins that network and drops the hotspot.
6. Rejoin the venue WiFi on your phone; Tailscale to the Pi should work again.

### Install / enable (once)

```bash
cd ~/cypher-esp32 && git pull
sudo cp pi/wifi-setup/cypher-wifi-setup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cypher-wifi-setup.service
```

### Force AP mode (test while still online)

```bash
sudo systemctl stop cypher-wifi-setup.service
sudo python3 /home/sentry/cypher-esp32/pi/wifi-setup/watchdog.py --force-ap
```

Code lives in `pi/wifi-setup/` (watchdog + stdlib setup server).

---

## 3. ESP32 Recovery Procedures

If the ESP32 becomes unresponsive (no UART replies, motors stuck, boot issues):

### Step 1 — Basic Diagnostics
1. Power-cycle the entire robot (main power off 10 s).
2. Check serial console from the Pi:
   ```bash
   screen /dev/serial0 115200
   # or /dev/ttyUSB0 if using a USB adapter
   ```
3. Look for boot messages and any brown-out / strapping-pin warnings.
4. Confirm the dashboard can still open the serial port and send `HEARTBEAT` / `STATUS?`.

**Common quick fixes**
- Loose power / ground
- GPIO 12 (tilt servo) being pulled low at boot (strapping pin)
- Overloaded 3.3 V rail

### Step 2 — Soft Recovery
- If UART is alive, send `STOP` then a fresh `MOVE` or simply let the safety timeout fire.
- Restart the dashboard service:
  ```bash
  sudo systemctl restart cypher-dashboard.service
  ```

### Step 3 — Hard Recovery / Reflash

1. Connect a USB-to-serial adapter to the ESP32 (TX↔RX, GND, and preferably RTS/DTR for auto-reset).
2. Put the ESP32 into download mode (hold BOOT while tapping EN, or let esptool handle it).
3. Flash with PlatformIO or esptool from `firmware/`.

---

## 4. Dashboard Service Recovery

```bash
sudo systemctl status cypher-dashboard.service
sudo systemctl restart cypher-dashboard.service
sudo journalctl -u cypher-dashboard.service -f
```

If the serial port is busy, confirm no other process is holding `/dev/serial0`.

---

## 5. Change Log

| Date         | Change                                                                 | Notes |
|--------------|------------------------------------------------------------------------|-------|
| June 23–24   | Original recovery + nginx reverse proxy for ESP32 web UI               | Superseded |
| July 24 2026 | Full rewrite for Pi-centric architecture; dashboard is the control UI  | — |
| Aug 11 2026  | WiFi AP recovery (Cypher-Setup hotspot + config page)                  | Current |

---

**Status:** Pi dashboard + Tailscale + WiFi AP recovery documented.  
PWA drive UI is installable; camera stream still a placeholder until hardware is reinstalled.
