// Blockcraft: start-up and the main loop. This file only wires the parts together; each part lives in its own module:
//   world/    the world: blocks, terrain, generation, chunks          render/   drawing it (Three.js)
//   player/   the player's body and what it points at                 input/    keyboard, mouse and controller
//   ui/       screens, menus and the HUD                              settings.js  the player's settings
import { World } from './world/world.js';
import { BLOCK, BLOCKS, IS_SOLID, LIGHT_OF, LIGHT_PASS } from './world/blocks.js';
import { DAY_LENGTH_SECONDS, WORLD_HEIGHT } from './world/constants.js';
import { Renderer } from './render/renderer.js';
import { Player } from './player/player.js';
import { raycast } from './player/raycast.js';
import { Input } from './input/input.js';
import { Screens } from './ui/screens.js';
import { Hud } from './ui/hud.js';
import { loadSettings, saveSettings } from './settings.js';

const REACH = 5;                                // how far away a block can be touched
const PLACE_REPEAT = 0.22;                      // seconds between blocks placed while the button is held
const PHYSICS_STEP = 1 / 120;
const BREAK_SPEEDUP = 3;                        // until tools are back, everything breaks three times faster than by bare hand

// Until the inventory is rebuilt, the hotbar holds a fixed set of blocks to build with.
const STARTING_HOTBAR = [BLOCK.grass, BLOCK.dirt, BLOCK.stone, BLOCK.cobblestone, BLOCK.oak_planks, BLOCK.oak_log, BLOCK.glass, BLOCK.glowstone, BLOCK.torch];

class Game {
  constructor() {
    this.settings = loadSettings();
    this.applyUiScale();
    this.canvas = document.getElementById('view');
    this.renderer = new Renderer(this.canvas, this.settings);
    this.input = new Input(this.canvas, this.settings);
    this.screens = new Screens(document.getElementById('screens'), this.input);
    this.hud = new Hud(document.getElementById('hud'), this.renderer.textures.tiles);
    this.state = 'title';
    this.world = null;
    this.player = null;
    this.time = 0.3;                            // time of day: 0.25 is noon, 0.75 midnight
    this.hotbar = STARTING_HOTBAR.slice();
    this.selected = 0;
    this.breaking = null;                       // { x, y, z, progress } while a block is being broken
    this.placeTimer = 0;
    this.frames = { count: 0, since: performance.now(), fps: 0 };
    addEventListener('resize', () => this.renderer.resize());
    this.showTitle();
    this.last = performance.now();
    requestAnimationFrame(t => this.frame(t));
  }

  applyUiScale() { document.documentElement.style.setProperty('--ui', String(this.settings.uiScale)); }

  // ---- screens ----

  showTitle() {
    this.state = 'title';
    this.input.setMode('menu');
    this.hud.show(false);
    document.body.classList.remove('playing');
    this.screens.closeAll();
    this.screens.push(this.screens.makeScreen({
      title: 'BLOCKCRAFT', subtitle: 'THE REBUILD  ·  FOUNDATION', big: true, solid: true, noBack: true,
      items: [
        { type: 'button', label: 'New World', onPress: () => this.newWorld(), hint: 'A new world with a random seed.' },
        { type: 'button', label: 'Settings', onPress: () => this.openSettings() },
        { type: 'button', label: 'Quit', onPress: () => window.close(), hint: 'Closes the game (in the desktop app or a launcher window).' },
      ],
    }));
  }

  openSettings() {
    this.screens.push(this.screens.settingsScreen(this.settings, key => {
      saveSettings(this.settings);
      if (key === 'uiScale') this.applyUiScale();
      this.renderer.applySettings(this.settings);
    }, !this.world));
  }

  pause() {
    this.state = 'paused';
    this.hud.show(false);
    this.input.setMode('menu');
    this.breaking = null; this.hud.setBreaking(null);
    document.body.classList.remove('playing');
    this.screens.push(this.screens.makeScreen({
      title: 'Paused', onBack: () => this.resume(),
      items: [
        { type: 'button', label: 'Resume', onPress: () => this.resume() },
        { type: 'button', label: 'Settings', onPress: () => this.openSettings() },
        { type: 'button', label: 'Quit to Title', onPress: () => this.quitToTitle(), hint: 'Changes to the world are not saved yet in this build.' },
      ],
    }));
  }

  resume() {
    this.screens.closeAll();
    this.hud.show(true);
    this.state = 'playing';
    this.input.setMode('game');
    document.body.classList.add('playing');
  }

  quitToTitle() {
    this.world?.dispose();
    this.world = null;
    this.renderer.setWorld(null);
    this.showTitle();
  }

  // ---- worlds ----

  newWorld(seed = Math.floor(Math.random() * 2 ** 31)) {
    this.world?.dispose();
    this.world = new World(seed, {
      onChunkLoaded: c => this.renderer.chunkLoaded(c),
      onChunkUnloaded: c => this.renderer.chunkUnloaded(c),
      onBlockChanged: (x, y, z) => this.renderer.blockChanged(x, y, z),
      onLightChanged: (cx, cz, sy) => this.renderer.lightChanged(cx, cz, sy),
    });
    this.renderer.setWorld(this.world);
    const spawn = this.world.findSpawn();
    this.player = new Player(spawn.x, spawn.y, spawn.z);
    this.time = 0.3;
    this.screens.closeAll();
    this.loading = this.screens.loadingScreen('Building the world…');
    this.screens.push(this.loading);
    this.state = 'loading';
    this.hud.setHotbar(this.hotbar, this.selected);
  }

  // ---- the loop ----

  frame(now) {
    requestAnimationFrame(t => this.frame(t));
    const dt = Math.min(0.25, (now - this.last) / 1000);
    this.last = now;
    this.input.update(dt);
    this.screens.update();

    if (this.world && this.player) {
      this.world.update(this.player.x, this.player.z, this.settings.renderDistance, this.state === 'loading' ? 12 : 4);
      if (this.state === 'loading') this.updateLoading();
      if (this.state === 'playing') this.updatePlaying(dt);
      const p = this.player, bob = this.state === 'playing' && this.settings.viewBob && p.onGround ? Math.sin(p.walked * 2.2) * 0.035 : 0;
      this.renderer.render({ x: p.x, y: p.eyeY + bob, z: p.z, yaw: p.yaw, pitch: p.pitch }, this.time, this.state === 'playing' ? this.target : null);
    } else {
      this.renderer.gl.setClearColor(0x0b0d10);
      this.renderer.gl.clear();
    }
    this.countFrame(now);
  }

  updateLoading() {
    // wait until the ground round the spawn point is there and drawn, then drop the player onto it
    const p = this.player, need = 3, pcx = Math.floor(p.x / 16), pcz = Math.floor(p.z / 16), total = (need * 2 + 1) ** 2;
    let have = 0;
    for (let dx = -need; dx <= need; dx++) for (let dz = -need; dz <= need; dz++) if (this.world.getChunk(pcx + dx, pcz + dz)) have++;
    this.loading.setProgress(have / total);
    if (have === total && this.renderer.isAreaMeshed(pcx, pcz, need - 1)) {
      while (this.world.isSolid(Math.floor(p.x), Math.floor(p.y), Math.floor(p.z)) && p.y < WORLD_HEIGHT) p.y++;
      this.hud.show(true);
      this.resume();
      this.hud.toast(`Seed ${this.world.seed}`);
    }
  }

  updatePlaying(dt) {
    const s = this.input.state;
    if (s.pause) { this.pause(); return; }
    this.time = (this.time + dt / DAY_LENGTH_SECONDS) % 1;
    // physics in fixed steps of 1/120 s: the same movement at any frame rate (up to a quarter of a second per frame)
    this.player.look(s);
    this.physicsTime = Math.min(0.25, (this.physicsTime ?? 0) + dt);
    while (this.physicsTime >= PHYSICS_STEP) { this.player.step(PHYSICS_STEP, s, this.world); this.physicsTime -= PHYSICS_STEP; }
    if (s.fly) this.hud.toast(this.player.flying ? 'Flying' : 'Walking', 1200);

    // hotbar
    if (s.hotbar || s.hotbarSlot >= 0) {
      this.selected = s.hotbarSlot >= 0 ? s.hotbarSlot : (this.selected + s.hotbar + this.hotbar.length * 4) % this.hotbar.length;
      this.hud.select(this.selected);
    }

    // what the player points at
    const p = this.player, d = p.lookDirection();
    this.target = raycast(this.world, p.x, p.eyeY, p.z, d.x, d.y, d.z, REACH);
    this.updateBreaking(dt, s);
    this.updatePlacing(dt, s);
  }

  /** Hold the attack button on a block to break it. The time it takes depends on the block's hardness. */
  updateBreaking(dt, s) {
    const t = this.target;
    if (!s.attack || !t) { this.breaking = null; this.hud.setBreaking(null); return; }
    if (!this.breaking || this.breaking.x !== t.x || this.breaking.y !== t.y || this.breaking.z !== t.z) this.breaking = { x: t.x, y: t.y, z: t.z, progress: 0 };
    const hardness = BLOCKS[t.id].hardness / BREAK_SPEEDUP;
    if (!isFinite(hardness)) { this.hud.setBreaking(null); return; }
    this.breaking.progress += hardness > 0 ? dt / hardness : 1;
    this.hud.setBreaking(Math.min(1, this.breaking.progress));
    if (this.breaking.progress >= 1) {
      this.world.setBlock(t.x, t.y, t.z, BLOCK.air);
      if (this.world.getBlock(t.x, t.y + 1, t.z) === BLOCK.torch) this.world.setBlock(t.x, t.y + 1, t.z, BLOCK.air);   // it stood on this
      this.breaking = null;
      this.hud.setBreaking(null);
    }
  }

  /** Press (or hold) use to place the selected block against the face being pointed at. */
  updatePlacing(dt, s) {
    this.placeTimer -= dt;
    if (!s.use) { this.placeTimer = 0; return; }
    if (!s.usePressed && this.placeTimer > 0) return;
    this.placeTimer = PLACE_REPEAT;
    const t = this.target;
    if (!t) return;
    const x = t.x + t.nx, y = t.y + t.ny, z = t.z + t.nz, id = this.hotbar[this.selected];
    const here = this.world.getBlock(x, y, z);
    if (here !== BLOCK.air && here !== BLOCK.water && here !== BLOCK.tall_grass) return;
    if (id === BLOCK.torch) {
      if (t.ny !== 1 || !IS_SOLID[t.id]) return;                  // torches stand on top of solid blocks (wall torches come later)
    } else if (this.player.overlaps(x, y, z)) return;
    this.world.setBlock(x, y, z, id);
  }

  countFrame(now) {
    const f = this.frames;
    f.count++;
    if (now - f.since >= 500) {
      f.fps = Math.round((f.count * 1000) / (now - f.since)); f.count = 0; f.since = now;
      if (this.settings.showFps && this.state === 'playing') {
        const r = this.renderer, p = this.player;
        this.hud.setFps(`${f.fps} fps\n${r.gl.domElement.width} x ${r.gl.domElement.height}\n${r.stats.sections} sections, ${(r.stats.triangles / 1000).toFixed(0)}k triangles\n` +
          `x ${p.x.toFixed(1)}  y ${p.y.toFixed(1)}  z ${p.z.toFixed(1)}`);
      } else this.hud.setFps('');
    }
  }
}

window.game = new Game();
window.BLOCK = BLOCK;            // (block ids by key, for tests and the browser console)
window.LIGHT_TABLES = { LIGHT_OF, LIGHT_PASS };   // for tests: light rules
