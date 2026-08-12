#!/usr/bin/env python3
"""
Minimal WiFi config page for Cypher AP recovery mode.
Stdlib only — must work even when the rest of the stack is down.
"""

from __future__ import annotations

import html
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

HOST = "0.0.0.0"
PORT = 8080

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cypher WiFi Setup</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #0a0a0f; color: #e5e7eb;
           max-width: 420px; margin: 2rem auto; padding: 0 1rem; }}
    h1 {{ font-size: 1.25rem; letter-spacing: 0.08em; }}
    label {{ display: block; margin-top: 1rem; font-size: 0.85rem; color: #9ca3af; }}
    input {{ width: 100%; padding: 0.65rem; margin-top: 0.35rem; border-radius: 6px;
             border: 1px solid #1f2937; background: #111117; color: #e5e7eb; box-sizing: border-box; }}
    button {{ margin-top: 1.25rem; width: 100%; padding: 0.85rem; border: none; border-radius: 6px;
              background: #22d3ee; color: #0a0a0f; font-weight: 700; font-size: 1rem; }}
    .msg {{ margin-top: 1rem; padding: 0.75rem; border-radius: 6px; background: #16161f; font-size: 0.9rem; }}
    .ok {{ border: 1px solid #22c55e; }}
    .err {{ border: 1px solid #ef4444; }}
    .hint {{ color: #6b7280; font-size: 0.8rem; margin-top: 0.5rem; }}
  </style>
</head>
<body>
  <h1>CYPHER · WIFI SETUP</h1>
  <p class="hint">Connected to hotspot <strong>Cypher-Setup</strong>. Enter the network Cypher should join.</p>
  {message}
  <form method="POST" action="/">
    <label>Network name (SSID)
      <input name="ssid" required autocomplete="off" autocapitalize="none">
    </label>
    <label>Password
      <input name="password" type="password" required autocomplete="off">
    </label>
    <button type="submit">Connect</button>
  </form>
  <p class="hint">After a successful connect the hotspot will shut down. Rejoin the venue Wi‑Fi and open the Tailscale address for the dashboard.</p>
</body>
</html>
"""


def nmcli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["nmcli", *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def connect_wifi(ssid: str, password: str) -> tuple[bool, str]:
    ssid = ssid.strip()
    if not ssid:
        return False, "SSID is required."

    # Prefer a clean connect; falls back to creating a connection profile.
    result = nmcli(
        "device", "wifi", "connect", ssid,
        "password", password,
        "ifname", "wlan0",
    )
    if result.returncode == 0:
        return True, "Connected. Hotspot will stop; Tailscale should come back shortly."

    err = (result.stderr or result.stdout or "nmcli failed").strip()
    return False, f"Connect failed: {err}"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print(f"[wifi-setup] {self.address_string()} - {fmt % args}")

    def _send(self, code: int, body: str) -> None:
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        # Captive-portal friendly: any path returns the form
        page = PAGE.format(message="")
        self._send(200, page)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        form = parse_qs(raw)
        ssid = (form.get("ssid") or [""])[0]
        password = (form.get("password") or [""])[0]

        ok, msg = connect_wifi(ssid, password)
        cls = "ok" if ok else "err"
        safe = html.escape(msg)
        message = f'<div class="msg {cls}">{safe}</div>'
        self._send(200, PAGE.format(message=message))

        if ok:
            # Give the browser time to show success, then signal exit
            def _shutdown() -> None:
                import time
                time.sleep(2)
                # Stop hotspot connection if present
                nmcli("connection", "down", "Cypher-Setup")
                # Ask the HTTP server to stop (watchdog will exit AP mode)
                if hasattr(self.server, "request_shutdown"):
                    self.server.request_shutdown()

            threading.Thread(target=_shutdown, daemon=True).start()


class SetupServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop = False

    def request_shutdown(self) -> None:
        self._stop = True

    def serve_until_done(self) -> None:
        self.timeout = 1.0
        while not self._stop:
            self.handle_request()


def run_server(host: str = HOST, port: int = PORT) -> None:
    server = SetupServer((host, port), Handler)
    print(f"[wifi-setup] Config page at http://0.0.0.0:{port}/ (try http://10.42.0.1:{port}/)")
    try:
        server.serve_until_done()
    finally:
        server.server_close()
        print("[wifi-setup] Setup server stopped")


if __name__ == "__main__":
    run_server()
