/**
 * Cypher Dashboard — client logic
 * Drive + pan/tilt + status
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
  holdTimer: null,
  lastThr: 0,
  lastStr: 0,
  ptRepeatTimer: null,
  ptRepeatKind: null,
  ptRepeatDelta: 0,
};

const DEADBAND = 8;
const PT_REPEAT_MS = 120;
const MOVE_HOLD_MS = 400;

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

function stopHoldRepeat() {
  if (state.holdTimer) {
    clearInterval(state.holdTimer);
    state.holdTimer = null;
  }
}

function startHoldRepeat(throttle, steering) {
  state.lastThr = throttle;
  state.lastStr = steering;
  if (state.holdTimer) return;
  state.holdTimer = setInterval(() => {
    if (!state.moving && !state.activeDir) {
      stopHoldRepeat();
      return;
    }
    sendMove(state.lastThr, state.lastStr, true);
  }, MOVE_HOLD_MS);
}

async function sendMove(throttle, steering, fromHold) {
  state.lastThr = throttle;
  state.lastStr = steering;
  if (!fromHold) startHoldRepeat(throttle, steering);
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
  stopHoldRepeat();
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

async function sendPanTilt(body) {
  try {
    const r = await fetch("/api/pan_tilt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return await r.json();
  } catch (e) {
    console.warn("pan_tilt failed", e);
    return { ok: false };
  }
}

async function centerPanTilt() {
  try {
    await fetch("/api/pan_tilt/center", { method: "POST" });
  } catch (e) {
    console.warn("center failed", e);
  }
}

function stopPtRepeat() {
  if (state.ptRepeatTimer) {
    clearInterval(state.ptRepeatTimer);
    state.ptRepeatTimer = null;
  }
  state.ptRepeatKind = null;
  state.ptRepeatDelta = 0;
}

function startPtRepeat(kind, delta) {
  stopPtRepeat();
  state.ptRepeatKind = kind;
  state.ptRepeatDelta = delta;
  const fire = () => {
    if (kind === "pan") sendPanTilt({ pan_delta: delta });
    else if (kind === "tilt") sendPanTilt({ tilt_delta: delta });
  };
  fire();
  state.ptRepeatTimer = setInterval(fire, PT_REPEAT_MS);
}

function bindPanTilt() {
  document.querySelectorAll("[data-pt]").forEach((btn) => {
    btn.style.userSelect = "none";
    btn.style.webkitUserSelect = "none";
    btn.style.touchAction = "none";

    const kind = btn.dataset.pt;

    const onDown = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (kind === "center") {
        centerPanTilt();
        return;
      }
      const delta = parseFloat(btn.dataset.delta || "0");
      if (kind === "pan" || kind === "tilt") {
        startPtRepeat(kind, delta);
      }
    };

    const onUp = (e) => {
      e.preventDefault();
      stopPtRepeat();
    };

    btn.addEventListener("pointerdown", onDown);
    btn.addEventListener("pointerup", onUp);
    btn.addEventListener("pointercancel", onUp);
    btn.addEventListener("contextmenu", (e) => e.preventDefault());
  });
}

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
  state.activeDir = dir;
  const cmd = dirToCommand(dir);
  state.moving = true;
  sendMove(cmd.throttle, cmd.steering);
}

function stopDir() {
  if (state.activeDir === null && !state.moving) return;
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

function effectiveSteering() {
  return clamp(applyDeadband(state.steering) + state.trim, -255, 255);
}

function pushMobileCommand() {
  const thr = applyDeadband(state.throttle);
  const rawSteer = applyDeadband(state.steering);
  updateMobileReadout();
  if (thr === 0 && rawSteer === 0) {
    if (state.moving || state.holdTimer) sendStop();
    return;
  }
  state.moving = true;
  sendMove(thr, effectiveSteering());
}

function scheduleMobileSend() {
  if (state.sendTimer) return;
  state.sendTimer = setTimeout(() => {
    state.sendTimer = null;
    pushMobileCommand();
  }, 50);
}

function springAxis(axis) {
  if (axis === "throttle") {
    state.throttle = 0;
    const el = document.getElementById("throttle-slider");
    if (el) el.value = 0;
  } else if (axis === "steer") {
    state.steering = 0;
    const el = document.getElementById("steer-slider");
    if (el) el.value = 0;
  }
  updateMobileReadout();
  pushMobileCommand();
}

function bindSpringReturn(el, axis) {
  if (!el) return;
  el.addEventListener("pointerup", (e) => {
    e.preventDefault();
    springAxis(axis);
  });
  el.addEventListener("pointercancel", (e) => {
    e.preventDefault();
    springAxis(axis);
  });
}

function bindMobileSliders() {
  const thr = document.getElementById("throttle-slider");
  const str = document.getElementById("steer-slider");
  const trim = document.getElementById("trim-slider");
  const stopBtn = document.getElementById("md-stop");

  if (thr) {
    thr.addEventListener("input", () => {
      state.throttle = parseInt(thr.value, 10) || 0;
      scheduleMobileSend();
    });
    bindSpringReturn(thr, "throttle");
  }
  if (str) {
    str.addEventListener("input", () => {
      state.steering = parseInt(str.value, 10) || 0;
      scheduleMobileSend();
    });
    bindSpringReturn(str, "steer");
  }
  if (trim) {
    const onTrim = () => {
      state.trim = parseInt(trim.value, 10) || 0;
      const label = document.getElementById("trim-val");
      if (label) label.textContent = String(state.trim);
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

function registerSW() {
  if (!("serviceWorker" in navigator)) return;
  navigator.serviceWorker.register("/static/sw.js").catch(() => {});
}

document.addEventListener("DOMContentLoaded", () => {
  updateClock();
  setInterval(updateClock, 1000);
  updateSpeedUI();
  updateMobileReadout();

  bindDpad();
  bindSpeed();
  bindMobileSliders();
  bindPanTilt();
  registerSW();

  window.addEventListener("keydown", onKeyDown);
  window.addEventListener("keyup", onKeyUp);

  pollStatus();
  setInterval(pollStatus, 2000);

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      sendStop();
      stopPtRepeat();
    }
  });
});
