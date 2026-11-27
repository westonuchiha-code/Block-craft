// All input, from the keyboard and mouse or a controller, turned into the same set of actions.
//
// Two modes:
//   'game'  movement, looking, and actions (jump, break, place, hotbar, pause)
//   'menu'  navigation only: up / down / left / right / confirm / back / previous tab / next tab, with auto-repeat while held.
//           Menus are driven with the D-pad (or left stick, or arrow keys); there is never an on-screen cursor to steer.
//
// The controller uses the standard layout (Xbox names):
//   left stick  move            right stick  look            A  jump / confirm       B  back
//   RT          break / attack  LT           place / use      LB RB  hotbar / tabs    Start  pause menu
//   L3 (click)  sprint          R3 (click)   sneak            D-pad  menus

export const NAV = ['up', 'down', 'left', 'right', 'confirm', 'back', 'tabPrev', 'tabNext'];

const PAD = { A: 0, B: 1, X: 2, Y: 3, LB: 4, RB: 5, LT: 6, RT: 7, BACK: 8, START: 9, L3: 10, R3: 11, UP: 12, DOWN: 13, LEFT: 14, RIGHT: 15 };
const DEADZONE = 0.16;
const REPEAT_DELAY = 0.38, REPEAT_RATE = 0.085;   // seconds: hold a direction and it repeats

const KEY_NAV = {
  ArrowUp: 'up', KeyW: 'up', ArrowDown: 'down', KeyS: 'down', ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right',
  Enter: 'confirm', Space: 'confirm', Escape: 'back', Backspace: 'back', KeyQ: 'tabPrev', KeyE: 'tabNext',
};

/** Apply a round deadzone and a gentle curve, so small stick movements are fine and full tilt is full speed. */
function stick(x, y) {
  const len = Math.hypot(x, y);
  if (len < DEADZONE) return [0, 0];
  const k = Math.min(1, (len - DEADZONE) / (1 - DEADZONE));
  const curved = k * k * 0.6 + k * 0.4;
  return [(x / len) * curved, (y / len) * curved];
}

export class Input {
  constructor(canvas, settings) {
    this.canvas = canvas;
    this.settings = settings;
    this.mode = 'menu';
    this.keys = new Set();               // keyboard keys held (by code)
    this.mouseButtons = new Set();
    this.mouseDX = 0; this.mouseDY = 0;
    this.wheel = 0;
    this.lastDevice = 'keyboard';        // 'keyboard' or 'gamepad': which button names to show
    this.pad = null;
    this.padPrev = [];
    this.navQueue = [];
    this.navHeld = new Map();            // nav action held on the pad / keyboard -> seconds until it repeats
    this.pressed = new Set();            // gameplay buttons that went down this frame
    this.state = this.emptyState();
    this.listen();
  }

  emptyState() {
    return { moveX: 0, moveZ: 0, lookX: 0, lookY: 0, jump: false, sprint: false, sneak: false, attack: false, use: false,
             usePressed: false, attackPressed: false, hotbar: 0, hotbarSlot: -1, pause: false, sprintToggle: false, sneakToggle: false, fly: false };
  }

  listen() {
    addEventListener('keydown', e => {
      if (e.code === 'F11') return;                                   // leave full screen to the browser / app
      this.lastDevice = 'keyboard';
      if (!e.repeat) this.pressed.add(e.code);
      this.keys.add(e.code);
      if (this.mode === 'menu' && KEY_NAV[e.code]) {
        // text boxes keep their own keys (typing a seed or a name)
        if (document.activeElement?.tagName === 'INPUT' && !['Escape', 'Enter', 'ArrowUp', 'ArrowDown'].includes(e.code)) return;
        this.navQueue.push(KEY_NAV[e.code]);
        e.preventDefault();
      }
      if (this.mode === 'game' && ['Space', 'Tab', 'Slash'].includes(e.code)) e.preventDefault();
    });
    addEventListener('keyup', e => this.keys.delete(e.code));
    addEventListener('blur', () => { this.keys.clear(); this.mouseButtons.clear(); });
    this.canvas.addEventListener('mousedown', e => {
      this.lastDevice = 'keyboard';
      if (this.mode === 'game' && document.pointerLockElement !== this.canvas) { this.lockPointer(); return; }
      this.mouseButtons.add(e.button); this.pressed.add(`Mouse${e.button}`);
    });
    addEventListener('mouseup', e => this.mouseButtons.delete(e.button));
    addEventListener('mousemove', e => {
      if (document.pointerLockElement !== this.canvas) return;
      this.mouseDX += e.movementX; this.mouseDY += e.movementY;
    });
    addEventListener('wheel', e => { if (this.mode === 'game') this.wheel += Math.sign(e.deltaY); }, { passive: true });
    addEventListener('contextmenu', e => e.preventDefault());
  }

  lockPointer() { this.canvas.requestPointerLock?.()?.catch?.(() => {}); }
  unlockPointer() { if (document.pointerLockElement) document.exitPointerLock(); }

  setMode(mode) {
    this.mode = mode;
    this.navQueue.length = 0;
    this.navHeld.clear();
    if (mode === 'game') this.lockPointer(); else this.unlockPointer();
  }

  /** Read the controller and turn everything held and pressed into this frame's state. Call once per frame. */
  update(dt) {
    const pads = navigator.getGamepads ? [...navigator.getGamepads()].filter(Boolean) : [];
    this.pad = pads.find(p => p.mapping === 'standard') || pads[0] || null;
    const btn = i => !!this.pad?.buttons[i]?.pressed;
    const btnDown = i => btn(i) && !this.padPrev[i];
    if (this.pad && this.pad.buttons.some(b => b.pressed)) this.lastDevice = 'gamepad';
    const axes = this.pad ? this.pad.axes : [0, 0, 0, 0];
    const [lx, ly] = stick(axes[0] || 0, axes[1] || 0);
    const [rx, ry] = stick(axes[2] || 0, axes[3] || 0);
    if (lx || ly || rx || ry) this.lastDevice = 'gamepad';

    if (this.mode === 'menu') this.updateMenu(dt, btn, btnDown, ly, lx);
    else this.updateGame(dt, btn, btnDown, lx, ly, rx, ry);

    this.padPrev = this.pad ? this.pad.buttons.map(b => b.pressed) : [];
    this.pressed.clear();
    this.mouseDX = this.mouseDY = this.wheel = 0;
  }

  updateGame(dt, btn, btnDown, lx, ly, rx, ry) {
    const k = c => this.keys.has(c), s = this.emptyState(), set = this.settings;
    s.moveX = (k('KeyD') ? 1 : 0) - (k('KeyA') ? 1 : 0) + lx;
    s.moveZ = (k('KeyS') ? 1 : 0) - (k('KeyW') ? 1 : 0) + ly;
    const len = Math.hypot(s.moveX, s.moveZ);
    if (len > 1) { s.moveX /= len; s.moveZ /= len; }
    const invert = set.invertY ? -1 : 1;
    const mouse = 0.0022 * set.mouseSensitivity;
    const stickRate = 3.4 * set.stickSensitivity * dt;
    s.lookX = -this.mouseDX * mouse - rx * stickRate;
    s.lookY = -this.mouseDY * mouse * invert - ry * stickRate * invert;
    s.jump = k('Space') || btn(PAD.A);
    s.sprint = k('ShiftLeft') || k('ControlLeft');
    s.sneak = k('KeyC');
    s.sprintToggle = btnDown(PAD.L3);
    s.sneakToggle = btnDown(PAD.R3);
    s.attack = this.mouseButtons.has(0) || btn(PAD.RT);
    s.use = this.mouseButtons.has(2) || btn(PAD.LT);
    s.attackPressed = this.pressed.has('Mouse0') || btnDown(PAD.RT);
    s.usePressed = this.pressed.has('Mouse2') || btnDown(PAD.LT);
    s.hotbar = this.wheel + (btnDown(PAD.RB) ? 1 : 0) - (btnDown(PAD.LB) ? 1 : 0);
    for (let i = 1; i <= 9; i++) if (this.pressed.has(`Digit${i}`)) s.hotbarSlot = i - 1;
    s.pause = this.pressed.has('Escape') || btnDown(PAD.START);
    s.fly = this.pressed.has('KeyF') || btnDown(PAD.Y);
    this.state = s;
  }

  updateMenu(dt, btn, btnDown, ly, lx) {
    this.state = this.emptyState();
    if (!this.pad) return;
    // buttons: one action per press
    if (btnDown(PAD.A)) this.navQueue.push('confirm');
    if (btnDown(PAD.B) || btnDown(PAD.START)) this.navQueue.push('back');
    if (btnDown(PAD.LB)) this.navQueue.push('tabPrev');
    if (btnDown(PAD.RB)) this.navQueue.push('tabNext');
    // directions: D-pad or left stick, repeating while held
    const held = {
      up: btn(PAD.UP) || ly < -0.6, down: btn(PAD.DOWN) || ly > 0.6,
      left: btn(PAD.LEFT) || lx < -0.6, right: btn(PAD.RIGHT) || lx > 0.6,
    };
    for (const [dir, on] of Object.entries(held)) {
      if (!on) { this.navHeld.delete(dir); continue; }
      if (!this.navHeld.has(dir)) { this.navQueue.push(dir); this.navHeld.set(dir, REPEAT_DELAY); continue; }
      const t = this.navHeld.get(dir) - dt;
      if (t <= 0) { this.navQueue.push(dir); this.navHeld.set(dir, REPEAT_RATE); } else this.navHeld.set(dir, t);
    }
  }

  /** Menu navigation actions since the last call. */
  takeNav() { const q = this.navQueue; this.navQueue = []; return q; }

  /** Name of a button for prompts on screen, for whichever device is in use. */
  label(action) {
    const pad = { confirm: 'A', back: 'B', tabs: 'LB / RB', jump: 'A', attack: 'RT', use: 'LT', pause: 'START', fly: 'Y' };
    const keys = { confirm: 'ENTER', back: 'ESC', tabs: 'Q / E', jump: 'SPACE', attack: 'LEFT CLICK', use: 'RIGHT CLICK', pause: 'ESC', fly: 'F' };
    return (this.lastDevice === 'gamepad' ? pad : keys)[action] ?? action;
  }
}
