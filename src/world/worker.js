// A world-generation worker: it builds whole chunks on its own CPU core, so new land never makes the game stutter.
// Messages in:  { seed }                    start (or switch) to a world
//               { id, cx, cz }              build this chunk
// Messages out: { id, cx, cz, sections }    sections are Uint16Arrays (or null for all-air), transferred, not copied
import { createGenerator } from './generator.js';

let generator = null, seed = null;

self.onmessage = ({ data }) => {
  if (data.seed !== undefined && data.seed !== seed) { seed = data.seed; generator = createGenerator(seed); }
  if (data.cx === undefined) return;
  const sections = generator.generateChunk(data.cx, data.cz);
  self.postMessage({ id: data.id, seed, cx: data.cx, cz: data.cz, sections }, sections.filter(Boolean).map(s => s.buffer));
};
