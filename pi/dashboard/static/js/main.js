/**
 * Cypher Dashboard — client logic
 * - Live clock
 * - Camera refresh
 * - Drive pad + keyboard → /api/move /api/stop
 * - Periodic ESP32 status poll
 */

const state = {
  speed: 120,
  activeDir: null,   // 'forward' | 'back' | 'left' | 'right' | null
  keysDown: new Set(),
};

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
  const s = state.speed;
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
const KEY_MAP = {
  ArrowUp: 'forward',
  ArrowDown: 'back',
  ArrowLeft: 'left',
  ArrowRight: 'right',
  ' ': 'stop',
  Space: 'stop',
};

function onKeyDown(e) {
  const dir = KEY_MAP[e.key];
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
  const dir = KEY_MAP[e.key];
  if (!dir) return;
  e.preventDefault();
  state.keysDown.delete(e.key);

  // If any movement key is still held, switch to that direction;
  // otherwise stop.
  const still = [...state.keysDown].map(k => KEY_MAP[k]).filter(d => d && d !== 'stop');
  if (still.length === 0) {
    stopDir();
  } else {
    startDir(still[still.length - 1]);
  }
}

/* ---------- Speed slider ---------- */
function bindSpeed() {
  const slider = document.getElementById('speed');
  const label = document.getElementById('speed-val');
  if (!slider || !label) return;

  slider.addEventListener('input', () => {
    state.speed = parseInt(slider.value, 10);
    label.textContent = state.speed;
    // If currently moving, re-send with new speed
    if (state.activeDir) {
      const cmd = dirToCommand(state.activeDir);
      sendMove(cmd.throttle, cmd.steering);
    }
  });
}

/* ---------- Init ---------- */
document.addEventListener('DOMContentLoaded', () => {
  updateClock();
  setInterval(updateClock, 1000);

  bindDpad();
  bindSpeed();
  window.addEventListener('keydown', onKeyDown);
  window.addEventListener('keyup', onKeyUp);

  // Status poll every 2 s
  pollStatus();
  setInterval(pollStatus, 2000);

  // Safety: stop motors if the page loses focus / is hidden
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) sendStop();
  });
  window.addEventListener('blur', () => sendStop());
});
