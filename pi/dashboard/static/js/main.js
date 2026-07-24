/**
 * Cypher Dashboard — client logic
 * - Live clock
 * - Camera refresh
 * - Drive pad + keyboard → /api/move /api/stop
 * - Discrete speed 10%–100% via number keys 1–0
 * - Periodic ESP32 status poll
 */

const state = {
  percent: 50,          // 10 … 100 in steps of 10
  activeDir: null,      // 'forward' | 'back' | 'left' | 'right' | null
  keysDown: new Set(),
};

function percentToPwm(pct) {
  return Math.round((pct / 100) * 255);
}

function getSpeed() {
  return percentToPwm(state.percent);
}

function updateSpeedUI() {
  const slider = document.getElementById('speed');
  const label = document.getElementById('speed-val');
  if (slider) slider.value = state.percent;
  if (label) label.textContent = state.percent + '%';
}

function setPercent(pct) {
  // Clamp and snap to nearest 10%
  pct = Math.max(10, Math.min(100, Math.round(pct / 10) * 10));
  state.percent = pct;
  updateSpeedUI();

  // If currently moving, immediately re-send with new speed
  if (state.activeDir) {
    const cmd = dirToCommand(state.activeDir);
    sendMove(cmd.throttle, cmd.steering);
  }
}

function updateClock() {
  const el = document.getElementById('clock');
  if (!el) return;
  const now = new Date();
  const h = String(now.getUTCHours()).padStart(2, '0');
  const m = String(now.getUTCMinutes()).padStart(2, '0');
  const s = String(now.getUTCSeconds()).padStart(2, '0');
  el.textContent = `${h}:${m}:${s} UTC`;
}

function refreshStream() {
  const img = document.getElementById('camera-stream');
  if (!img) return;
  const base = img.src.split('?')[0];
  img.src = `${base}?t=${Date.now()}`;
}

function setStatus(online) {
  const dot = document.getElementById('esp-status-dot');
  const text = document.getElementById('esp-status-text');
  const conn = document.getElementById('conn-state');
  if (dot) {
    dot.classList.toggle('offline', !online);
  }
  if (text) text.textContent = online ? 'ESP32 ONLINE' : 'ESP32 OFFLINE';
  if (conn) {
    conn.textContent = online ? 'UP' : 'DOWN';
    conn.classList.toggle('down', !online);
  }
}

async function pollStatus() {
  try {
    const r = await fetch('/api/status');
    const data = await r.json();
    setStatus(!!data.connected);
  } catch (e) {
    setStatus(false);
  }
}

function dirToCommand(dir) {
  const s = getSpeed();
  switch (dir) {
    case 'forward': return { throttle: s,  steering: 0 };
    case 'back':    return { throttle: -s, steering: 0 };
    case 'left':    return { throttle: 0,  steering: -s };
    case 'right':   return { throttle: 0,  steering: s };
    default:        return { throttle: 0,  steering: 0 };
  }
}

async function sendMove(throttle, steering) {
  try {
    const r = await fetch('/api/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ throttle, steering }),
    });
    const data = await r.json();
    if (!data.ok) {
      console.warn('MOVE failed', data);
      setStatus(false);
    }
  } catch (e) {
    console.warn('MOVE network error', e);
    setStatus(false);
  }
}

async function sendStop() {
  state.activeDir = null;
  try {
    await fetch('/api/stop', { method: 'POST' });
  } catch (e) {
    console.warn('STOP failed', e);
  }
}

function startDir(dir) {
  if (state.activeDir === dir) return;
  state.activeDir = dir;
  const cmd = dirToCommand(dir);
  sendMove(cmd.throttle, cmd.steering);
}

function stopDir() {
  if (state.activeDir === null) return;
  sendStop();
}

/* ---------- Button (pointer) handlers ---------- */
function bindDpad() {
  const dpad = document.getElementById('dpad');
  if (!dpad) return;

  dpad.querySelectorAll('.drive-btn').forEach(btn => {
    const dir = btn.dataset.dir;

    const onDown = (e) => {
      e.preventDefault();
      if (dir === 'stop') {
        sendStop();
        return;
      }
      startDir(dir);
    };
    const onUp = (e) => {
      e.preventDefault();
      if (dir !== 'stop') stopDir();
    };

    btn.addEventListener('pointerdown', onDown);
    btn.addEventListener('pointerup', onUp);
    btn.addEventListener('pointerleave', onUp);
    btn.addEventListener('pointercancel', onUp);
  });
}

/* ---------- Keyboard ---------- */
const DIR_KEYS = {
  ArrowUp: 'forward',
  ArrowDown: 'back',
  ArrowLeft: 'left',
  ArrowRight: 'right',
  ' ': 'stop',
  Space: 'stop',
};

// Number keys → percent (1=10% … 9=90%, 0=100%)
const SPEED_KEYS = {
  '1': 10, '2': 20, '3': 30, '4': 40, '5': 50,
  '6': 60, '7': 70, '8': 80, '9': 90, '0': 100,
};

function onKeyDown(e) {
  // Speed keys (work even while moving)
  if (SPEED_KEYS[e.key] !== undefined) {
    e.preventDefault();
    setPercent(SPEED_KEYS[e.key]);
    return;
  }

  const dir = DIR_KEYS[e.key];
  if (!dir) return;
  e.preventDefault();
  if (state.keysDown.has(e.key)) return;
  state.keysDown.add(e.key);

  if (dir === 'stop') {
    sendStop();
    return;
  }
  startDir(dir);
}

function onKeyUp(e) {
  const dir = DIR_KEYS[e.key];
  if (!dir) return;
  e.preventDefault();
  state.keysDown.delete(e.key);

  const still = [...state.keysDown]
    .map(k => DIR_KEYS[k])
    .filter(d => d && d !== 'stop');
  if (still.length === 0) {
    stopDir();
  } else {
    startDir(still[still.length - 1]);
  }
}

/* ---------- Speed slider (snaps to 10% steps) ---------- */
function bindSpeed() {
  const slider = document.getElementById('speed');
  if (!slider) return;

  slider.addEventListener('input', () => {
    setPercent(parseInt(slider.value, 10));
  });
}

/* ---------- Init ---------- */
document.addEventListener('DOMContentLoaded', () => {
  updateClock();
  setInterval(updateClock, 1000);

  updateSpeedUI();          // show default 50%
  bindDpad();
  bindSpeed();
  window.addEventListener('keydown', onKeyDown);
  window.addEventListener('keyup', onKeyUp);

  pollStatus();
  setInterval(pollStatus, 2000);

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) sendStop();
  });
  window.addEventListener('blur', () => sendStop());
});
