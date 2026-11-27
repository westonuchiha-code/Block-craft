// Small pictures of blocks for the hotbar: the block seen from above at an angle, its three visible faces shaded like the world.
import { BLOCKS } from '../world/blocks.js';
import { BIOMES } from '../world/biomes.js';
import { TINT_BASE } from '../render/tiles.js';

const cache = new Map();

/** @returns {HTMLCanvasElement} a 64 x 64 picture of the block */
export function blockIcon(id, tiles) {
  if (cache.has(id)) return copy(cache.get(id));
  const b = BLOCKS[id], size = 64;
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const g = canvas.getContext('2d');
  g.imageSmoothingEnabled = false;
  if (b.textures) {
    const tint = b.tint === 'foliage' ? BIOMES[0].foliage : b.tint === 'grass' ? BIOMES[1].grass : null;
    const face = (name, shade) => tileCanvas(tiles.get(name), tint, shade);
    if (b.render === 'cross' || b.render === 'torch') {
      g.drawImage(face(b.textures.side, 1), 8, 8, 48, 48);
    } else {
      // top: squashed diamond; left and right: slanted sides. Each tile is drawn through a transform onto its face.
      const s = size / 2;
      g.setTransform(s / 16, s / 32, -s / 16, s / 32, s, 0);                       // top
      g.drawImage(face(b.textures.top, 1), 0, 0);
      g.setTransform(s / 16, s / 32, 0, s / 16, 0, s / 2);                    // left
      g.drawImage(face(b.textures.side, 0.78), 0, 0);
      g.setTransform(s / 16, -s / 32, 0, s / 16, s, s);                       // right
      g.drawImage(face(b.textures.side, 0.6), 0, 0);
      g.setTransform(1, 0, 0, 1, 0, 0);
    }
  }
  cache.set(id, canvas);
  return copy(canvas);
}

function copy(src) {
  const c = document.createElement('canvas');
  c.width = src.width; c.height = src.height;
  c.getContext('2d').drawImage(src, 0, 0);
  return c;
}

function tileCanvas(tile, tint, shade) {
  const c = document.createElement('canvas');
  c.width = c.height = 16;
  const img = new ImageData(16, 16);
  for (let i = 0; i < 256; i++) {
    const t = tile.tint[i] && tint ? tint.map(v => v / 255 / TINT_BASE) : [1, 1, 1];
    for (let k = 0; k < 3; k++) img.data[i * 4 + k] = Math.min(255, tile.rgba[i * 4 + k] * t[k] * shade);
    img.data[i * 4 + 3] = tile.rgba[i * 4 + 3];
  }
  c.getContext('2d').putImageData(img, 0, 0);
  return c;
}
