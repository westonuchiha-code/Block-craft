// Trees. Four shapes:
//   round    one trunk and a round canopy (maple wide, birch tall and slim, oak in between)
//   conifer  a tall cone (spruce)
//   great    a thick 2 x 2 trunk, a wide canopy and big side branches (old oaks)
//   palm     a slim leaning trunk with a crown of drooping fronds
// A tree is fully described by where its root is and the seed, so every chunk it reaches can draw its own part of it.
import { hash3 } from '../core/noise.js';

/** Leaves in a flat disc of radius r around a centre, with a ragged edge. */
function leafDisc(out, cx, y, cz, r, layer, seed) {
  for (let x = Math.floor(cx - r - 1); x <= Math.ceil(cx + r); x++) {
    for (let z = Math.floor(cz - r - 1); z <= Math.ceil(cz + r); z++) {
      const d2 = (x + 0.5 - cx) ** 2 + (z + 0.5 - cz) ** 2;
      if (d2 > r * r) continue;
      if (r > 1.4 && d2 > (r - 1) ** 2 && hash3(x, y * 5 + layer, z, seed + 78) < 0.25) continue;
      out.push([x, y, z]);
    }
  }
}

/**
 * The blocks of one tree whose trunk starts at (x, y, z).
 * For 'great', (x, z) is the corner of its 2 x 2 trunk.
 * @returns {{logs: number[][], leaves: number[][]}}
 */
export function buildTree(wood, shape, x, y, z, seed) {
  const logs = [], leaves = [];
  const rand = i => hash3(x, y * 7 + i, z, seed + 77);

  if (shape === 'round') {
    const wide = wood === 'maple', tall = wood === 'birch';
    const height = (tall ? 5 : 4) + Math.floor(rand(0) * 3) + (wide ? 1 : 0);
    for (let i = 0; i < height; i++) logs.push([x, y + i, z]);
    const crown = y + height - 1;
    const layers = wide ? [[-2, 2.3], [-1, 3.1], [0, 3.1], [1, 2.3], [2, 1.4]]
                 : tall ? [[-2, 1.6], [-1, 2.2], [0, 2.2], [1, 1.6], [2, 1.0]]
                 : [[-1, 2.4], [0, 2.4], [1, 1.7], [2, 1.0]];
    layers.forEach(([dy, r], k) => leafDisc(leaves, x + 0.5, crown + dy, z + 0.5, r, k, seed));

  } else if (shape === 'palm') {
    const height = 6 + Math.floor(rand(0) * 4);
    const lean = [[1, 0], [0, 1], [-1, 0], [0, -1]][Math.floor(rand(1) * 4)];
    let tx = x, tz = z;
    for (let i = 0; i < height; i++) {
      const off = i >= 3 ? Math.floor((i - 1) / 3) : 0;
      tx = x + lean[0] * off; tz = z + lean[1] * off;
      logs.push([tx, y + i, tz]);
    }
    const top = y + height - 1;
    leaves.push([tx, top + 1, tz]);
    for (const [ax, az] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1]]) {
      const reach = ax && az ? 2 : 4;
      for (let k = 1; k <= reach; k++) leaves.push([tx + ax * k, k <= 2 ? top + 1 : k === 3 ? top : top - 1, tz + az * k]);
    }

  } else if (shape === 'conifer') {
    const height = 7 + Math.floor(rand(0) * 4);
    for (let i = 0; i < height; i++) logs.push([x, y + i, z]);
    const crown = y + height - 1, radii = [0.6, 1.5, 2.4, 1.5, 2.4, 3.2, 2.4, 3.2, 2.4, 3.2];
    for (let k = 0; k < height; k++) leafDisc(leaves, x + 0.5, crown + 2 - k, z + 0.5, radii[Math.min(k, radii.length - 1)], k, seed);

  } else { // great
    const height = 9 + Math.floor(rand(0) * 5);
    for (let dx = 0; dx < 2; dx++) for (let dz = 0; dz < 2; dz++) for (let i = -1; i < height; i++) logs.push([x + dx, y + i, z + dz]);
    const crown = y + height - 1;
    [[-4, 2.5], [-3, 4.0], [-2, 4.8], [-1, 5.0], [0, 4.6], [1, 3.6], [2, 2.2], [3, 1.2]]
      .forEach(([dy, r], k) => leafDisc(leaves, x + 1, crown + dy, z + 1, r, k, seed));
    // big branches from the upper trunk, each ending in a puff of leaves
    const dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]];
    const branches = 3 + (rand(1) > 0.5 ? 1 : 0), d0 = Math.floor(rand(30) * 4);
    for (let b = 0; b < branches; b++) {
      const [dx, dz] = dirs[(b + d0) % 4], side = rand(40 + b) > 0.5 ? 1 : 0;
      const bx = dx > 0 ? x + 2 : dx < 0 ? x - 1 : x + side;
      const bz = dz > 0 ? z + 2 : dz < 0 ? z - 1 : z + side;
      const by = y + Math.floor(height * 0.45) + Math.floor(rand(10 + b) * height * 0.3);
      const len = 2 + Math.floor(rand(20 + b) * 3);
      let ex = bx, ey = by, ez = bz;
      for (let i = 0; i < len; i++) { ex = bx + dx * i; ez = bz + dz * i; ey = by + Math.floor(i / 2); logs.push([ex, ey, ez]); }
      leafDisc(leaves, ex + 0.5, ey - 1, ez + 0.5, 2.0, 0, seed);
      leafDisc(leaves, ex + 0.5, ey, ez + 0.5, 2.4, 1, seed);
      leafDisc(leaves, ex + 0.5, ey + 1, ez + 0.5, 1.6, 2, seed);
    }
  }
  return { logs, leaves };
}

/** How far a tree can reach from its root, so a chunk knows how far around it to look for trees. */
export const TREE_REACH = 9;
