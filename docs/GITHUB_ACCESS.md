# GitHub Access – Cypher Project

## Repository
- **URL:** https://github.com/gearhed90/cypher-esp32
- **Branch:** `main`
- **Owner:** gearhed90

## Authentication (as of August 2026)

### Current method on the Pi: SSH (preferred)

SSH keys are set up on the Raspberry Pi (`cypher-pi`).

- Remote URL: `git@github.com:gearhed90/cypher-esp32.git`
- No username/password or token needed for `git pull` / `git push`

### Personal Access Token (fallback)

Only needed on machines that don’t have SSH keys configured.

1. Create a token at: https://github.com/settings/tokens  
   → **Generate new token (classic)** → scope **`repo`**
2. When prompted:
   - Username: `gearhed90`
   - Password: paste the token

### Useful commands

```bash
cd ~/cypher-esp32
git status
git pull
git push
git log --oneline -5
git remote -v
