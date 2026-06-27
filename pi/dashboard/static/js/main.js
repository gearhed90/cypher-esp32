/**
 * Cypher Dashboard - Minimal client-side enhancements
 * - Live clock (UTC for operational consistency)
 * - Stream refresh utility
 */

function updateClock() {
  const clockEl = document.getElementById('clock');
  if (!clockEl) return;

  const now = new Date();
  // Use UTC for a more "synthetic / mission time" feel
  const hours = String(now.getUTCHours()).padStart(2, '0');
  const minutes = String(now.getUTCMinutes()).padStart(2, '0');
  const seconds = String(now.getUTCSeconds()).padStart(2, '0');

  clockEl.textContent = `${hours}:${minutes}:${seconds} UTC`;
}

// Refresh the camera stream by forcing a new request
function refreshStream() {
  const img = document.getElementById('camera-stream');
  if (!img) return;

  const currentSrc = img.src.split('?')[0]; // remove any existing cache buster
  const timestamp = Date.now();
  img.src = `${currentSrc}?t=${timestamp}`;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  // Start the clock
  updateClock();
  setInterval(updateClock, 1000);

  // Optional: auto-refresh stream every 60s in case of frozen MJPEG
  // Uncomment if desired:
  // setInterval(() => {
  //   const img = document.getElementById('camera-stream');
  //   if (img && img.complete) refreshStream();
  // }, 60000);
});