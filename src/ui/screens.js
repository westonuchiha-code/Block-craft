// The game's screens: title, pause, settings and loading. Each is a full-window layer with a heading, a menu and the button
// prompts for whichever device is in use.
import { Menu } from './menu.js';
import { SETTINGS } from '../settings.js';

export class Screens {
  /**
   * @param {HTMLElement} root  where screens are added
   * @param {import('../input/input.js').Input} input
   */
  constructor(root, input) {
    this.root = root;
    this.input = input;
    this.stack = [];          // open screens, the top one has control
  }

  get active() { return this.stack[this.stack.length - 1] ?? null; }

  /** Show a screen over whatever is open. */
  push(screen) {
    this.active?.el.classList.remove('open');
    this.stack.push(screen);
    screen.el.classList.add('open');
    this.updatePrompts();
  }

  /** Close the top screen and go back to the one under it. */
  pop() {
    const s = this.stack.pop();
    if (s) { s.el.classList.remove('open'); s.onClose?.(); }
    this.active?.el.classList.add('open');
    this.active?.menu?.refresh();
    this.updatePrompts();
  }

  closeAll() { while (this.stack.length) this.pop(); }

  /** Pass this frame's navigation to the top screen. */
  update() {
    const nav = this.input.takeNav();
    const s = this.active;
    if (!s) return;
    for (const a of nav) s.menu?.nav(a);
    if (this.promptDevice !== this.input.lastDevice) this.updatePrompts();
  }

  updatePrompts() {
    this.promptDevice = this.input.lastDevice;
    for (const s of this.stack) {
      const el = s.el.querySelector('.prompts');
      if (!el) continue;
      const parts = [[this.input.label('confirm'), 'Select'], ...(s.noBack ? [] : [[this.input.label('back'), 'Back']])];
      el.innerHTML = parts.map(([k, v]) => `<span><b>${k}</b>${v}</span>`).join('');
    }
  }

  // ---- building screens ----

  /** A screen with a title, an optional line under it, and a menu. */
  makeScreen({ title, subtitle, items, onBack, big = false, solid = false, noBack = false }) {
    const el = document.createElement('div');
    el.className = `screen${solid ? ' solid' : ''}`;
    el.innerHTML = `<div class="${big ? 'title' : 'heading'}"></div>${subtitle ? '<div class="subtitle"></div>' : ''}<div class="panel"></div><div class="hint-text"></div><div class="prompts"></div>`;
    el.querySelector(big ? '.title' : '.heading').textContent = title;
    if (subtitle) el.querySelector('.subtitle').textContent = subtitle;
    this.root.appendChild(el);
    const screen = { el, noBack };
    screen.menu = new Menu(el.querySelector('.panel'), items, { onBack, hintEl: el.querySelector('.hint-text') });
    screen.onClose = () => el.remove();
    return screen;
  }

  /** The settings screen: every setting as a row, changed with left / right, applied at once. */
  settingsScreen(settings, onChange, solid = false) {
    const items = Object.entries(SETTINGS).map(([key, def]) => typeof def.default === 'boolean'
      ? { type: 'toggle', label: def.label, get: () => settings[key], set: v => { settings[key] = v; onChange(key); } }
      : { type: 'range', label: def.label, min: def.min, max: def.max, step: def.step, format: def.format,
          get: () => settings[key], set: v => { settings[key] = v; onChange(key); } });
    items.push({ type: 'button', label: 'Done', onPress: () => this.pop() });
    return this.makeScreen({ title: 'Settings', items, onBack: () => this.pop(), solid });
  }

  /** A full-window loading screen with a progress bar. */
  loadingScreen(text) {
    const el = document.createElement('div');
    el.className = 'screen solid';
    el.innerHTML = '<div class="heading"></div><div class="loading-bar"><i></i></div>';
    el.querySelector('.heading').textContent = text;
    this.root.appendChild(el);
    const screen = { el, noBack: true, setProgress: p => { el.querySelector('.loading-bar i').style.width = `${Math.round(p * 100)}%`; } };
    screen.onClose = () => el.remove();
    return screen;
  }
}
