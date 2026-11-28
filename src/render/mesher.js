// The mesher: turns one 16 x 16 x 16 section of the world into triangles for the graphics card.
//
// Only faces that can be seen are emitted (a face against an opaque block is skipped). Each corner of each face carries:
//   uv, layer   where in the block textures to look
//   light       x: ambient occlusion times the face's own shading (corners in creases are darker, like Minecraft's smooth lighting)
//               y: sky light at the corner, 0-1 (light.js), averaged over the open cells round the corner (smooth lighting)
//               z: block light at the corner (torches, lava, glowstone), 0-1, averaged the same way
//   tint        the biome colour at that column, for grass and leaves (blended over the neighbouring columns).
//               Liquids use it for something else: x = how deep the liquid is under that corner (0 at the shore, 1 at 12+
//               blocks), y = 1 for water and 0 for lava, so the liquid shader can darken deep water and treat lava apart.
// Two meshes come out: 'solid' (opaque, leaves, glass, plants: drawn without blending) and 'liquid' (water, lava: blended).
import { BLOCK, BLOCKS, LIGHT_OF } from '../world/blocks.js';
import { sectionIndex } from '../world/chunk.js';
import { BIOMES } from '../world/biomes.js';
import { CHUNK_SIZE as S, WORLD_HEIGHT } from '../world/constants.js';

const P = S + 2;                                   // padded size: the section plus one block of its neighbours on every side
const pidx = (x, y, z) => ((y + 1) * P + (z + 1)) * P + (x + 1);

const RENDER = BLOCKS.map(b => b.render);
const OPAQUE = Uint8Array.from(BLOCKS, b => (b.render === 'cube' ? 1 : 0));
const TINTED = Uint8Array.from(BLOCKS, b => (b.tint ? 1 : 0));

// The six faces: normal n, and the two axes across the face (u, v) with u x v = n, so corners in the order
// (0,0) (1,0) (1,1) (0,1) wind counter-clockwise seen from outside. Side faces have v pointing up, so textures stand upright.
const FACES = [
  { n: [1, 0, 0], u: [0, 0, -1], v: [0, 1, 0], shade: 0.80 },   // east
  { n: [-1, 0, 0], u: [0, 0, 1], v: [0, 1, 0], shade: 0.80 },   // west
  { n: [0, 1, 0], u: [1, 0, 0], v: [0, 0, -1], shade: 1.00 },   // up
  { n: [0, -1, 0], u: [1, 0, 0], v: [0, 0, 1], shade: 0.55 },   // down
  { n: [0, 0, 1], u: [1, 0, 0], v: [0, 1, 0], shade: 0.68 },    // south
  { n: [0, 0, -1], u: [-1, 0, 0], v: [0, 1, 0], shade: 0.68 },  // north
];
const CORNERS = [[0, 0], [1, 0], [1, 1], [0, 1]];
const AO_LEVELS = [0.42, 0.62, 0.82, 1.0];
export const LIQUID_DROP = 0.125;                        // a liquid's surface sits this far below the top of its block
const LIQUID_DEEP = 12;                           // liquid this deep (or more) counts as fully deep
const WATER = BLOCK.water;

class Buffers {
  constructor() { this.pos = []; this.uv = []; this.layer = []; this.light = []; this.tint = []; this.index = []; this.count = 0; }
  vertex(x, y, z, u, v, layer, ao, sky, glow, tint) {
    this.pos.push(x, y, z); this.uv.push(u, v); this.layer.push(layer); this.light.push(ao, sky, glow); this.tint.push(tint[0], tint[1], tint[2]);
    return this.count++;
  }
  quad(a, b, c, d, flip) {
    if (flip) this.index.push(b, c, d, b, d, a); else this.index.push(a, b, c, a, c, d);
  }
  result() {
    if (!this.count) return null;
    return {
      position: new Float32Array(this.pos), uv: new Float32Array(this.uv), layer: new Float32Array(this.layer),
      light: new Float32Array(this.light), tint: new Float32Array(this.tint),
      index: this.count > 65535 ? new Uint32Array(this.index) : new Uint16Array(this.index),
    };
  }
}

/**
 * Mesh one section.
 * @param {import('../world/world.js').World} world
 * @param {Int16Array} faceLayer  texture layer per block id and face (from textures.js)
 * @returns {{solid: object|null, liquid: object|null}} arrays ready for a BufferGeometry, or null where there is nothing to draw
 */
export function meshSection(world, cx, cz, sy, faceLayer) {
  const x0 = cx * S, y0 = sy * S, z0 = cz * S;

  // 1. copy the section and a one-block border round it into a padded array (neighbour chunks included)
  const ids = new Uint16Array(P * P * P);
  const light = new Uint8Array(P * P * P).fill(0xF0); // light bytes (sky << 4 | block), open sky where there is no chunk
  for (let dz = -1; dz <= S; dz++) for (let dx = -1; dx <= S; dx++) {
    const wx = x0 + dx, wz = z0 + dz, ccx = Math.floor(wx / S), ccz = Math.floor(wz / S);
    const chunk = world.getChunk(ccx, ccz);
    if (!chunk) continue;
    const lx = wx - ccx * S, lz = wz - ccz * S;
    for (let dy = -1; dy <= S; dy++) {
      const wy = y0 + dy;
      if (wy < 0 || wy >= WORLD_HEIGHT) continue;
      ids[pidx(dx, dy, dz)] = chunk.get(lx, wy, lz);
      const ls = chunk.light?.[wy >> 4];
      if (ls) light[pidx(dx, dy, dz)] = ls[sectionIndex(lx, wy & 15, lz)];
    }
  }

  // 2. the biome colours of the columns, each blended with its neighbours so biome edges fade instead of stepping
  const tintGrass = [], tintFoliage = [];
  {
    const g = world.generator, raw = [];
    for (let dz = -3; dz <= S + 2; dz++) for (let dx = -3; dx <= S + 2; dx++) raw.push(BIOMES[g.biomeAt(x0 + dx, z0 + dz)]);
    const W = S + 6;
    for (let dz = -1; dz <= S; dz++) for (let dx = -1; dx <= S; dx++) {
      let gr = 0, gg = 0, gb = 0, fr = 0, fg = 0, fb = 0, n = 0;
      for (let oz = -2; oz <= 2; oz++) for (let ox = -2; ox <= 2; ox++) {
        const b = raw[(dz + oz + 3) * W + (dx + ox + 3)];
        gr += b.grass[0]; gg += b.grass[1]; gb += b.grass[2]; fr += b.foliage[0]; fg += b.foliage[1]; fb += b.foliage[2]; n++;
      }
      tintGrass.push([gr / n / 255, gg / n / 255, gb / n / 255]);
      tintFoliage.push([fr / n / 255, fg / n / 255, fb / n / 255]);
    }
  }
  const NO_TINT = [1, 1, 1];
  const tintAt = (id, dx, dz) => {
    if (!TINTED[id]) return NO_TINT;
    const i = (dz + 1) * P + (dx + 1);
    return BLOCKS[id].tint === 'foliage' ? tintFoliage[i] : tintGrass[i];
  };

  const skyAt = (x, y, z) => (light[pidx(x, y, z)] >> 4) / 15;
  const glowAt = (x, y, z) => (light[pidx(x, y, z)] & 15) / 15;

  // how deep the liquid is at a padded column, counted down from the layer y (cached: lakes are mostly one level)
  const depthCache = new Map();
  const liquidDepth = (dx, y, dz, id) => {
    if (dx < -1 || dz < -1 || dx > S || dz > S || ids[pidx(dx, y, dz)] !== id) return 0;
    const key = (y * P + dz + 1) * P + dx + 1;
    let d = depthCache.get(key);
    if (d === undefined) {
      const wx = x0 + dx, wz = z0 + dz;
      d = 0;
      while (d < LIQUID_DEEP && world.getBlock(wx, y0 + y - d, wz) === id) d++;
      depthCache.set(key, d);
    }
    return d;
  };
  const liquidTint = (id, px, y, pz) => {
    const cx = Math.round(px), cz = Math.round(pz);
    const d = liquidDepth(cx - 1, y, cz - 1, id) + liquidDepth(cx, y, cz - 1, id) + liquidDepth(cx - 1, y, cz, id) + liquidDepth(cx, y, cz, id);
    return [d / 4 / LIQUID_DEEP, id === WATER ? 1 : 0, 0];
  };

  const solid = new Buffers(), liquid = new Buffers();

  for (let y = 0; y < S; y++) for (let z = 0; z < S; z++) for (let x = 0; x < S; x++) {
    const id = ids[pidx(x, y, z)];
    if (!id) continue;
    const render = RENDER[id];
    if (render === 'none') continue;

    if (render === 'cross') { emitCross(solid, id, x, y, z, faceLayer[id * 6], skyAt(x, y, z), glowAt(x, y, z), tintAt(id, x, z)); continue; }
    if (render === 'torch') { emitTorch(solid, x, y, z, faceLayer[id * 6], skyAt(x, y, z), LIGHT_OF[id] / 15); continue; }

    const isLiquid = render === 'liquid';
    const out = isLiquid ? liquid : solid;
    const lowered = isLiquid && ids[pidx(x, y + 1, z)] !== id;

    for (let f = 0; f < 6; f++) {
      const F = FACES[f], nx = x + F.n[0], ny = y + F.n[1], nz = z + F.n[2];
      const other = ids[pidx(nx, ny, nz)];
      // is this face hidden?
      if (OPAQUE[other]) continue;
      if (other === id && render !== 'cutout') continue;                       // glass against glass, water against water
      if (isLiquid && other && RENDER[other] !== 'cross' && RENDER[other] !== 'none' && f !== 2) continue; // water sides against any block
      if (isLiquid && f === 2 && other && RENDER[other] === 'liquid') continue;

      const layer = faceLayer[id * 6 + f], tint = tintAt(id, x, z), ownGlow = LIGHT_OF[id] / 15;   // a glowing block is lit by itself
      const v = [];
      for (let k = 0; k < 4; k++) {
        const [su, sv] = CORNERS[k];
        const du = su ? 1 : -1, dv = sv ? 1 : -1;
        // the three cells beside this corner, in the layer of cells in front of the face
        const ax = nx + F.u[0] * du, ay = ny + F.u[1] * du, az = nz + F.u[2] * du;
        const bx = nx + F.v[0] * dv, by = ny + F.v[1] * dv, bz = nz + F.v[2] * dv;
        const cx2 = nx + F.u[0] * du + F.v[0] * dv, cy2 = ny + F.u[1] * du + F.v[1] * dv, cz2 = nz + F.u[2] * du + F.v[2] * dv;
        const sa = OPAQUE[ids[pidx(ax, ay, az)]], sb = OPAQUE[ids[pidx(bx, by, bz)]], sc = OPAQUE[ids[pidx(cx2, cy2, cz2)]];
        const ao = isLiquid ? 3 : (sa && sb ? 0 : 3 - sa - sb - sc);
        // smooth light: the average over the open cells among the four round this corner
        let skySum = skyAt(nx, ny, nz), glowSum = glowAt(nx, ny, nz), n = 1;
        if (!sa) { skySum += skyAt(ax, ay, az); glowSum += glowAt(ax, ay, az); n++; }
        if (!sb) { skySum += skyAt(bx, by, bz); glowSum += glowAt(bx, by, bz); n++; }
        if (!sc && !(sa && sb)) { skySum += skyAt(cx2, cy2, cz2); glowSum += glowAt(cx2, cy2, cz2); n++; }
        let px = x + 0.5 + 0.5 * F.n[0] + (su - 0.5) * F.u[0] + (sv - 0.5) * F.v[0];
        let py = y + 0.5 + 0.5 * F.n[1] + (su - 0.5) * F.u[1] + (sv - 0.5) * F.v[1];
        const pz = z + 0.5 + 0.5 * F.n[2] + (su - 0.5) * F.u[2] + (sv - 0.5) * F.v[2];
        if (lowered && py > y + 0.99) py -= LIQUID_DROP;
        v.push({ px, py, pz, u: su, v: sv, ao, sky: skySum / n, glow: Math.max(glowSum / n, ownGlow), tint: isLiquid ? liquidTint(id, px, y, pz) : tint });
      }
      const idx = v.map(c => out.vertex(c.px, c.py, c.pz, c.u, c.v, layer, AO_LEVELS[c.ao] * F.shade, c.sky, c.glow, c.tint));
      // turn the quad's diagonal to follow the darker corners, so shading in creases does not look skewed
      out.quad(idx[0], idx[1], idx[2], idx[3], v[0].ao + v[2].ao < v[1].ao + v[3].ao);
    }
  }
  return { solid: solid.result(), liquid: liquid.result() };
}

/** A plant: two pictures crossed diagonally through the block, each drawn from both sides. */
function emitCross(out, id, x, y, z, layer, sky, glow, tint) {
  const planes = [[[0.15, 0.15], [0.85, 0.85]], [[0.15, 0.85], [0.85, 0.15]]];
  for (const [[ax, az], [bx, bz]] of planes) {
    const a = out.vertex(x + ax, y, z + az, 0, 0, layer, 0.9, sky, glow, tint);
    const b = out.vertex(x + bx, y, z + bz, 1, 0, layer, 0.9, sky, glow, tint);
    const c = out.vertex(x + bx, y + 1, z + bz, 1, 1, layer, 1.0, sky, glow, tint);
    const d = out.vertex(x + ax, y + 1, z + az, 0, 1, layer, 1.0, sky, glow, tint);
    out.quad(a, b, c, d, false);
    out.quad(b, a, d, c, false);       // the back side
  }
}

/**
 * A torch: a stick two pixels square and ten tall standing in the middle of the block, its four sides and top cut from the
 * middle of the torch picture (the flame is the top two rows of the stick).
 */
const TORCH_W = 1 / 16, TORCH_H = 10 / 16, NO_TINT = [1, 1, 1];
function emitTorch(out, x, y, z, layer, sky, glow) {
  const lo = 0.5 - TORCH_W, hi = 0.5 + TORCH_W, u0 = 7 / 16, u1 = 9 / 16;
  const side = (ax, az, bx, bz, shade) => {
    const a = out.vertex(x + ax, y, z + az, u0, 0, layer, shade, sky, glow, NO_TINT);
    const b = out.vertex(x + bx, y, z + bz, u1, 0, layer, shade, sky, glow, NO_TINT);
    const c = out.vertex(x + bx, y + TORCH_H, z + bz, u1, TORCH_H, layer, shade, sky, glow, NO_TINT);
    const d = out.vertex(x + ax, y + TORCH_H, z + az, u0, TORCH_H, layer, shade, sky, glow, NO_TINT);
    out.quad(a, b, c, d, false);
  };
  side(lo, hi, hi, hi, 0.9);       // south
  side(hi, lo, lo, lo, 0.9);       // north
  side(hi, hi, hi, lo, 0.8);       // east
  side(lo, lo, lo, hi, 0.8);       // west
  const t = y + TORCH_H, v0 = TORCH_H - 2 / 16, v1 = TORCH_H;
  const a = out.vertex(x + lo, t, z + hi, u0, v0, layer, 1, sky, glow, NO_TINT);
  const b = out.vertex(x + hi, t, z + hi, u1, v0, layer, 1, sky, glow, NO_TINT);
  const c = out.vertex(x + hi, t, z + lo, u1, v1, layer, 1, sky, glow, NO_TINT);
  const d = out.vertex(x + lo, t, z + lo, u0, v1, layer, 1, sky, glow, NO_TINT);
  out.quad(a, b, c, d, false);
}
