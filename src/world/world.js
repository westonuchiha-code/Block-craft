// The world as the game sees it: the chunks loaded round the player, block reads and writes, and the workers that build new chunks.
import { Chunk } from './chunk.js';
import { Lighting } from './light.js';
import { createGenerator } from './generator.js';
import { CHUNK_SIZE, WORLD_HEIGHT, SEA_LEVEL } from './constants.js';
import { IS_SOLID } from './blocks.js';

const chunkKey = (cx, cz) => `${cx},${cz}`;

export class World {
  /**
   * @param {number} seed
   * @param {{ onChunkLoaded?: (chunk: Chunk) => void, onChunkUnloaded?: (chunk: Chunk) => void,
   *           onBlockChanged?: (x: number, y: number, z: number) => void,
   *           onLightChanged?: (cx: number, cz: number, sy: number) => void }} hooks
   */
  constructor(seed, hooks = {}) {
    this.seed = seed;
    this.hooks = hooks;
    /** The chunks in the world, built and lit. @type {Map<string, Chunk>} */
    this.chunks = new Map();
    this.pending = new Map();            // key -> request id, chunks asked for and not yet in the world
    this.arrived = [];                   // chunks back from a worker, waiting to be lit (then they join the world)
    this.lighting = new Lighting(this, (cx, cz, sy) => this.hooks.onLightChanged?.(cx, cz, sy));
    this.nextRequestId = 1;
    /** The same generator the workers run, for questions the game asks directly (biome colours, spawn point). */
    this.generator = createGenerator(seed);
    this.workers = startWorkers(seed, msg => this.receiveChunk(msg));
    this.nextWorker = 0;
  }

  dispose() {
    for (const w of this.workers) w.terminate();
    this.workers = [];
  }

  // ---- blocks ----

  getChunk(cx, cz) { return this.chunks.get(chunkKey(cx, cz)); }

  getBlock(x, y, z) {
    if (y < 0 || y >= WORLD_HEIGHT) return 0;
    const c = this.chunks.get(chunkKey(Math.floor(x / CHUNK_SIZE), Math.floor(z / CHUNK_SIZE)));
    return c ? c.get(x - c.cx * CHUNK_SIZE, y, z - c.cz * CHUNK_SIZE) : 0;
  }

  /** Is the block at this spot solid? Unloaded chunks count as solid, so nothing falls out of the world while it loads. */
  isSolid(x, y, z) {
    if (y < 0) return true;
    if (y >= WORLD_HEIGHT) return false;
    const c = this.chunks.get(chunkKey(Math.floor(x / CHUNK_SIZE), Math.floor(z / CHUNK_SIZE)));
    if (!c) return true;
    return IS_SOLID[c.get(x - c.cx * CHUNK_SIZE, y, z - c.cz * CHUNK_SIZE)] === 1;
  }

  setBlock(x, y, z, id) {
    const c = this.chunks.get(chunkKey(Math.floor(x / CHUNK_SIZE), Math.floor(z / CHUNK_SIZE)));
    if (!c || y < 0 || y >= WORLD_HEIGHT) return false;
    const lx = x - c.cx * CHUNK_SIZE, lz = z - c.cz * CHUNK_SIZE;
    c.set(lx, y, lz, id);
    c.updateSkyTop(lx, lz);
    c.edits.set(`${lx},${y},${lz}`, id);
    this.lighting.blockChanged(x, y, z);
    this.hooks.onBlockChanged?.(x, y, z);
    return true;
  }

  // ---- loading ----

  /**
   * Keep the chunks within `radius` of (x, z) loaded: ask for missing ones nearest first, drop ones well outside.
   * Arrived chunks are lit and join the world within `lightBudgetMs` of work.
   * Call every frame; it does little work when nothing has changed.
   */
  update(x, z, radius, lightBudgetMs = 4) {
    const pcx = Math.floor(x / CHUNK_SIZE), pcz = Math.floor(z / CHUNK_SIZE);
    const maxInFlight = this.workers.length * 3;
    if (this.pending.size < maxInFlight) {
      const wanted = [];
      for (let dx = -radius; dx <= radius; dx++) for (let dz = -radius; dz <= radius; dz++) {
        const d2 = dx * dx + dz * dz;
        if (d2 > radius * radius + radius) continue;                 // a round area, not a square
        const key = chunkKey(pcx + dx, pcz + dz);
        if (!this.chunks.has(key) && !this.pending.has(key)) wanted.push([d2, pcx + dx, pcz + dz, key]);
      }
      wanted.sort((a, b) => a[0] - b[0]);
      for (const [, cx, cz, key] of wanted.slice(0, maxInFlight - this.pending.size)) this.request(cx, cz, key);
    }
    const drop = radius + 2;
    const t0 = performance.now();
    while (this.arrived.length && performance.now() - t0 < lightBudgetMs) {
      const chunk = this.arrived.shift(), key = chunkKey(chunk.cx, chunk.cz);
      this.pending.delete(key);
      if (Math.abs(chunk.cx - pcx) > drop || Math.abs(chunk.cz - pcz) > drop) continue;
      this.lighting.lightChunk(chunk);               // this also puts it in this.chunks
      this.hooks.onChunkLoaded?.(chunk);
    }
    for (const [key, c] of this.chunks) {
      if (Math.abs(c.cx - pcx) > drop || Math.abs(c.cz - pcz) > drop) {
        this.chunks.delete(key);
        this.lighting.forget(c);
        this.hooks.onChunkUnloaded?.(c);
      }
    }
  }

  request(cx, cz, key) {
    const id = this.nextRequestId++;
    this.pending.set(key, id);
    this.workers[this.nextWorker++ % this.workers.length].postMessage({ seed: this.seed, id, cx, cz });
  }

  receiveChunk({ id, seed, cx, cz, sections }) {
    const key = chunkKey(cx, cz);
    if (seed !== this.seed || this.pending.get(key) !== id) return;     // an answer for a world or a request we no longer want
    this.pending.set(key, -1);                                             // still pending: built, waiting to be lit
    this.arrived.push(new Chunk(cx, cz, sections));
  }

  /** Are the chunks round this spot loaded (so the player can be put down there)? */
  isAreaLoaded(x, z, radius = 1) {
    const pcx = Math.floor(x / CHUNK_SIZE), pcz = Math.floor(z / CHUNK_SIZE);
    for (let dx = -radius; dx <= radius; dx++) for (let dz = -radius; dz <= radius; dz++) if (!this.chunks.has(chunkKey(pcx + dx, pcz + dz))) return false;
    return true;
  }

  /** A dry spot near the world's origin to start on: the nearest land above the sea, searched outwards in rings. */
  findSpawn() {
    const g = this.generator;
    const treeNear = (x, z) => { for (let dx = -5; dx <= 5; dx++) for (let dz = -5; dz <= 5; dz++) if (g.treeRootedAt(x + dx, z + dz)) return true; return false; };
    for (let r = 0; r < 400; r += 4) {
      for (let a = 0; a < Math.max(1, r); a++) {
        const ang = (a / Math.max(1, r)) * Math.PI * 2, x = Math.round(Math.cos(ang) * r), z = Math.round(Math.sin(ang) * r);
        const col = g.column(x, z);
        if (col.h > SEA_LEVEL + 1 && !col.steep && !col.caveMouth && !treeNear(x, z)) return { x: x + 0.5, y: col.h + 1, z: z + 0.5 };
      }
    }
    return { x: 0.5, y: g.surfaceHeight(0, 0) + 1, z: 0.5 };
  }
}

/** Start the chunk-building workers: a few cores' worth, leaving room for the game itself and the browser. */
function startWorkers(seed, onMessage) {
  const count = Math.max(2, Math.min(6, (navigator.hardwareConcurrency || 4) - 2));
  const url = URL.createObjectURL(new Blob([__WORKER_SOURCE__], { type: 'text/javascript' }));
  return Array.from({ length: count }, () => {
    const w = new Worker(url);
    w.onmessage = e => onMessage(e.data);
    w.postMessage({ seed });
    return w;
  });
}
