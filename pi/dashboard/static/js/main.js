/**
 * Cypher Dashboard — client logic
 * - Mobile landscape: continuous throttle/steer sliders + trim
 * - Desktop: dual-stick buttons + keyboard
 * - Safety STOP on blur / hide / explicit stop
 */

const state = {
  percent: 50,
  activeDir: null,
  keysDown: new Set(),
  throttle: 0,
  steering: 0,
  trim: 0,
  moving: false,
  sendTimer: null,
};

const DEADBAND = 8; // ignore tiny slider noise near center

function percentToPwm(pct) {
  return Math.round((pct / 100) * 255);
}

function getSpeed() {
  return percentToPwm(state.percent);
}

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function applyDeadband(v) {
  return Math.abs(v) < DEADBAND ? 0 : v;
}

/* ---------- Status UI (both layouts) ---------- */
function setStatus(online) {
  document.querySelectorAll("#esp-status-dot, #esp-status-dot-m").forEach((dot) => {
    if (dot) dot.classList.toggle("offline", !online);
  });
  const t = document.getElementById("esp-status-text");
  const tm = document.getElementById("esp-status-text-m");
  if (t) t.textContent = online ? "ESP32 ONLINE" : "ESP32 OFFLINE";
  if (tm) tm.textContent = online ? "ONLINE" : "OFFLINE";
  const conn = document.getElementById("conn-state");
  if (conn) {
    conn.textContent = online ? "UP" : "DOWN";
    conn.classList.toggle("down", !online);
  }
}

async function pollStatus() {
  try {
    const r = await fetch("/api/status");
    const data = await r.json();
    setStatus(!!data.connected);
  } catch (e) {
    setStatus(false);
  }
}

function updateClock() {
  const el = document.getElementById("clock");
  if (!el) return;
  const now = new Date();
  const h = String(now.getUTCHours()).padStart(2, "0");
  const m = String(now.getUTCMinutes()).padStart(2, "0");
  const s = String(now.getUTCSeconds()).padStart(2, "0");
  el.textContent = `${h}:${m}:${s} UTC`;
}

function updateSpeedUI() {
  const slider = document.getElementById("speed");
  const label = document.getElementById("speed-val");
  if (slider) slider.value = state.percent;
  if (label) label.textContent = state.percent + "%";
}

function setPercent(pct) {
  pct = Math.max(10, Math.min(100, Math.round(pct / 10) * 10));
  state.percent = pct;
  updateSpeedUI();
  if (state.activeDir) {
    const cmd = dirToCommand(state.activeDir);
    sendMove(cmd.throttle, cmd.steering);
  }
}

function updateMobileReadout() {
  const el = document.getElementById("md-readout");
  if (!el) return;
  const st = clamp(state.steering + state.trim, -255, 255);
  el.textContent = `T ${state.throttle} · S ${st} · trim ${state.trim}`;
}

/* ---------- API ---------- */
async function sendMove(throttle, steering) {
  try {
    const r = await fetch("/api/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ throttle, steering }),
    });
    const data = await r.json();
    if (!data.ok) {
      console.warn("MOVE failed", data);
      setStatus(false);
    }
  } catch (e) {
    console.warn("MOVE network error", e);
    setStatus(false);
  }
}

async function sendStop() {
  state.activeDir = null;
  state.moving = false;
  state.throttle = 0;
  state.steering = 0;
  const thr = document.getElementById("throttle-slider");
  const str = document.getElementById("steer-slider");
  if (thr) thr.value = 0;
  if (str) str.value = 0;
  updateMobileReadout();
  try {
    await fetch("/api/stop", { method: "POST" });
  } catch (e) {
    console.warn("STOP failed", e);
  }
}

/* ---------- Desktop d-pad / keyboard ---------- */
function dirToCommand(dir) {
  const s = getSpeed();
  switch (dir) {
    case "forward": return { throttle: s, steering: 0 };
    case "back": return { throttle: -s, steering: 0 };
    case "left": return { throttle: 0, steering: -s };
    case "right": return { throttle: 0, steering: s };
    default: return { throttle: 0, steering: 0 };
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

function bindDpad() {
  document.querySelectorAll(".drive-btn").forEach((btn) => {
    const dir = btn.dataset.dir;
    if (!dir) return;
    const onDown = (e) => {
      e.preventDefault();
      if (dir === "stop") {
        sendStop();
        return;
      }
      startDir(dir);
    };
    const onUp = (e) => {
      e.preventDefault();
      if (dir !== "stop") stopDir();
    };
    btn.addEventListener("pointerdown", onDown);
    btn.addEventListener("pointerup", onUp);
    btn.addEventListener("pointerleave", onUp);
    btn.addEventListener("pointercancel", onUp);
  });
}

const DIR_KEYS = {
  ArrowUp: "forward",
  ArrowDown: "back",
  ArrowLeft: "left",
  ArrowRight: "right",
  " ": "stop",
  Space: "stop",
  w: "forward",
  W: "forward",
  s: "back",
  S: "back",
  a: "left",
  A: "left",
  d: "right",
  D: "right",
};

const SPEED_KEYS = {
  "1": 10, "2": 20, "3": 30, "4": 40, "5": 50,
  "6": 60, "7": 70, "8": 80, "9": 90, "0": 100,
};

function onKeyDown(e) {
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
  if (dir === "stop") {
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
    .map((k) => DIR_KEYS[k])
    .filter((d) => d && d !== "stop");
  if (still.length === 0) stopDir();
  else startDir(still[still.length - 1]);
}

function bindSpeed() {
  const slider = document.getElementById("speed");
  if (!slider) return;
  slider.addEventListener("input", () => setPercent(parseInt(slider.value, 10)));
}

/* ---------- Mobile sliders ---------- */
function effectiveSteering() {
  return clamp(applyDeadband(state.steering) + state.trim, -255, 255);
}

function pushMobileCommand() {
  const thr = applyDeadband(state.throttle);
  const st = effectiveSteering();
  updateMobileReadout();
  if (thr === 0 && applyDeadband(state.steering) === 0 && state.trim === 0) {
    // fully neutral — stop motors
    if (state.moving) {
      state.moving = false;
      fetch("/api/stop", { method: "POST" }).catch(() => {});
    }
    return;
  }
  // If only trim is non-zero but sticks centered, still don't drive
  if (thr === 0 && applyDeadband(state.steering) === 0) {
    if (state.moving) {
      state.moving = false;
      fetch("/api/stop", { method: "POST" }).catch(() => {});
    }
    return;
  }
  state.moving = true;
  sendMove(thr, st);
}

function scheduleMobileSend() {
  if (state.sendTimer) return;
  state.sendTimer = setTimeout(() => {
    state.sendTimer = null;
    pushMobileCommand();
  }, 50); // ~20 Hz max
}

function bindMobileSliders() {
  const thr = document.getElementById("throttle-slider");
  const str = document.getElementById("steer-slider");
  const trim = document.getElementById("trim-slider");
  const stopBtn = document.getElementById("md-stop");

  if (thr) {
    const onThr = () => {
      state.throttle = parseInt(thr.value, 10) || 0;
      scheduleMobileSend();
    };
    thr.addEventListener("input", onThr);
    thr.addEventListener("change", onThr);
  }

  if (str) {
    const onStr = () => {
      state.steering = parseInt(str.value, 10) || 0;
      scheduleMobileSend();
    };
    str.addEventListener("input", onStr);
    str.addEventListener("change", onStr);
  }

  if (trim) {
    const onTrim = () => {
      state.trim = parseInt(trim.value, 10) || 0;
      const label = document.getElementById("trim-val");
      if (label) label.textContent = String(state.trim);
      // Re-send if already moving so trim takes effect immediately
      if (state.moving) scheduleMobileSend();
      else updateMobileReadout();
    };
    trim.addEventListener("input", onTrim);
    trim.addEventListener("change", onTrim);
  }

  if (stopBtn) {
    stopBtn.addEventListener("click", (e) => {
      e.preventDefault();
      sendStop();
    });
  }
}

/* ---------- PWA ---------- */
function registerSW() {
  if (!("serviceWorker" in navigator)) return;
  navigator.serviceWorker.register("/static/sw.js").catch((err) => {
    console.warn("SW register failed", err);
  });
}

/* ---------- Init ---------- */
document.addEventListener("DOMContentLoaded", () => {
  updateClock();
  setInterval(updateClock, 1000);
  updateSpeedUI();
  updateMobileReadout();

  bindDpad();
  bindSpeed();
  bindMobileSliders();
  registerSW();

  window.addEventListener("keydown", onKeyDown);
  window.addEventListener("keyup", onKeyUp);

  pollStatus();
  setInterval(pollStatus, 2000);

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) sendStop();
  });
  window.addEventListener("blur", () => sendStop());
});
