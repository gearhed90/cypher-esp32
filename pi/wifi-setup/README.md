# Cypher WiFi Setup

Two roles:

1. **Field link (preferred with cyberdeck):** Cypher joins cyberdeck AP `Cypher-Deck`.
2. **Recovery AP:** If Cypher has no known network, start **Cypher-Setup** so you can add credentials.

Ethernet is recovery-only for the rover.

---

## A. Cyberdeck field link (`Cypher-Deck`)

### On Cypher (robot) — station profile

```bash
cd ~/cypher-esp32 && git pull
export CYPHER_DECK_PSK='your-password-here'   # ≥8 characters
sudo bash pi/wifi-setup/setup-cypher-deck-station.sh
```

- Creates NM connection **Cypher-Deck**
- `autoconnect=yes`, priority **80**
- SSID `Cypher-Deck`, WPA-PSK, DHCP

Bring up manually:

```bash
sudo nmcli connection up Cypher-Deck
ip -br addr show wlan0
```

### On cyberdeck (controller) — AP profile

Copy `setup-deck-ap.sh` to the deck (or clone this repo) and run:

```bash
export CYPHER_DECK_PSK='your-password-here'
sudo bash pi/wifi-setup/setup-deck-ap.sh
```

Start field AP:

```bash
sudo nmcli connection up Cypher-Deck
# Deck should be 192.168.5.1
```

Stop AP:

```bash
sudo nmcli connection down Cypher-Deck
```

### Use

1. Deck: `nmcli connection up Cypher-Deck`
2. Power Cypher
3. Deck: `nmap -p 5000 192.168.5.0/24` → open `http://192.168.5.x:5000`

---

## B. Recovery hotspot (Cypher-Setup)

When the Pi cannot join a known WiFi network, this service starts a setup hotspot.

### Flow

1. Boot → wait ~90 s for normal WiFi.
2. If `wlan0` is still not connected → start **Cypher-Setup** hotspot.
3. Join **Cypher-Setup**, open the setup URL (see watchdog / setup_server).
4. Enter venue SSID + password → Pi joins that network, drops the hotspot.
5. If you do nothing for ~2 minutes, hotspot drops and known networks are retried.

### Install on the Pi

```bash
cd ~/cypher-esp32 && git pull
sudo cp pi/wifi-setup/cypher-wifi-setup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cypher-wifi-setup.service
sudo systemctl status cypher-wifi-setup.service
```

### Force AP (test)

```bash
sudo systemctl stop cypher-wifi-setup.service
sudo python3 /home/sentry/cypher-esp32/pi/wifi-setup/watchdog.py --force-ap
```

### Notes

- Requires NetworkManager (`nmcli`).
- Setup server uses Python stdlib only.
- Does not replace Tailscale; it restores an underlying path so Tailscale can work again.
- Prefer **Cypher-Deck** when the cyberdeck is the controller.
