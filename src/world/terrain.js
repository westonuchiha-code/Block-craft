// The shape of the land, and which biome each spot is in.
//
// BIOMES: the world is cut into large regions round scattered centre points (one per REGION_SIZE square, jittered), with each
// column's position warped by a slow noise first, so borders wander instead of running straight. A region's biome comes from the
// climate at its centre. Near a border the land's shape is blended between the two biomes, so it never steps at the edge.
//
// LAND: four noise maps, each shaped by a curve, the way Minecraft builds its land:
//   continentalness  how far inland an area is (low = sea)
//   erosion          how flat it is (low = rugged)
//   peaks & valleys  the local rise and fall
//   weirdness        a per-area flag that adds terraces
// The biome then scales the rolling ground and the mountains, and adds dunes in the desert. Lakes and rivers are cut in last.
// Everything here depends only on (x, z) and the seed.
import { clamp01, smooth01, spline, lerp } from '../core/math.js';
import { hash3, valueNoise, gradientNoise, fbm } from '../core/noise.js';
import { BLOCK } from './blocks.js';
import { BIOMES, BIOME, biomeForClimate } from './biomes.js';
import { SEA_LEVEL, BASE_SEA_LEVEL, TERRAIN_LIFT, TREE_LINE, SNOW_LINE } from './constants.js';

const REGION_SIZE = 1300;            // average biome region width, in blocks
const BORDER_WARP = 240;            // how far borders wander
const BORDER_BLEND = 90;            // land shape is blended over this width round a border
const MAX_HEIGHT = 150;             // the tallest ground

// curves written against the old sea level of 16, before the land is lifted
const LAND_CURVE   = [[0, 4], [0.1, 7], [0.17, 12], [0.25, 15.5], [0.33, 18], [0.6, 22], [0.8, 28], [1, 35]]; // continentalness -> base height
const RUGGED_CURVE = [[0, 1], [0.5, 0.9], [0.65, 0.55], [0.8, 0.2], [1, 0.05]];                             // erosion -> roughness
const MOUNT_CURVE  = [[0, 0], [0.42, 0], [0.55, 0.8], [0.68, 1], [1, 1]];                                   // continentalness -> mountains
const MOUNT_MASK   = [[0, 1], [0.4, 1], [0.55, 0], [1, 0]];                                                 // erosion -> mountains only where rugged
const LAKE_LEVEL = 0.33, RIVER_WIDTH = 0.03;

/** A cache keyed by column, cleared when it grows too big. */
function columnCache(limit) {
  const map = new Map();
  return {
    get: (x, z) => map.get((x + 200000) * 400000 + (z + 200000)),
    set(x, z, v) { if (map.size > limit) map.clear(); map.set((x + 200000) * 400000 + (z + 200000), v); return v; },
  };
}

export function createTerrain(seed) {
  const heights = columnCache(200000);
  const columns = columnCache(200000);
  const regionsAt = columnCache(200000);
  const regionBiome = new Map();

  // ---- biome regions ----

  /** The centre of region (i, j), jittered inside its square. */
  const regionCentre = (i, j) => [
    (i + 0.15 + 0.7 * hash3(i, 41, j, seed + 400)) * REGION_SIZE,
    (j + 0.15 + 0.7 * hash3(i, 42, j, seed + 400)) * REGION_SIZE,
  ];

  function biomeOfRegion(i, j) {
    const key = i * 131072 + j;
    let b = regionBiome.get(key);
    if (b === undefined) {
      const [cx, cz] = regionCentre(i, j);
      b = biomeForClimate(fbm(cx / 2600, cz / 2600, seed + 160), fbm(cx / 2000, cz / 2000, seed + 170));
      regionBiome.set(key, b);
    }
    return b;
  }

  /**
   * Which biome a column is in, and how near a border it is:
   * { biome, other, blend }: `other` is the biome across the nearest border, `blend` how much of it to mix into the land's shape
   * (0 deep inside, 0.5 right on the border).
   */
  function regionInfo(x, z) {
    const cached = regionsAt.get(x, z);
    if (cached) return cached;
    const wx = x + (fbm(x / 260, z / 260, seed + 401) - 0.5) * BORDER_WARP * 2;
    const wz = z + (fbm(x / 260, z / 260, seed + 402) - 0.5) * BORDER_WARP * 2;
    const ri = Math.floor(wx / REGION_SIZE), rj = Math.floor(wz / REGION_SIZE);
    let d1 = Infinity, b1 = 0;
    const found = [];
    for (let i = ri - 1; i <= ri + 1; i++) for (let j = rj - 1; j <= rj + 1; j++) {
      const [cx, cz] = regionCentre(i, j), d = Math.hypot(wx - cx, wz - cz), b = biomeOfRegion(i, j);
      found.push([d, b]);
      if (d < d1) { d1 = d; b1 = b; }
    }
    let d2 = Infinity, b2 = b1;                                   // the nearest region of a different biome
    for (const [d, b] of found) if (b !== b1 && d < d2) { d2 = d; b2 = b; }
    const blend = b2 === b1 ? 0 : 0.5 * (1 - smooth01((d2 - d1) / BORDER_BLEND));
    return regionsAt.set(x, z, { biome: b1, other: b2, blend });
  }

  const biomeAt = (x, z) => regionInfo(x, z).biome;

  /** A biome's land-shape setting at a column, blended across the border. */
  const shape = (info, key) => lerp(+BIOMES[info.biome].terrain[key], +BIOMES[info.other].terrain[key], info.blend);

  // ---- height ----

  /** Height of the ground (the top solid block) at a column. */
  function surfaceHeight(x, z) {
    const cached = heights.get(x, z);
    if (cached !== undefined) return cached;
    const info = regionInfo(x, z);
    const c = fbm(x / 400, z / 400, seed + 110);
    const e = fbm(x / 90, z / 90, seed + 120);
    const pv = fbm(x / 50, z / 50, seed + 130) * 2 - 1;   // -1 valley .. +1 peak
    const w = fbm(x / 120, z / 120, seed + 140);
    const rough = spline(e, RUGGED_CURVE) * shape(info, 'rolling');
    const inland = smooth01((c - 0.2) / 0.12);             // 0 out at sea, 1 on the continent

    let h = spline(c, LAND_CURVE) + shape(info, 'lift') * inland;
    h += pv * 9 * rough * inland + pv * 1.5 * (1 - inland);          // rolling ground, more where it is rugged
    h -= smooth01((-pv - 0.5) / 0.3) * rough * 4 * inland;          // valleys between the rises
    const ridge = 1 - Math.abs(pv);
    const mount = spline(c, MOUNT_CURVE) * spline(e, MOUNT_MASK) * shape(info, 'mountains');
    h += mount * (ridge * ridge * 36 + ridge * 5);                  // mountain ridges with foothills
    const dunes = shape(info, 'dunes') * inland;
    if (dunes > 0) h += dunes * (Math.abs(gradientNoise(x / 26, z / 40, seed + 145) - 0.5) * 9 - 1.5);
    const terrace = smooth01((w - 0.72) / 0.04) * (1 - Math.min(1, mount));
    h += (Math.floor(h / 4) * 4 - h) * terrace;                     // flat-topped terraces with steep sides

    // lakes: low basins pulled below sea level, anywhere that is not high ground
    const lake = fbm(x / 55, z / 55, seed + 150);
    const lakeAmount = smooth01((LAKE_LEVEL - lake) / 0.1) * clamp01(1 - (h - BASE_SEA_LEVEL) / 9);
    if (h > BASE_SEA_LEVEL - 3.5) h += (BASE_SEA_LEVEL - 3.5 - h) * lakeAmount;
    // rivers: a winding channel along the middle of a noise field, fading out on high ground
    const river = Math.abs(gradientNoise(x / 170, z / 170, seed + 155) - 0.5);
    const bank = smooth01(1 - river / RIVER_WIDTH);
    const riverFade = clamp01(1 - (h - BASE_SEA_LEVEL) / 12) * (1 - Math.min(1, mount) * 0.9);
    if (h > BASE_SEA_LEVEL - 2.5) h += (BASE_SEA_LEVEL - 2.5 - h) * bank * riverFade;

    return heights.set(x, z, Math.floor(Math.max(2, Math.min(MAX_HEIGHT - TERRAIN_LIFT, h))) + TERRAIN_LIFT);
  }

  // ---- what the surface is made of ----

  /**
   * Everything about one column that more than one block needs:
   *   h, biome, top (the surface block), under (the blocks under it), steep (a cliff), caveMouth (a cave may open here),
   *   mesa (desert high ground: layered red rock instead of sand).
   */
  function column(x, z) {
    const cached = columns.get(x, z);
    if (cached) return cached;
    const h = surfaceHeight(x, z);
    const slope = Math.max(
      Math.abs(surfaceHeight(x + 1, z) - h), Math.abs(surfaceHeight(x - 1, z) - h),
      Math.abs(surfaceHeight(x, z + 1) - h), Math.abs(surfaceHeight(x, z - 1) - h));
    const steep = slope >= 3 && h > SEA_LEVEL + 1;                 // sheer faces show bare rock
    const snowY = SNOW_LINE - 3 + Math.floor(valueNoise(x / 18, z / 18, seed + 180) * 6);
    const biome = biomeAt(x, z);
    let top, under, mesa = false;
    if (h <= SEA_LEVEL + 1) {                                       // beaches, lake beds, sea floor
      top = (h <= SEA_LEVEL - 6 && hash3(x, 0, z, seed + 11) < 0.4) ? BLOCK.gravel : BLOCK.sand;
      under = BLOCK.sand;
    } else if (biome === BIOME.desert) {
      // sand on the low ground (dunes); the high ground is mesas of coloured rock bands
      mesa = h > SEA_LEVEL + 13;
      top = mesa ? (slope <= 1 ? BLOCK.red_sand : BLOCK.terracotta) : BLOCK.sand;
      under = mesa ? BLOCK.terracotta : BLOCK.sand;
    } else if (h >= snowY && slope <= 6) { top = BLOCK.snow; under = BLOCK.stone; }
    else if (steep || h >= TREE_LINE) { top = BLOCK.stone; under = BLOCK.stone; }
    else if (biome === BIOME.frost) { top = BLOCK.snow; under = BLOCK.dirt; }
    else { top = BLOCK.grass; under = BLOCK.dirt; }
    const caveMouth = h > SEA_LEVEL + 3 && valueNoise(x / 30, z / 30, seed + 190) > 0.86;
    return columns.set(x, z, { h, biome, top, under, steep, caveMouth, mesa });
  }

  return { surfaceHeight, biomeAt, regionInfo, column };
}
