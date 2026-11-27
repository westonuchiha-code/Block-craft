// Player settings, kept in this browser (or the desktop app) between sessions.
//
// The defaults assume a modern gaming PC (a GeForce RTX 3070 class card) on a large 4K screen: the picture is drawn at the
// screen's full resolution, with anti-aliasing, and the world is visible to 192 blocks. Everything can be lowered.

const STORE_KEY = 'blockcraft.settings';

export const SETTINGS = {
  renderDistance:   { label: 'View distance', default: 12, min: 4, max: 32, step: 1, format: v => `${v} chunks (${v * 16} blocks)` },
  renderScale:      { label: 'Resolution', default: 1, min: 0.5, max: 2, step: 0.125, format: v => (v === 1 ? 'Native (100%)' : `${Math.round(v * 100)}%`) },
  fov:              { label: 'Field of view', default: 75, min: 55, max: 105, step: 1, format: v => `${v}°` },
  uiScale:          { label: 'Menu and HUD size', default: 1, min: 0.7, max: 1.6, step: 0.05, format: v => `${Math.round(v * 100)}%` },
  stickSensitivity: { label: 'Controller look speed', default: 1, min: 0.3, max: 2.5, step: 0.05, format: v => `${Math.round(v * 100)}%` },
  mouseSensitivity: { label: 'Mouse look speed', default: 1, min: 0.2, max: 3, step: 0.05, format: v => `${Math.round(v * 100)}%` },
  invertY:          { label: 'Invert look up and down', default: false },
  viewBob:          { label: 'View bob while walking', default: true },
  showFps:          { label: 'Show frame rate', default: false },
};

export function loadSettings() {
  const out = {};
  for (const [k, s] of Object.entries(SETTINGS)) out[k] = s.default;
  try {
    const saved = JSON.parse(localStorage.getItem(STORE_KEY) || '{}');
    for (const k of Object.keys(SETTINGS)) if (k in saved && typeof saved[k] === typeof out[k]) out[k] = saved[k];
  } catch { /* no storage, or damaged: use the defaults */ }
  return out;
}

export function saveSettings(settings) {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(settings)); } catch { /* not stored; they still apply now */ }
}
