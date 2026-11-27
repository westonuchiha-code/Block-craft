// Light: how bright each block of the world is, from the sky and from glowing blocks. Two levels per block, 0-15 each, as in
// Minecraft:
//   sky light    15 in the open. It falls straight down through clear blocks (air, glass, plants) without fading, and loses 1
//                for each step sideways, and for each step down through water or leaves. So a cave mouth is bright, and the
//                tunnel behind it darkens a step per block.
//   block light  a glowing block shines at its own level (glowstone and lava 15, a torch 14) and loses 1 per step.
// Each chunk section keeps one byte per block: sky light in the high four bits, block light in the low four. A section with no
// array (null) is open sky (sky 15, no block light): the empty air above the land.
//
// Light is worked out on the main thread with flood fills:
//   lightChunk    when a chunk arrives: fill it from the sky and its glowing blocks, and let the light of the chunks already
//                 round it flow in across the borders (and its own flow out to them)
//   blockChanged  when a block changes: take away the light that came through or from that spot, then fill back in from the
//                 light that is left round it
// Every section whose light changed is reported, so it can be drawn again.
import { CHUNK_SIZE as S, SECTIONS_PER_CHUNK, WORLD_HEIGHT } from './constants.js';
import { LIGHT_OF, LIGHT_PASS } from './blocks.js';
import { sectionIndex } from './chunk.js';

const OPEN_SKY = 0xF0;               // the light byte of open air: sky 15, no block light
const SKY = 0, GLOW = 1;             // the two channels
const DIRS = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
const DOWN = 3;

const level = (byte, ch) => (ch === SKY ? byte >> 4 : byte & 15);

export class Lighting {
  /**
   * @param {import('./world.js').World} world
   * @param {(cx: number, cz: number, sy: number) => void} onSectionChanged  called for each section whose light changed
   */
  constructor(world, onSectionChanged) {
    this.world = world;
    this.onSectionChanged = onSectionChanged;
    this.changed = new Set();        // "cx,cz,sy" keys changed during the current fill
    this.quiet = null;               // a chunk whose changes are not reported (one being lit for the first time is drawn anyway)
    this.lastChunk = null;
  }

  // ---- reading and writing one block's light ----

  chunkAt(x, z) {
    const cx = Math.floor(x / S), cz = Math.floor(z / S), c = this.lastChunk;
    if (c && c.cx === cx && c.cz === cz) return c;
    const found = this.world.getChunk(cx, cz);
    if (found) this.lastChunk = found;
    return found;
  }

  /** The light byte at a spot (sky << 4 | block). Above the world is open sky; below it and in unloaded chunks is dark. */
  get(x, y, z) {
    if (y >= WORLD_HEIGHT) return OPEN_SKY;
    if (y < 0) return 0;
    const c = this.chunkAt(x, z);
    if (!c) return 0;
    const s = c.light[y >> 4];
    return s ? s[sectionIndex(x - c.cx * S, y & 15, z - c.cz * S)] : OPEN_SKY;
  }

  set(c, x, y, z, ch, value) {
    const lx = x - c.cx * S, ly = y & 15, lz = z - c.cz * S, sy = y >> 4;
    let s = c.light[sy];
    if (!s) s = c.light[sy] = new Uint8Array(S * S * S).fill(OPEN_SKY);
    const i = sectionIndex(lx, ly, lz);
    s[i] = ch === SKY ? (value << 4) | (s[i] & 15) : (s[i] & 0xF0) | value;
    if (c === this.quiet) return;
    // the mesher reads the light one block beyond a section, so a change on a section's edge redraws the section beside it too
    this.note(c.cx, c.cz, sy);
    if (lx === 0) this.note(c.cx - 1, c.cz, sy); else if (lx === S - 1) this.note(c.cx + 1, c.cz, sy);
    if (lz === 0) this.note(c.cx, c.cz - 1, sy); else if (lz === S - 1) this.note(c.cx, c.cz + 1, sy);
    if (ly === 0 && sy > 0) this.note(c.cx, c.cz, sy - 1); else if (ly === 15 && sy < SECTIONS_PER_CHUNK - 1) this.note(c.cx, c.cz, sy + 1);
  }

  /** A chunk left the world: forget it if it is the one remembered for quick lookups. */
  forget(chunk) { if (this.lastChunk === chunk) this.lastChunk = null; }

  note(cx, cz, sy) { this.changed.add(`${cx},${cz},${sy}`); }

  report() {
    for (const key of this.changed) { const [cx, cz, sy] = key.split(',').map(Number); this.onSectionChanged(cx, cz, sy); }
    this.changed.clear();
  }

  // ---- a new chunk ----

  /** Light a chunk that has just arrived. Its neighbours that are already lit share light with it across the borders. */
  lightChunk(chunk) {
    const top = chunk.topSection();
    chunk.light = new Array(SECTIONS_PER_CHUNK).fill(null);
    for (let sy = 0; sy <= top; sy++) chunk.light[sy] = new Uint8Array(S * S * S);
    const x0 = chunk.cx * S, z0 = chunk.cz * S, roof = (top + 1) * S;
    const sky = [], glow = [];
    this.quiet = chunk;
    this.lastChunk = null;
    this.world.chunks.set(`${chunk.cx},${chunk.cz}`, chunk);      // from here on the chunk is part of the world

    // open sky: every block above the column's sky top is 15
    for (let lz = 0; lz < S; lz++) for (let lx = 0; lx < S; lx++) {
      const st = chunk.skyTop[lz * S + lx];
      for (let y = st; y < roof; y++) chunk.light[y >> 4][sectionIndex(lx, y & 15, lz)] = OPEN_SKY;
    }
    // where the sky meets cover (the block under the sky top, or a darker column beside), the fill starts
    const skyTopAt = (x, z) => {
      const c = this.chunkAt(x, z);
      return c ? c.skyTop[(z - c.cz * S) * S + (x - c.cx * S)] : null;
    };
    for (let lz = 0; lz < S; lz++) for (let lx = 0; lx < S; lx++) {
      const x = x0 + lx, z = z0 + lz, st = chunk.skyTop[lz * S + lx];
      let reach = st;
      for (const [dx, , dz] of [DIRS[0], DIRS[1], DIRS[4], DIRS[5]]) {
        const nst = skyTopAt(x + dx, z + dz);
        if (nst !== null && nst > reach) reach = nst;
      }
      for (let y = st; y <= reach; y++) sky.push(x, y, z);
    }
    // glowing blocks
    for (let sy = 0; sy <= top; sy++) {
      const ids = chunk.sections[sy];
      if (!ids) continue;
      for (let i = 0; i < ids.length; i++) {
        const glowLevel = LIGHT_OF[ids[i]];
        if (!glowLevel) continue;
        const lx = i & 15, lz = (i >> 4) & 15, ly = i >> 8;
        chunk.light[sy][i] = (chunk.light[sy][i] & 0xF0) | glowLevel;
        glow.push(x0 + lx, sy * S + ly, z0 + lz);
      }
    }

    this.spread(sky, SKY);
    this.spread(glow, GLOW);

    // light from the neighbours: their border blocks flow in
    const inflow = [[], []];
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const n = this.world.getChunk(chunk.cx + dx, chunk.cz + dz);
      if (!n || !n.light) continue;
      const nTop = Math.max(top, n.topSection()), height = (nTop + 1) * S;
      for (let k = 0; k < S; k++) {
        const lx = dx === 1 ? 0 : dx === -1 ? S - 1 : k, lz = dz === 1 ? 0 : dz === -1 ? S - 1 : k;
        const x = n.cx * S + lx, z = n.cz * S + lz;
        for (let y = 0; y < height; y++) {
          const s = n.light[y >> 4], b = s ? s[sectionIndex(lx, y & 15, lz)] : OPEN_SKY;
          if ((b >> 4) > 1) inflow[SKY].push(x, y, z);
          if ((b & 15) > 1) inflow[GLOW].push(x, y, z);
        }
      }
    }
    this.spread(inflow[SKY], SKY);
    this.spread(inflow[GLOW], GLOW);
    this.quiet = null;
    this.report();
  }

  // ---- a changed block ----

  /** A block changed (the world has already stored it): put its light right. */
  blockChanged(x, y, z) {
    const c = this.chunkAt(x, z);
    if (!c || !c.light) return;
    const id = this.world.getBlock(x, y, z), byte = this.get(x, y, z);
    for (const ch of [SKY, GLOW]) {
      const refill = [];
      // take away what this spot held, and everything that got its light through here
      const old = level(byte, ch);
      if (old) { this.set(c, x, y, z, ch, 0); this.unspread([x, y, z, old], ch, refill); }
      // what this spot gives now: its own glow, or (if light passes) whatever its neighbours bring
      if (ch === GLOW && LIGHT_OF[id]) { this.set(c, x, y, z, GLOW, LIGHT_OF[id]); refill.push(x, y, z); }
      if (LIGHT_PASS[id]) for (const [dx, dy, dz] of DIRS) if (y + dy >= 0 && y + dy < WORLD_HEIGHT) refill.push(x + dx, y + dy, z + dz);
      this.spread(refill, ch);
    }
    this.report();
  }

  // ---- the two flood fills ----

  /** Spread light outwards from the queued spots (x, y, z triples) to every spot it can make brighter. */
  spread(queue, ch) {
    for (let head = 0; head < queue.length; head += 3) {
      const x = queue[head], y = queue[head + 1], z = queue[head + 2];
      const here = level(this.get(x, y, z), ch);
      if (here <= 1) continue;
      for (let d = 0; d < 6; d++) {
        const [dx, dy, dz] = DIRS[d], nx = x + dx, ny = y + dy, nz = z + dz;
        if (ny < 0 || ny >= WORLD_HEIGHT) continue;
        const c = this.chunkAt(nx, nz);
        if (!c || !c.light) continue;                           // not here yet: it pulls the light in when it arrives
        const pass = LIGHT_PASS[c.get(nx - c.cx * S, ny, nz - c.cz * S)];
        if (!pass) continue;
        const next = ch === SKY && d === DOWN && here === 15 && pass === 2 ? 15 : here - 1;
        if (level(this.get(nx, ny, nz), ch) >= next) continue;
        this.set(c, nx, ny, nz, ch, next);
        queue.push(nx, ny, nz);
      }
    }
  }

  /**
   * Take light away: starting from a spot that has just gone dark (it held `old`), darken every spot that got its light
   * through it. Spots lit from elsewhere are kept and queued in `refill`, to shine back into the gap.
   */
  unspread(start, ch, refill) {
    const queue = start;
    for (let head = 0; head < queue.length; head += 4) {
      const x = queue[head], y = queue[head + 1], z = queue[head + 2], was = queue[head + 3];
      for (let d = 0; d < 6; d++) {
        const [dx, dy, dz] = DIRS[d], nx = x + dx, ny = y + dy, nz = z + dz;
        if (ny < 0 || ny >= WORLD_HEIGHT) continue;
        const c = this.chunkAt(nx, nz);
        if (!c || !c.light) continue;
        const n = level(this.get(nx, ny, nz), ch);
        if (!n) continue;
        const fedFromHere = n < was || (ch === SKY && d === DOWN && was === 15 && n === 15);
        const ownGlow = ch === GLOW && LIGHT_OF[c.get(nx - c.cx * S, ny, nz - c.cz * S)] === n;
        if (fedFromHere && !ownGlow) {
          this.set(c, nx, ny, nz, ch, 0);
          queue.push(nx, ny, nz, n);
        } else {
          refill.push(nx, ny, nz);
        }
      }
    }
  }
}
