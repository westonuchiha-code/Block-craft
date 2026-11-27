// Which block the player is pointing at: a ray stepped from the eye through the block grid, one cell at a time
// (the standard "DDA" walk), stopping at the first block that can be hit.
import { BLOCKS } from '../world/blocks.js';

const TARGETABLE = Uint8Array.from(BLOCKS, b => (b.render !== 'none' && b.render !== 'liquid' ? 1 : 0));

/**
 * @returns {{x:number,y:number,z:number,id:number,nx:number,ny:number,nz:number,distance:number}|null}
 *   the block hit, and the normal of the face hit (where a new block would go)
 */
export function raycast(world, ox, oy, oz, dx, dy, dz, maxDistance) {
  let x = Math.floor(ox), y = Math.floor(oy), z = Math.floor(oz);
  const stepX = Math.sign(dx), stepY = Math.sign(dy), stepZ = Math.sign(dz);
  const tdx = stepX ? Math.abs(1 / dx) : Infinity, tdy = stepY ? Math.abs(1 / dy) : Infinity, tdz = stepZ ? Math.abs(1 / dz) : Infinity;
  let tx = stepX > 0 ? (x + 1 - ox) * tdx : stepX < 0 ? (ox - x) * tdx : Infinity;
  let ty = stepY > 0 ? (y + 1 - oy) * tdy : stepY < 0 ? (oy - y) * tdy : Infinity;
  let tz = stepZ > 0 ? (z + 1 - oz) * tdz : stepZ < 0 ? (oz - z) * tdz : Infinity;
  let nx = 0, ny = 0, nz = 0, t = 0;
  while (t <= maxDistance) {
    const id = world.getBlock(x, y, z);
    if (TARGETABLE[id]) return { x, y, z, id, nx, ny, nz, distance: t };
    if (tx < ty && tx < tz) { t = tx; tx += tdx; x += stepX; nx = -stepX; ny = 0; nz = 0; }
    else if (ty < tz) { t = ty; ty += tdy; y += stepY; nx = 0; ny = -stepY; nz = 0; }
    else { t = tz; tz += tdz; z += stepZ; nx = 0; ny = 0; nz = -stepZ; }
  }
  return null;
}
