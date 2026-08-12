# Cypher WiFi Setup (AP recovery)

When the Pi cannot join a known WiFi network, this service starts a setup hotspot so you can add a network from your phone.

## Flow

1. Boot → wait ~90 s for normal WiFi.
2. If `wlan0` is still not connected → start **Cypher-Setup** hotspot (password `cyphersetup`).
3. On your phone: join **Cypher-Setup**.
4. Open **http://10.42.0.1:8080**.
5. Enter venue SSID + password → Pi joins that network, drops the hotspot, Tailscale comes back.
6. **If you do nothing for 2 minutes**, the Pi drops the hotspot and reconnects to a known network (e.g. home WiFi).

## Install on the Pi

```bash
cd ~/cypher-esp32
git pull

sudo cp pi/wifi-setup/cypher-wifi-setup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cypher-wifi-setup.service

sudo systemctl status cypher-wifi-setup.service
sudo journalctl -u cypher-wifi-setup.service -f
```

## Manual test (force AP mode)

```bash
sudo systemctl stop cypher-wifi-setup.service
sudo python3 /home/sentry/cypher-esp32/pi/wifi-setup/watchdog.py --force-ap
# Optional longer window:
# sudo python3 .../watchdog.py --force-ap --ap-timeout 300
```

Join **Cypher-Setup** / `cyphersetup`, open the URL. After 2 minutes (default) it should return to home WiFi by itself.

## Notes

- Requires NetworkManager (`nmcli`).
- Setup server uses Python stdlib only.
- Does not replace Tailscale; it restores an underlying WiFi path so Tailscale can work again.
