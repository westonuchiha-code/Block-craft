// The natural world: given a seed, what block is at any (x, y, z), and how to fill a whole chunk at once.
// No state but caches: the same seed always gives the same world.
import { hash3, valueNoise, valueNoise3 } from '../core/noise.js';
import { BLOCK, woodBlock } from './blocks.js';
import { BIOME, TREES_BY_BIOME } from './biomes.js';
import { createTerrain } from './terrain.js';
import { buildTree, TREE_REACH } from './trees.js';
import { CHUNK_SIZE, SECTION_HEIGHT, SECTIONS_PER_CHUNK, WORLD_HEIGHT, SEA_LEVEL, TREE_LINE, LAVA_LEVEL } from './constants.js';

const CAVE_WIDTH = 0.075;
const CAVE_ROOF = 9;                  // caves stay at least this far under the ground (except at cave mouths)
const GENERATED_TOP = 160;            // nothing natural above this

export function createGenerator(seed) {
  const terrain = createTerrain(seed);
  const { column } = terrain;

  // caves: where two 3D noise fields are both near their middle, the rock is hollowed into a winding tunnel. The fields are as
  // tall as they are wide, so tunnels are round (two to four blocks high, high enough to walk in), and a third, slow field
  // decides where caves are at all, so they come in clusters with solid rock between.
  function isCave(x, y, z) {
    if (valueNoise3(x / 90, y / 45, z / 90, seed + 82) < 0.52) return false;
    if (Math.abs(valueNoise3(x / 16, y / 20, z / 16, seed + 80) - 0.5) > CAVE_WIDTH) return false;
    return Math.abs(valueNoise3(x / 16, y / 20, z / 16, seed + 81) - 0.5) < CAVE_WIDTH;
  }

  // desert mesas: flat bands of coloured rock, each a few blocks thick, wandering gently up and down
  const MESA_BANDS = [BLOCK.terracotta, BLOCK.light_terracotta, BLOCK.terracotta, BLOCK.red_terracotta, BLOCK.red_sandstone,
                      BLOCK.terracotta, BLOCK.light_terracotta, BLOCK.red_sandstone, BLOCK.red_terracotta];
  function mesaBand(x, y, z) {
    const wave = y + Math.floor(Math.sin(x * 0.05 + z * 0.03) * 1.5 + valueNoise(x / 40, z / 40, seed + 340) * 3);
    return MESA_BANDS[Math.floor(hash3(Math.floor(wave / 3), 0, 0, seed + 341) * MESA_BANDS.length)];
  }

  // ores lie deeper the better they are: iron below 48, mithril below 20, adamantite (the best) only down by the lava
  function oreAt(x, y, z) {
    const cx = x >> 1, cy = y >> 1, cz = z >> 1;
    if (y <= 10 && hash3(cx, cy, cz, seed + 93) < 0.0019 && hash3(x, y, z, seed + 94) < 0.55) return BLOCK.adamantite_ore;
    if (y <= 20 && hash3(cx, cy, cz, seed + 91) < (y <= 10 ? 0.0016 : 0.0048) && hash3(x, y, z, seed + 92) < 0.55) return BLOCK.mithril_ore;
    if (y <= 48 && hash3(cx, cy, cz, seed + 89) < 0.012 && hash3(x, y, z, seed + 90) < 0.55) return BLOCK.iron_ore;
    return 0;
  }

  // the rock: wavy strata bands (they show on cliffs), rounded blobs of other rock, pockets of gravel and dirt, tuff deep down
  function rockAt(x, y, z) {
    const wave = y + Math.floor(Math.sin(x * 0.11 + z * 0.05) * 1.6 + Math.sin(z * 0.13 - x * 0.04) * 1.6);
    const band = hash3(wave >> 1, 0, 0, seed + 41);
    if (band < 0.15) return BLOCK.andesite;
    if (band < 0.22) return BLOCK.granite;
    if (band < 0.29) return BLOCK.diorite;
    const cx = Math.floor(x / 8), cy = Math.floor(y / 8), cz = Math.floor(z / 8);
    if (hash3(cx, cy, cz, seed + 43) < 0.75) {
      const px = cx * 8 + 4 + (hash3(cx, cy, cz, seed + 44) - 0.5) * 2;
      const py = cy * 8 + 4 + (hash3(cx, cy, cz, seed + 45) - 0.5) * 2;
      const pz = cz * 8 + 4 + (hash3(cx, cy, cz, seed + 46) - 0.5) * 2;
      const r = 2.6 + hash3(cx, cy, cz, seed + 47) * 1.6;
      const dx = x - px, dy = (y - py) * 1.4, dz = z - pz;
      if (dx * dx + dy * dy + dz * dz < r * r) {
        const k = hash3(cx, cy, cz, seed + 48);
        if (y < 28 && k < 0.6) return BLOCK.tuff;
        return k < 0.28 ? BLOCK.granite : k < 0.5 ? BLOCK.andesite : k < 0.68 ? BLOCK.diorite : k < 0.82 ? BLOCK.gravel : BLOCK.dirt;
      }
    }
    return BLOCK.stone;
  }

  // rock near the surface grows moss on the low, damp cliffs
  function stoneFace(x, y, z) {
    if (y > SEA_LEVEL - 3 && y < SEA_LEVEL + 30 && hash3(x >> 1, y >> 1, z >> 1, seed + 50) < 0.16) return BLOCK.mossy_rock;
    return rockAt(x, y, z);
  }

  // tall grass grows in patches: thick in meadows, absent between
  function tallGrassAt(x, z) {
    const patch = valueNoise(x / 9, z / 9, seed + 210);
    return hash3(x, 3, z, seed + 211) < (patch > 0.55 ? 0.55 : patch > 0.42 ? 0.12 : 0.02);
  }

  // a cactus now and then in the desert: 1 to 3 blocks tall, or 0
  function cactusHeight(x, z) {
    if (hash3(x, 8, z, seed + 330) >= 0.007 || valueNoise(x / 20, z / 20, seed + 331) <= 0.35) return 0;
    return 1 + Math.floor(hash3(x, 9, z, seed + 332) * 3);
  }

  /** The natural block at one spot, before trees are added. */
  function blockAt(x, y, z) {
    if (y <= 0) return BLOCK.bedrock;
    if (y > GENERATED_TOP) return BLOCK.air;
    const col = column(x, z), h = col.h;
    if (y > h) {
      if (y <= SEA_LEVEL) return (y === SEA_LEVEL && col.biome === BIOME.frost) ? BLOCK.ice : BLOCK.water;
      if (col.biome === BIOME.desert && col.top === BLOCK.sand && !col.caveMouth && h > SEA_LEVEL + 4 && y <= h + cactusHeight(x, z)) return BLOCK.cactus;
      if (y === h + 1 && col.top === BLOCK.grass && !col.caveMouth && h > SEA_LEVEL && tallGrassAt(x, z)) return BLOCK.tall_grass;
      return BLOCK.air;
    }
    if (y >= h - 3) {                                             // the surface and the three blocks under it
      if (col.caveMouth && y >= 2 && isCave(x, y, z)) return BLOCK.air;
      if (col.mesa) return y === h && col.top === BLOCK.red_sand ? BLOCK.red_sand : mesaBand(x, y, z);
      if (y === h) return col.top === BLOCK.stone ? stoneFace(x, y, z) : col.top;
      if (col.biome === BIOME.desert && col.top === BLOCK.sand && y <= h - 2) return BLOCK.sandstone;
      if (col.under === BLOCK.stone) return stoneFace(x, y, z);
      if (col.under === BLOCK.dirt && hash3(x, y, z, seed + 9) < 0.05) return BLOCK.gravel;
      return col.under;
    }
    // (caves stay well under the ground, so thin ridges and peaks are not left with holes or hanging pieces; they open to the
    //  surface only where the column is marked as a cave mouth, above)
    if (y >= 2 && y < h - CAVE_ROOF && isCave(x, y, z)) return y <= LAVA_LEVEL ? BLOCK.lava : (h < SEA_LEVEL && y <= SEA_LEVEL) ? BLOCK.water : BLOCK.air;
    if (col.mesa && y >= h - 30) return mesaBand(x, y, z);            // the bands run deep into the mesa
    const ore = oreAt(x, y, z);
    if (ore) return ore;
    if (hash3(x, y, z, seed + 7) < 0.04) return BLOCK.coal_ore;
    return y >= h - 6 ? stoneFace(x, y, z) : rockAt(x, y, z);
  }

  // ---- trees ----
  const treeCache = new Map();
  const treeChance = (x, z) => 0.005 + 0.05 * Math.min(1, Math.max(0, (valueNoise(x / 40, z / 40, seed + 50) - 0.4) / 0.35));
  const candidate = (x, z) => { const v = hash3(x, 0, z, seed + 99); return v < 0.055 && v < treeChance(x, z) ? v : -1; };

  /** The tree rooted at this column, or null. Trees keep a gap from each other (the lowest hash in a 5 x 5 patch wins). */
  function treeRootedAt(x, z) {
    const key = x * 131072 + z;
    if (treeCache.has(key)) return treeCache.get(key);
    let tree = null;
    const v = candidate(x, z);
    if (v >= 0) {
      let wins = true;
      for (let dx = -2; dx <= 2 && wins; dx++) for (let dz = -2; dz <= 2; dz++) {
        if ((dx || dz)) { const o = candidate(x + dx, z + dz); if (o >= 0 && o < v) { wins = false; break; } }
      }
      const col = wins ? column(x, z) : null;
      const groundOk = col && (col.top === BLOCK.grass ||
        (col.biome === BIOME.frost && col.top === BLOCK.snow && col.h < TREE_LINE && hash3(x, 2, z, seed + 97) < 0.45) ||
        (col.biome === BIOME.desert && col.top === BLOCK.sand && col.h <= SEA_LEVEL + 4 && hash3(x, 2, z, seed + 97) < 0.3));   // palms only by the water
      if (groundOk && !col.caveMouth && col.h > SEA_LEVEL + 1 && col.h + 24 < WORLD_HEIGHT) {
        const table = TREES_BY_BIOME[col.biome];
        let total = 0; for (const e of table) total += e[2];
        let pick = hash3(x, 1, z, seed + 98) * total, entry = table[0];
        for (const e of table) { if (pick < e[2]) { entry = e; break; } pick -= e[2]; }
        let [wood, shape] = entry, base = col.h + 1;
        if (shape === 'great') {                                // a 2 x 2 trunk needs level grass under all four blocks
          for (const [ox, oz] of [[1, 0], [0, 1], [1, 1]]) {
            const c2 = column(x + ox, z + oz);
            if (c2.top !== BLOCK.grass || c2.caveMouth || c2.h <= SEA_LEVEL + 1 || Math.abs(c2.h - col.h) > 1) { shape = 'round'; base = col.h + 1; break; }
            base = Math.max(base, c2.h + 1);
          }
        }
        tree = { x, z, y: base, wood, shape };
      }
    }
    if (treeCache.size > 60000) treeCache.clear();
    treeCache.set(key, tree);
    return tree;
  }

  // ---- whole chunks ----

  /**
   * Fill one chunk with the natural world.
   * @returns {(Uint16Array|null)[]} its sections, bottom up; null where a section is all air.
   */
  function generateChunk(cx, cz) {
    const sections = new Array(SECTIONS_PER_CHUNK).fill(null);
    const x0 = cx * CHUNK_SIZE, z0 = cz * CHUNK_SIZE;
    const section = s => sections[s] || (sections[s] = new Uint16Array(CHUNK_SIZE * SECTION_HEIGHT * CHUNK_SIZE));
    const index = (lx, ly, lz) => (ly * CHUNK_SIZE + lz) * CHUNK_SIZE + lx;
    const get = (lx, y, lz) => { const s = sections[y >> 4]; return s ? s[index(lx, y & 15, lz)] : 0; };
    const put = (lx, y, lz, id) => { section(y >> 4)[index(lx, y & 15, lz)] = id; };

    for (let lz = 0; lz < CHUNK_SIZE; lz++) for (let lx = 0; lx < CHUNK_SIZE; lx++) {
      const x = x0 + lx, z = z0 + lz, top = Math.max(column(x, z).h + 4, SEA_LEVEL);
      for (let y = 0; y <= top; y++) { const id = blockAt(x, y, z); if (id) put(lx, y, lz, id); }
    }

    // trees that reach into this chunk: leaves only fill empty space and grass; logs also replace leaves
    const inside = (x, y, z) => x >= x0 && x < x0 + CHUNK_SIZE && z >= z0 && z < z0 + CHUNK_SIZE && y > 0 && y < WORLD_HEIGHT;
    const placedLogs = [];
    for (let x = x0 - TREE_REACH; x < x0 + CHUNK_SIZE + TREE_REACH; x++) for (let z = z0 - TREE_REACH; z < z0 + CHUNK_SIZE + TREE_REACH; z++) {
      if (hash3(x, 0, z, seed + 99) >= 0.055) continue;     // (quick reject before the full check)
      const t = treeRootedAt(x, z);
      if (!t) continue;
      const parts = buildTree(t.wood, t.shape, t.x, t.y, t.z, seed);
      const leaf = woodBlock(t.wood, 'leaves');
      for (const [bx, by, bz] of parts.leaves) {
        if (!inside(bx, by, bz)) continue;
        const here = get(bx - x0, by, bz - z0);
        if (here === BLOCK.air || here === BLOCK.tall_grass) put(bx - x0, by, bz - z0, leaf);
      }
      placedLogs.push([parts.logs, woodBlock(t.wood, 'log')]);
    }
    for (const [logs, log] of placedLogs) for (const [bx, by, bz] of logs) {
      if (!inside(bx, by, bz)) continue;
      const here = get(bx - x0, by, bz - z0);
      if (here === BLOCK.air || here === BLOCK.tall_grass || BLOCK_IS_LEAVES.has(here)) put(bx - x0, by, bz - z0, log);
    }
    return sections;
  }

  return { ...terrain, blockAt, generateChunk, treeRootedAt };
}

const BLOCK_IS_LEAVES = new Set(['maple', 'oak', 'birch', 'spruce', 'palm'].map(w => woodBlock(w, 'leaves')));
