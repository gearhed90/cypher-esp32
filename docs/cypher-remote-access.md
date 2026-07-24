# Cypher Remote Access & Recovery Guide

**Last Updated:** July 24, 2026  
**Phase:** Foundation  
**Priority:** Reliable remote access to the Pi dashboard + clean ESP32 recovery path

---

## Current Architecture (Important)

Control no longer goes through an ESP32 web UI.

- The **Raspberry Pi dashboard** (`http://cypher:5000`) is the single control interface.
- The ESP32 is a pure motor controller that only listens on UART.
- Remote access therefore means reaching the **Pi** (via Tailscale or similar), not proxying an ESP32 web server.

The older reverse-proxy configuration that pointed at the ESP32 web UI is obsolete and should not be used.

---

## 1. Remote Access Goal

Make the Pi dashboard reliably reachable from outside the local network with:

- Tailscale (preferred) or equivalent zero-config VPN
- Optional nginx reverse proxy on the Pi if you want a clean path or TLS later
- Clear status of the dashboard service and UART link

### Recommended Access Path

```
Your machine → Tailscale → Raspberry Pi → Dashboard on port 5000
```

Once Tailscale is healthy you can simply open:

```
http://<pi-tailscale-name-or-ip>:5000
```

---

## 2. ESP32 Recovery Procedures

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
3. On the Pi (or any machine with esptool):

   ```bash
   pip3 install esptool
   esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
   esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 /path/to/firmware.bin
   ```

4. Power-cycle or press EN, then monitor serial at 115200.

**Tips**
- Prefer a USB adapter over the Pi’s native UART for flashing (easier boot-mode control).
- Use 115200 baud if 460800 is unstable.
- Ensure solid 5 V power during the flash.

---

## 3. Dashboard Service Recovery

```bash
# Status
sudo systemctl status cypher-dashboard.service

# Restart
sudo systemctl restart cypher-dashboard.service

# Live logs
sudo journalctl -u cypher-dashboard.service -f
```

If the serial port is busy, confirm no other process (old bridge service, screen session, etc.) is holding `/dev/serial0`.

---

## 4. Change Log

| Date         | Change                                                                 | Notes |
|--------------|------------------------------------------------------------------------|-------|
| June 23–24   | Original recovery + nginx reverse proxy for ESP32 web UI               | Superseded |
| July 24 2026 | Full rewrite for Pi-centric architecture; dashboard is the control UI  | Current |

---

**Status:** Documentation locked to the current architecture.  
Implementation of the hardened Tailscale + status page remains a Foundation task.
