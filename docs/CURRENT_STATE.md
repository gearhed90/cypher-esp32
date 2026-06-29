# Cypher - Current State (June 2026)

## Working
- Full motor control from dashboard (buttons + keyboard)
- Combined movement (forward + turning at the same time)
- Speed slider
- Heartbeat + 1.5s safety timeout
- ESP32 simplified (no web server)
- Dashboard is the single control interface

## Services
- `cypher-dashboard.service` → Running
- `cypher-bridge.service` → Stopped (not needed)

## Next Possible Improvements
- UI polish / status indicators
- OTA enable command for ESP32
- Vision / tracking features
- Better error handling / reconnection logic

## Notes
- ESP32 is currently plugged into USB for easy monitoring.
- All control happens through http://cypher:5000
