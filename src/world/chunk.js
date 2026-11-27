// A chunk: one 16 x 256 x 16 column of the world, stored as sixteen 16 x 16 x 16 sections. A section that is all air is not
// stored at all (null), which is most of the sky.
import { CHUNK_SIZE, SECTION_HEIGHT, SECTIONS_PER_CHUNK, WORLD_HEIGHT } from './constants.js';
import { IS_OPAQUE } from './blocks.js';

export const SECTION_VOLUME = CHUNK_SIZE * SECTION_HEIGHT * CHUNK_SIZE;

/** Index of a block inside its section: x fastest, then z, then y. */
export const sectionIndex = (lx, ly, lz) => (ly * CHUNK_SIZE + lz) * CHUNK_SIZE + lx;

export class Chunk {
  constructor(cx, cz, sections) {
    this.cx = cx;
    this.cz = cz;
    /** @type {(Uint16Array|null)[]} */
    this.sections = sections ?? new Array(SECTIONS_PER_CHUNK).fill(null);
    /** Blocks the player changed, "x,y,z" (local) -> id: the part of a chunk that has to be saved. */
    this.edits = new Map();
    /** Per column (x + z*16): one above the highest block that stops daylight. Below it, a spot is under cover. */
    this.skyTop = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE);
    for (let lz = 0; lz < CHUNK_SIZE; lz++) for (let lx = 0; lx < CHUNK_SIZE; lx++) this.updateSkyTop(lx, lz);
  }

  /** Recompute one column's sky top (after a block in it changed). */
  updateSkyTop(lx, lz) {
    let y = WORLD_HEIGHT - 1;
    while (y > 0 && !IS_OPAQUE[this.get(lx, y, lz)]) y--;
    this.skyTop[lz * CHUNK_SIZE + lx] = Math.min(255, y + 1);
  }

  get(lx, y, lz) {
    if (y < 0 || y >= WORLD_HEIGHT) return 0;
    const s = this.sections[y >> 4];
    return s ? s[sectionIndex(lx, y & 15, lz)] : 0;
  }

  set(lx, y, lz, id) {
    if (y < 0 || y >= WORLD_HEIGHT) return;
    let s = this.sections[y >> 4];
    if (!s) {
      if (id === 0) return;
      s = this.sections[y >> 4] = new Uint16Array(SECTION_VOLUME);
    }
    s[sectionIndex(lx, y & 15, lz)] = id;
  }

  /** The highest section that holds anything, or -1. */
  topSection() {
    for (let s = SECTIONS_PER_CHUNK - 1; s >= 0; s--) if (this.sections[s]) return s;
    return -1;
  }
}
