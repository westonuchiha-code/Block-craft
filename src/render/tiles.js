// The block art: every texture is a 16 x 16 tile of hand-composed pixels, built here from a few tones laid out in clumps, seams and
// highlights (the same art as the first version, ported). Tiles are pure functions of their own small seeds, so they look the same
// in every world.
//
// A tile is { rgba: Uint8ClampedArray(16*16*4), tint: Uint8Array(16*16) }:
//   rgba  colour, with alpha 0 for holes (leaf gaps, the gaps between grass blades)
//   tint  255 where the texel takes the biome's colour (grass, maple leaves). Those texels are stored as grey (brightness only)
//         and multiplied by the biome colour when drawn.
import { makeRng } from '../core/noise.js';
import { shadeRgb } from '../core/math.js';

const N = 16;
/** Grey stored for a tinted texel of brightness 1.0. Brightness above 1 (highlights) still fits under 255. */
export const TINT_BASE = 0.78;

class Tile {
  constructor(fill = [255, 0, 255]) {
    this.rgba = new Uint8ClampedArray(N * N * 4);
    this.tint = new Uint8Array(N * N);
    for (let i = 0; i < N * N; i++) this.set(i % N, (i / N) | 0, fill);
  }
  /** Set one texel. Row 0 is the TOP of the tile. */
  set(x, y, rgb, alpha = 255) {
    const o = ((y & 15) * N + (x & 15)) * 4;
    this.rgba[o] = rgb[0]; this.rgba[o + 1] = rgb[1]; this.rgba[o + 2] = rgb[2]; this.rgba[o + 3] = alpha;
    this.tint[(y & 15) * N + (x & 15)] = 0;
  }
  /** Set a texel that takes the biome colour, by its brightness (1 = the biome colour itself). */
  setTinted(x, y, brightness) {
    const g = Math.min(255, Math.round(brightness * TINT_BASE * 255));
    this.set(x, y, [g, g, g]);
    this.tint[(y & 15) * N + (x & 15)] = 255;
  }
  hole(x, y) { this.set(x, y, [0, 0, 0], 0); }
  get(x, y) { const o = ((y & 15) * N + (x & 15)) * 4; return [this.rgba[o], this.rgba[o + 1], this.rgba[o + 2]]; }
  copy() { const t = new Tile(); t.rgba.set(this.rgba); t.tint.set(this.tint); return t; }
  /** A tile made by a function of (x, y) returning [r,g,b]. */
  static from(fn) { const t = new Tile(); for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) t.set(x, y, fn(x, y)); return t; }
}

// ---- painting helpers ----

/** Smooth tileable noise 0..1 over the tile, with `cells` lattice points per side. */
function tileNoise(rng, cells) {
  const g = Array.from({ length: cells * cells }, rng);
  const sm = t => t * t * (3 - 2 * t);
  return (x, y) => {
    const fx = (x / N) * cells, fy = (y / N) * cells, x0 = Math.floor(fx), y0 = Math.floor(fy), tx = sm(fx - x0), ty = sm(fy - y0);
    const at = (i, j) => g[(j % cells) * cells + (i % cells)];
    const a = at(x0, y0), b = at(x0 + 1, y0), c = at(x0, y0 + 1), d = at(x0 + 1, y0 + 1);
    return (a + (b - a) * tx) * (1 - ty) + (c + (d - c) * tx) * ty;
  };
}
const pickTone = (palette, v) => palette[Math.min(palette.length - 1, Math.max(0, Math.floor(v * palette.length)))];

/** Fine grain: each texel picks one of a few close tones, soft clumps leaning the choice. */
function grain(rng, palette, cells = 4) {
  const n = tileNoise(rng, cells);
  return Tile.from((x, y) => palette[Math.floor(Math.min(0.999, Math.max(0, rng() * 0.7 + n(x, y) * 0.5 - 0.1)) * palette.length)]);
}
/** Two scales of soft clumps. */
function clumps(rng, palette, big, small, mix) {
  const n1 = tileNoise(rng, big), n2 = tileNoise(rng, small);
  return Tile.from((x, y) => pickTone(palette, n1(x, y) * (1 - mix) + n2(x, y) * mix));
}
/** Small pits: dark dents with an optional light lip below. */
function pits(t, rng, count, dark, light) {
  const shapes = [[[0, 0], [1, 0]], [[0, 0], [0, 1]], [[0, 0], [1, 0], [0, 1]], [[0, 0], [1, 0], [1, 1]]];
  for (let i = 0; i < count; i++) {
    const x = Math.floor(rng() * 15), y = Math.floor(rng() * 14), s = shapes[Math.floor(rng() * shapes.length)];
    for (const [dx, dy] of s) t.set(x + dx, y + dy, dark);
    if (light) t.set(x + 1, y + 2, light);
  }
}
/** `count` short runs (w x h) of one colour, wrapping round the edges. */
function scatter(t, rng, count, w, h, col) {
  for (let i = 0; i < count; i++) {
    const x0 = Math.floor(rng() * N), y0 = Math.floor(rng() * N);
    for (let dy = 0; dy < h; dy++) for (let dx = 0; dx < w; dx++) t.set(x0 + dx, y0 + dy, col);
  }
}
/** Stones separated by dark gaps (nearest-seed cells, tileable), each its own tone, lit on the upper-left edge. */
function cells(rng, count, palette, gap, gapCol, lit) {
  const pts = Array.from({ length: count }, () => [rng() * N, rng() * N, pickTone(palette, rng())]);
  const owner = new Int32Array(N * N), margin = new Float32Array(N * N);
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    let b1 = 1e9, b2 = 1e9, bi = 0;
    pts.forEach(([px, py], i) => {
      let dx = Math.abs(x + 0.5 - px); dx = Math.min(dx, N - dx);
      let dy = Math.abs(y + 0.5 - py); dy = Math.min(dy, N - dy);
      const d = Math.hypot(dx, dy);
      if (d < b1) { b2 = b1; b1 = d; bi = i; } else if (d < b2) b2 = d;
    });
    owner[y * N + x] = bi; margin[y * N + x] = b2 - b1;
  }
  return Tile.from((x, y) => {
    if (margin[y * N + x] < gap) return gapCol;
    const i = owner[y * N + x], edge = owner[((y + 15) % N) * N + x] !== i || owner[y * N + (x + 15) % N] !== i;
    return lit && edge ? shadeRgb(pts[i][2], 1.18) : pts[i][2];
  });
}
/** Mineral nuggets set into stone, each with a glint and a shadow under it (ores, coal). */
function nuggets(stone, rng, spots, dark, mid, light) {
  const t = stone.copy();
  const shapes = [[[1, 0], [2, 0], [0, 1], [1, 1], [2, 1], [1, 2]], [[0, 0], [1, 0], [0, 1], [1, 1], [2, 1], [1, 2], [2, 2]], [[1, 0], [0, 1], [1, 1], [2, 1], [1, 2], [2, 2]]];
  for (const [x0, y0] of spots) {
    const s = shapes[Math.floor(rng() * shapes.length)];
    for (const [dx, dy] of s) t.set(x0 + dx, y0 + dy, mid);
    for (const [dx, dy] of s) if (!s.some(([a, b]) => a === dx && b === dy + 1)) t.set(x0 + dx, y0 + dy + 1, dark);
    t.set(x0 + s[0][0], y0 + s[0][1], light);
  }
  return t;
}

// ---- the tiles ----

/** Build every tile. @returns {Map<string, Tile>} */
export function buildTiles() {
  const tiles = new Map();
  const rng = n => makeRng(7000 + n);
  const add = (name, tile) => { tiles.set(name, tile); return tile; };

  // EARTH AND ROCK
  const dirt = (() => {
    const r = rng(1), t = grain(r, [[88, 60, 40], [100, 70, 46], [112, 80, 52], [124, 90, 60], [134, 98, 66]], 5);
    pits(t, r, 5, [76, 50, 32], null);
    for (let i = 0; i < 6; i++) {               // pale pebbles, each with a shadow under it
      const x = Math.floor(r() * 14), y = Math.floor(r() * 14);
      t.set(x, y, [158, 132, 104]); t.set(x + 1, y, [142, 116, 90]); t.set(x, y + 1, [72, 48, 30]); t.set(x + 1, y + 1, [84, 58, 38]);
    }
    for (let i = 0; i < 7; i++) t.set(Math.floor(r() * 16), Math.floor(r() * 16), [150, 116, 82]);
    return add('dirt', t);
  })();
  const stone = (() => {
    const r = rng(2), t = grain(r, [[106, 108, 112], [116, 118, 122], [126, 128, 132], [136, 138, 142], [146, 148, 152]], 4);
    pits(t, r, 6, [86, 88, 94], [154, 156, 160]);
    for (let i = 0; i < 2; i++) {               // two faint hairline cracks
      const x0 = Math.floor(r() * 11), y0 = Math.floor(r() * 14);
      for (let k = 0; k < 4; k++) t.set(x0 + k, y0 + (k >> 1), [94, 96, 102]);
    }
    return add('stone', t);
  })();
  { const r = rng(71), t = grain(r, [[126, 127, 130], [136, 137, 140], [146, 147, 149], [156, 156, 158]], 5);
    pits(t, r, 7, [104, 104, 110], [168, 168, 170]); scatter(t, r, 10, 1, 1, [92, 92, 98]); add('andesite', t); }
  { const r = rng(72), t = grain(r, [[142, 98, 82], [152, 106, 90], [162, 116, 98], [172, 126, 108]], 4);
    pits(t, r, 6, [118, 78, 64], [196, 160, 140]); scatter(t, r, 9, 1, 1, [206, 176, 158]); scatter(t, r, 6, 1, 1, [104, 70, 58]); add('granite', t); }
  { const r = rng(73), t = grain(r, [[176, 176, 178], [188, 188, 190], [200, 200, 202], [212, 212, 214]], 4);
    pits(t, r, 6, [96, 96, 102], [232, 232, 234]); scatter(t, r, 8, 2, 1, [110, 110, 116]); scatter(t, r, 8, 1, 1, [236, 236, 238]); add('diorite', t); }
  { const r = rng(74), t = grain(r, [[78, 80, 72], [88, 90, 80], [98, 100, 88], [110, 112, 98]], 3);
    for (let i = 0; i < 5; i++) { const y = Math.floor(r() * 16), x0 = Math.floor(r() * 16), len = 4 + Math.floor(r() * 4); for (let k = 0; k < len; k++) t.set(x0 + k, y, [120, 122, 106]); }
    pits(t, r, 4, [60, 62, 56], null); add('tuff', t); }
  { const r = rng(75), t = stone.copy(), n = tileNoise(r, 4);
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const v = n(x, y) + r() * 0.25;
      if (v > 0.62) t.set(x, y, v > 0.82 ? [104, 152, 72] : v > 0.72 ? [84, 130, 60] : [66, 106, 50]);
    }
    scatter(t, r, 5, 1, 1, [120, 170, 84]); add('mossy_rock', t); }
  add('cobblestone', cells(rng(3), 10, [[112, 112, 116], [126, 126, 130], [140, 140, 144], [100, 102, 108], [132, 128, 124]], 0.8, [58, 58, 62], true));
  add('gravel', cells(rng(4), 22, [[116, 112, 108], [134, 130, 126], [100, 98, 98], [148, 142, 134], [122, 114, 104], [92, 90, 92]], 0.55, [70, 68, 68], true));
  { const r = rng(5), t = clumps(r, [[214, 200, 150], [222, 208, 158], [230, 216, 168]], 4, 8, 0.3);
    scatter(t, r, 18, 1, 1, [194, 178, 130]); scatter(t, r, 7, 2, 1, [240, 228, 186]); scatter(t, r, 4, 1, 2, [200, 184, 138]); add('sand', t); }
  add('bedrock', clumps(rng(10), [[30, 30, 34], [44, 44, 48], [58, 58, 62], [22, 22, 26]], 4, 8, 0.5));
  { const r = rng(11), t = clumps(r, [[232, 238, 246], [240, 245, 251], [248, 250, 255]], 4, 8, 0.3); scatter(t, r, 5, 1, 1, [210, 224, 240]); add('snow', t); }
  { const r = rng(31), t = clumps(r, [[20, 14, 32], [30, 22, 46], [42, 30, 64], [26, 18, 40]], 4, 8, 0.4);
    scatter(t, r, 6, 1, 1, [96, 80, 140]); scatter(t, r, 3, 2, 1, [58, 44, 90]); add('obsidian', t); }
  add('lava', clumps(rng(30), [[130, 34, 10], [188, 62, 12], [232, 104, 18], [255, 170, 44]], 4, 8, 0.45));
  add('glowstone', cells(rng(12), 9, [[255, 236, 150], [255, 222, 120], [255, 246, 190], [246, 204, 96]], 0.6, [196, 148, 60], true));

  const n8 = tileNoise(rng(82), 8), n4 = tileNoise(rng(81), 4);
  add('sandstone_side', Tile.from((x, y) => shadeRgb([216, 192, 134], (y % 5 === 0 ? 0.86 : y % 5 === 1 ? 1.04 : 0.97) * (0.95 + 0.1 * n8(x, y)))));
  add('sandstone_top', Tile.from((x, y) => shadeRgb([222, 200, 142], 0.94 + 0.12 * n8(x, y))));
  add('ice', Tile.from((x, y) => {
    const k = n8(x, y), crack = (x * 3 + y * 5) % 11 === 0 || (x * 7 - y * 2 + 40) % 13 === 0;
    return crack ? [226, 242, 252] : shadeRgb([150 + 20 * k, 198 + 14 * k, 234], 0.9 + 0.2 * n4(x, y));
  }));
  add('cactus_side', Tile.from((x, y) => {
    if (x % 4 === 2 && y % 3 === 1) return [236, 230, 190];                     // spines
    return shadeRgb([66, 126, 58], (x % 4 === 0 ? 0.78 : x % 4 === 1 ? 1.1 : 1.0) * (0.94 + 0.12 * n8(x, y)));
  }));
  add('cactus_top', Tile.from((x, y) => {
    const d = Math.max(Math.abs(x - 7.5), Math.abs(y - 7.5));
    return d > 6 ? [50, 98, 44] : d > 3 ? shadeRgb([86, 150, 72], 0.95 + 0.1 * n8(x, y)) : [228, 214, 120];
  }));
  { const r = rng(40), n = tileNoise(r, 4), m = tileNoise(r, 8);
    add('water', Tile.from((x, y) => {
      const v = n(x, y) * 0.6 + m(x, y) * 0.4;
      return v > 0.66 ? [70, 120, 210] : v > 0.45 ? [48, 92, 196] : [38, 74, 178];
    })); }

  // ORES: stone with clusters of mineral. Iron rusty tan, mithril pale silver-blue, adamantite deep green.
  { const r = rng(9), t = stone.copy();
    const shapes = [[[1, 0], [2, 0], [0, 1], [1, 1], [2, 1], [1, 2], [2, 2]], [[0, 0], [1, 0], [0, 1], [1, 1], [2, 1], [0, 2], [1, 2]], [[1, 0], [0, 1], [1, 1], [2, 1], [1, 2]]];
    for (const [x0, y0] of [[1, 1], [9, 0], [5, 6], [11, 7], [1, 10], [8, 12]]) {
      const s = shapes[Math.floor(r() * shapes.length)];
      for (const [dx, dy] of s) t.set(x0 + dx, y0 + dy, [26, 26, 30]);
      for (const [dx, dy] of s) if (!s.some(([a, b]) => a === dx && b === dy + 1)) t.set(x0 + dx, y0 + dy + 1, [84, 86, 92]);
      t.set(x0 + s[0][0], y0 + s[0][1], [116, 118, 132]); t.set(x0 + s[1][0], y0 + s[1][1], [56, 56, 66]);
    }
    add('coal_ore', t); }
  const oreSpots = [[2, 1], [10, 2], [6, 7], [12, 9], [2, 11], [8, 13]];
  add('iron_ore', nuggets(stone, rng(201), oreSpots, [140, 96, 64], [206, 160, 122], [244, 214, 182]));
  add('adamantite_ore', nuggets(stone, rng(202), oreSpots, [20, 70, 48], [48, 160, 104], [170, 246, 206]));
  add('mithril_ore', nuggets(stone, rng(203), oreSpots, [60, 96, 168], [140, 196, 255], [255, 255, 255]));

  // GRASS: the top is brightness only (it takes the biome colour); the side is dirt under a ragged fringe of grass
  { const r = rng(6), n1 = tileNoise(r, 4), n2 = tileNoise(r, 8), t = new Tile();
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const v = n1(x, y) * 0.65 + n2(x, y) * 0.35;
      t.setTinted(x, y, v < 0.3 ? 0.86 : v < 0.7 ? 0.96 : 1.06);
    }
    for (let i = 0; i < 10; i++) { const x = Math.floor(r() * 16), y = Math.floor(r() * 15); t.setTinted(x, y, 0.7); t.setTinted(x, y + 1, 0.82); }
    for (let i = 0; i < 3; i++) t.setTinted(Math.floor(r() * 16), Math.floor(r() * 16), 1.15);
    add('grass_top', t);
    const side = dirt.copy(), r2 = rng(7);
    for (let x = 0; x < N; x++) {
      const depth = 2 + Math.floor(r2() * 3);
      for (let y = 0; y < depth; y++) side.setTinted(x, y, (y === depth - 1 ? 0.8 : 0.95) * (0.92 + 0.12 * n1(x, y)));
    }
    add('grass_side', side); }

  // TALL GRASS: a tuft of tinted blades on a clear background
  { const r = rng(41), t = new Tile();
    for (let i = 0; i < N * N; i++) t.hole(i % N, (i / N) | 0);
    for (let b = 0; b < 9; b++) {
      let x = 1 + Math.floor(r() * 14); const h = 6 + Math.floor(r() * 9), lean = r() < 0.5 ? -1 : 1;
      for (let k = 0; k < h; k++) {
        if (k > 3 && r() < 0.25) x = Math.max(0, Math.min(15, x + lean));
        t.setTinted(x, 15 - k, 0.75 + 0.35 * (k / h));
      }
    }
    add('tall_grass', t); }

  // WOOD: planks per wood (the same board pattern in each wood's colour), bark and cut ends per species
  const planksPattern = (() => {
    const r = rng(8), tones = [1.0, 0.95, 1.05, 0.98], t = [];
    for (let y = 0; y < N; y++) { t.push([]); for (let x = 0; x < N; x++) t[y].push(1); }
    for (let b = 0; b < 4; b++) {
      for (let y = b * 4; y < b * 4 + 4; y++) for (let x = 0; x < N; x++) t[y][x] = tones[b] * (y === b * 4 ? 0.66 : y === b * 4 + 3 ? 0.9 : 1);
      for (let i = 0; i < 4; i++) {
        const gx = Math.floor(r() * 16), gy = b * 4 + 1 + Math.floor(r() * 2), len = 3 + Math.floor(r() * 5);
        for (let k = 0; k < len; k++) t[gy][(gx + k) % 16] = tones[b] * 0.86;
      }
      const nail = Math.floor(r() * 16);
      t[b * 4 + 1][nail] = tones[b] * 0.55; t[b * 4 + 1][(nail + 8) % 16] = tones[b] * 0.55;
    }
    return t;
  })();
  const PLANK_COLOUR = { maple: [182, 146, 96], oak: [150, 110, 66], birch: [214, 196, 146], spruce: [112, 80, 50], palm: [196, 160, 112] };
  for (const [wood, c] of Object.entries(PLANK_COLOUR)) add(`${wood}_planks`, Tile.from((x, y) => shadeRgb(c, planksPattern[y][x])));

  // bark: tall ridges 2-3 px wide (dark furrow, lit edge, body), light and dark in short stretches, a few cross-scars
  const bark = (seed, [furrow, low, mid, high], scar) => {
    const r = rng(seed), t = new Tile(low), widths = [];
    for (let s = 0; s < N;) { const w = Math.min(N - s, 2 + Math.floor(r() * 2)); if (N - s - w === 1) { widths.push(N - s); s = N; } else { widths.push(w); s += w; } }
    let x = 0;
    for (const w of widths) {
      for (let k = 0; k < w; k++) {
        const base = k === 0 ? furrow : k === 1 ? high : k === 2 ? mid : low, y0 = Math.floor(r() * 4);
        let dark = false;
        for (let n = 0; n < N; n++) {
          if (n === 0 || r() < 0.2) dark = k >= 1 && r() < 0.35;
          t.set(x + k, y0 + n, dark ? (base === high ? mid : base === mid ? low : base) : (k === 0 && r() < 0.12 ? low : base));
        }
      }
      x += w;
    }
    for (let i = 0; i < 3; i++) { const bx = Math.floor(r() * 14), by = 2 + Math.floor(r() * 11); t.set(bx, by, scar); t.set(bx + 1, by, scar); t.set(bx, by + 1, high); }
    return t;
  };
  const rings = (barkCol, wood, wood2, heart) => Tile.from((x, y) => {
    const d = Math.max(Math.abs(x - 7.5), Math.abs(y - 7.5));
    return d > 7 ? barkCol : d < 1.6 ? heart : Math.floor(d * 0.9) % 2 ? wood2 : wood;
  });
  add('maple_log_side', bark(20, [[48, 44, 40], [92, 86, 78], [112, 104, 96], [134, 126, 116]], [34, 32, 30]));
  add('oak_log_side', bark(21, [[46, 32, 20], [96, 70, 44], [118, 88, 56], [140, 108, 70]], [30, 20, 12]));
  add('birch_log_side', bark(22, [[196, 194, 184], [222, 220, 210], [236, 234, 226], [246, 244, 238]], [44, 42, 40]));
  add('spruce_log_side', bark(23, [[30, 22, 14], [66, 48, 32], [84, 62, 42], [104, 80, 56]], [20, 14, 8]));
  add('palm_log_side', Tile.from((x, y) => shadeRgb([156, 122, 84], (y % 4 === 0 ? 0.72 : y % 4 === 1 ? 0.9 : 1.04) * (0.94 + 0.12 * n8(x, y)) * ((x + y * 2) % 7 === 0 ? 0.88 : 1))));
  add('maple_log_top', rings([84, 78, 72], [190, 160, 116], [172, 140, 98], [150, 112, 76]));
  add('oak_log_top', rings([76, 56, 38], [172, 134, 86], [152, 114, 70], [128, 90, 52]));
  add('birch_log_top', rings([222, 220, 210], [214, 194, 140], [200, 176, 120], [168, 140, 92]));
  add('spruce_log_top', rings([60, 44, 30], [128, 94, 60], [112, 80, 50], [92, 64, 38]));
  add('palm_log_top', Tile.from((x, y) => { const d = Math.hypot(x - 7.5, y - 7.5); return d > 7 ? [120, 92, 62] : Math.floor(d) % 2 ? [196, 160, 112] : [176, 140, 96]; }));

  // leaves: clumps of leaf tones with darker pockets, and small gaps you can see through. Maple takes the biome colour.
  { const r = rng(13), n1 = tileNoise(r, 4), n2 = tileNoise(r, 8);
    const shadeAt = (x, y) => { const v = n1(x, y) * 0.55 + n2(x, y) * 0.45; return v < 0.35 ? 0.72 : v < 0.65 ? 0.92 : 1.1; };
    const r2 = rng(14), h1 = tileNoise(r2, 8), h2 = tileNoise(r2, 4);
    const isHole = (x, y) => h1(x, y) * 0.6 + h2(x, y) * 0.4 > 0.64;
    const LEAF = { oak: [56, 108, 38], birch: [122, 160, 64], spruce: [34, 78, 54], palm: [84, 152, 52] };
    const maple = new Tile();
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) isHole(x, y) ? maple.hole(x, y) : maple.setTinted(x, y, shadeAt(x, y));
    add('maple_leaves', maple);
    for (const [wood, c] of Object.entries(LEAF)) {
      const t = new Tile();
      for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) isHole(x, y) ? t.hole(x, y) : t.set(x, y, shadeRgb(c, shadeAt(x, y)));
      add(`${wood}_leaves`, t);
    } }

  // GLASS: pale blue with a bright frame and two diagonal glints; mostly see-through
  { const t = new Tile();
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) t.set(x, y, [200, 228, 240], 0);
    for (let i = 0; i < N; i++) for (const [x, y] of [[i, 0], [i, 15], [0, i], [15, i]]) t.set(x, y, [214, 236, 246]);
    for (let i = 1; i < 15; i++) { for (const [x, y] of [[i, 1], [1, i]]) t.set(x, y, [190, 224, 240], 200); for (const [x, y] of [[i, 14], [14, i]]) t.set(x, y, [150, 190, 214], 200); }
    for (let k = 0; k < 4; k++) { t.set(3 + k, 3 + k, [240, 250, 255], 230); t.set(4 + k, 3 + k, [226, 244, 252], 200); }
    for (let k = 0; k < 2; k++) t.set(3 + k, 9 + k, [240, 250, 255], 230);
    add('glass', t); }

  return tiles;
}

/** A plain colour per tile (its average), for things drawn without textures: the map, particles, distant terrain. */
export function averageColour(tile) {
  let r = 0, g = 0, b = 0, n = 0;
  for (let i = 0; i < N * N; i++) if (tile.rgba[i * 4 + 3] > 0) { r += tile.rgba[i * 4]; g += tile.rgba[i * 4 + 1]; b += tile.rgba[i * 4 + 2]; n++; }
  return n ? [r / n, g / n, b / n] : [0, 0, 0];
}

