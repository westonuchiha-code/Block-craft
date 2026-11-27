// The block textures on the graphics card: every tile is one layer of a texture array (so tiles never bleed into each other when
// filtered at a distance), plus a matching array that marks which texels take the biome colour.
import * as THREE from 'three';
import { BLOCKS } from '../world/blocks.js';
import { buildTiles } from './tiles.js';

/** Faces in the order the mesher uses them. */
export const FACE = { east: 0, west: 1, up: 2, down: 3, south: 4, north: 5 };   // +x, -x, +y, -y, +z, -z

export function createBlockTextures(maxAnisotropy) {
  const tiles = buildTiles();
  const names = [...tiles.keys()];
  const layerOf = new Map(names.map((n, i) => [n, i]));
  const size = 16, count = names.length;

  const colour = new Uint8Array(size * size * 4 * count);
  const tint = new Uint8Array(size * size * count);
  names.forEach((name, layer) => {
    const t = tiles.get(name);
    for (let y = 0; y < size; y++) {
      // tile rows run top-down; texture rows run bottom-up (v = 0 at the bottom of a face)
      const src = (size - 1 - y) * size, dst = layer * size * size + y * size;
      colour.set(t.rgba.subarray(src * 4, (src + size) * 4), dst * 4);
      tint.set(t.tint.subarray(src, src + size), dst);
    }
  });

  const arrayTexture = (data, format) => {
    const tex = new THREE.DataArrayTexture(data, size, size, count);
    tex.format = format;
    tex.type = THREE.UnsignedByteType;
    tex.magFilter = THREE.NearestFilter;                  // crisp pixels up close
    tex.minFilter = THREE.LinearMipmapLinearFilter;       // smooth, shimmer-free at a distance
    tex.generateMipmaps = true;
    tex.anisotropy = maxAnisotropy;                       // sharp on surfaces seen at a slant (the ground ahead)
    tex.needsUpdate = true;
    return tex;
  };

  // which layer each face of each block uses
  const faceLayer = new Int16Array(BLOCKS.length * 6).fill(-1);
  for (const b of BLOCKS) {
    if (!b.textures) continue;
    const pick = { 0: b.textures.side, 1: b.textures.side, 2: b.textures.top, 3: b.textures.bottom, 4: b.textures.side, 5: b.textures.side };
    for (let f = 0; f < 6; f++) {
      const layer = layerOf.get(pick[f]);
      if (layer === undefined) throw new Error(`block ${b.key} uses a missing texture: ${pick[f]}`);
      faceLayer[b.id * 6 + f] = layer;
    }
  }

  return {
    colour: arrayTexture(colour, THREE.RGBAFormat),
    tintMask: arrayTexture(tint, THREE.RedFormat),
    faceLayer,
    tiles,
    layerOf,
  };
}
