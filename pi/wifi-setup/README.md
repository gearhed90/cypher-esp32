# Cypher WiFi Setup (AP recovery)

When the Pi cannot join a known WiFi network, this service starts a setup hotspot so you can add a network from your phone.

## Flow

1. Boot → wait ~90 s for normal WiFi.
2. If `wlan0` is still not connected → start **Cypher-Setup** hotspot (password `cyphersetup`).
3. On your phone: join **Cypher-Setup**.
4. Open **http://10.42.0.1:8080** (or whatever IP the page shows).
5. Enter venue SSID + password → Pi joins that network, drops the hotspot, Tailscale comes back.

## Install on the Pi

```bash
cd ~/cypher-esp32
git pull

# Install systemd unit
sudo cp pi/wifi-setup/cypher-wifi-setup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cypher-wifi-setup.service

# Status / logs
sudo systemctl status cypher-wifi-setup.service
sudo journalctl -u cypher-wifi-setup.service -f
```

## Manual test (force AP mode)

```bash
sudo systemctl stop cypher-wifi-setup.service
sudo python3 /home/sentry/cypher-esp32/pi/wifi-setup/watchdog.py --force-ap
```

Join **Cypher-Setup** / `cyphersetup`, open the URL printed in the journal.

## Notes

- Requires NetworkManager (`nmcli`). Default on current Raspberry Pi OS.
- Setup server uses Python stdlib only (no pip packages).
- Does not replace Tailscale; it only restores an underlying WiFi path so Tailscale can work again.
