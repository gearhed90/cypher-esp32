# Cypher Remote Access & Recovery Guide

**Last Updated:** June 24, 2026  
**Project Phase:** Foundation  
**Thread:** Cypher Remote Access  
**Priority:** Recover the ESP32 + set up a reverse proxy on the Raspberry Pi 4

---

## Current Status (as of June 24, 2026)

- ESP32-WROVER-CAM is reachable at `192.168.12.64` (also responds to `sentrybot.local`).
- It is currently running the older “Sentry Motor” web UI (full joystick + mode + head control interface with WebSocket).
- Raspberry Pi 4 (Tailscale IP `100.70.99.34`) is successfully proxying the ESP32 web UI at `http://100.70.99.34/cypher/`.
- WebSocket connections work (may have a short delay on first connect).
- UART link exists on `/dev/serial0` at 115200 baud (currently quiet unless ESP32 is printing).

**Goal achieved:** ESP32 web UI is now reliably accessible remotely through the Pi via Tailscale.

---

## 1. ESP32 Recovery Procedures

[Previous recovery steps remain unchanged — see earlier version for power cycle, esptool, soft reboot planning, etc.]

---

## 2. Reverse Proxy Setup (Completed)

**Working configuration** as of June 24, 2026:

```nginx
server {
    listen 80;
    listen [::]:80;

    server_name _;

    access_log /var/log/nginx/cypher-esp32-access.log;
    error_log  /var/log/nginx/cypher-esp32-error.log;

    # WebSocket path
    location /ws {
        proxy_pass http://192.168.12.64/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    # Main ESP32 web UI
    location /cypher/ {
        proxy_pass http://192.168.12.64/;
        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_buffering off;
        proxy_read_timeout 300s;
    }

    location / {
        return 301 /cypher/;
    }
}
Access URL: http://100.70.99.34/cypher/

Change Log

























DateChangeUpdated ByJune 23, 2026Initial creation + recovery proceduresZack + GrokJune 24, 2026Completed nginx reverse proxy setupGrokJune 24, 2026Confirmed working WebSocket + full UI accessZack
