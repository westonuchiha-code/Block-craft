// The shape of the land. Four noise maps, each shaped by a curve, the way Minecraft builds its land:
//   continentalness  how far inland an area is (low = sea)
//   erosion          how flat it is (low = rugged)
//   peaks & valleys  the local rise and fall
//   weirdness        a per-area flag that adds terraces
// Then lakes and rivers are cut in. Everything here depends only on (x, z) and the seed.
import { clamp01, smooth01, spline } from '../core/math.js';
import { hash3, valueNoise, gradientNoise, fbm } from '../core/noise.js';
import { BLOCK } from './blocks.js';
import { BIOME } from './biomes.js';
import { SEA_LEVEL, BASE_SEA_LEVEL, TERRAIN_LIFT, TREE_LINE, SNOW_LINE } from './constants.js';

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
  const biomes = columnCache(200000);

  /** Height of the ground (the top solid block) at a column. */
  function surfaceHeight(x, z) {
    const cached = heights.get(x, z);
    if (cached !== undefined) return cached;
    const c = fbm(x / 400, z / 400, seed + 110);
    const e = fbm(x / 90, z / 90, seed + 120);
    const pv = fbm(x / 50, z / 50, seed + 130) * 2 - 1;   // -1 valley .. +1 peak
    const w = fbm(x / 120, z / 120, seed + 140);
    const rough = spline(e, RUGGED_CURVE);
    const inland = smooth01((c - 0.2) / 0.12);             // 0 out at sea, 1 on the continent

    let h = spline(c, LAND_CURVE);
    h += pv * 9 * rough * inland + pv * 1.5 * (1 - inland);          // rolling ground, more where it is rugged
    h -= smooth01((-pv - 0.5) / 0.3) * rough * 4 * inland;          // valleys between the rises
    const ridge = 1 - Math.abs(pv);
    const mount = spline(c, MOUNT_CURVE) * spline(e, MOUNT_MASK);
    h += mount * (ridge * ridge * 36 + ridge * 5);                  // mountain ridges with foothills
    const terrace = smooth01((w - 0.72) / 0.04) * (1 - mount);
    h += (Math.floor(h / 4) * 4 - h) * terrace;                     // flat-topped terraces with steep sides

    // lakes: low basins pulled below sea level, anywhere that is not high ground
    const lake = fbm(x / 55, z / 55, seed + 150);
    const lakeAmount = smooth01((LAKE_LEVEL - lake) / 0.1) * clamp01(1 - (h - BASE_SEA_LEVEL) / 9);
    if (h > BASE_SEA_LEVEL - 3.5) h += (BASE_SEA_LEVEL - 3.5 - h) * lakeAmount;
    // rivers: a winding channel along the middle of a noise field, fading out on high ground
    const river = Math.abs(gradientNoise(x / 170, z / 170, seed + 155) - 0.5);
    const bank = smooth01(1 - river / RIVER_WIDTH);
    const riverFade = clamp01(1 - (h - BASE_SEA_LEVEL) / 12) * (1 - mount * 0.9);
    if (h > BASE_SEA_LEVEL - 2.5) h += (BASE_SEA_LEVEL - 2.5 - h) * bank * riverFade;

    return heights.set(x, z, Math.floor(Math.max(2, Math.min(72, h))) + TERRAIN_LIFT);
  }

  /** The biome of a column (an index into BIOMES). */
  function biomeAt(x, z) {
    const cached = biomes.get(x, z);
    if (cached !== undefined) return cached;
    const t = fbm(x / 320, z / 320, seed + 160), m = fbm(x / 240, z / 240, seed + 170);
    let b;
    if (t < 0.25) b = BIOME.frost;
    else if (t >= 0.42 && fbm(x / 360, z / 360, seed + 175) > 0.67) b = BIOME.desert;
    else if (t < 0.4) b = BIOME.highlands;
    else b = m > 0.5 ? BIOME.forest : BIOME.autumn;
    return biomes.set(x, z, b);
  }

  /**
   * Everything about one column that more than one block needs:
   *   height, biome, the top block and the blocks under it, whether it is a cliff, whether a cave opens there.
   */
  function column(x, z) {
    const cached = columns.get(x, z);
    if (cached) return cached;
    const h = surfaceHeight(x, z);
    const slope = Math.max(
      Math.abs(surfaceHeight(x + 1, z) - h), Math.abs(surfaceHeight(x - 1, z) - h),
      Math.abs(surfaceHeight(x, z + 1) - h), Math.abs(surfaceHeight(x, z - 1) - h));
    const steep = slope >= 3 && h > SEA_LEVEL + 1;                 // sheer faces show bare stone
    const snowY = SNOW_LINE - 3 + Math.floor(valueNoise(x / 18, z / 18, seed + 180) * 6);
    const biome = biomeAt(x, z);
    let top, under;
    if (h <= SEA_LEVEL + 1) {                                       // beaches, lake beds, sea floor
      top = (h <= SEA_LEVEL - 6 && hash3(x, 0, z, seed + 11) < 0.4) ? BLOCK.gravel : BLOCK.sand;
      under = BLOCK.sand;
    } else if (h >= snowY && slope <= 6) { top = BLOCK.snow; under = BLOCK.stone; }
    else if (steep || h >= TREE_LINE) { top = BLOCK.stone; under = BLOCK.stone; }
    else { top = BLOCK.grass; under = BLOCK.dirt; }
    if (top === BLOCK.grass && biome === BIOME.frost) { top = BLOCK.snow; under = BLOCK.dirt; }
    else if (top === BLOCK.grass && biome === BIOME.desert) { top = BLOCK.sand; under = BLOCK.sand; }
    const caveMouth = h > SEA_LEVEL + 3 && valueNoise(x / 30, z / 30, seed + 190) > 0.82;
    return columns.set(x, z, { h, biome, top, under, steep, caveMouth });
  }

  return { surfaceHeight, biomeAt, column };
}
