// World statistics, for judging generation changes by numbers: run `node tools/worldstats.mjs [seed]`.
//   biomes in view  how many different biomes can be seen within 192 blocks (the default view distance) of a spot
//   sand up high    how often the ground more than 14 blocks above the sea is sand
//   caves           how much of the rock is cave, and how tall the tunnels are (a run of air one block high cannot be walked in)
//   walkable land   between neighbouring land columns, how often the step is 0-1 blocks (walk or jump), 2-3 (a wall you must dig or
//                   build round), or 4+ (a cliff); in all land, and in mountain biomes only
//   floating        rock or earth only 1-2 blocks thick with open air under it near the surface (hanging bits)
import { createGenerator } from '../src/world/generator.js';
import { BLOCK } from '../src/world/blocks.js';
import { SEA_LEVEL } from '../src/world/constants.js';
import { makeRng } from '../src/core/noise.js';

const seed = +(process.argv[2] ?? 12345), g = createGenerator(seed), rnd = makeRng(seed);

// biomes in view
const counts = [0, 0, 0, 0, 0, 0];
for (let k = 0; k < 150; k++) {
  const x0 = Math.floor((rnd() - 0.5) * 20000), z0 = Math.floor((rnd() - 0.5) * 20000), seen = new Set();
  for (let a = 0; a < 64; a++) for (const r of [0, 48, 96, 144, 192]) seen.add(g.biomeAt(Math.round(x0 + Math.cos(a / 10.2) * r), Math.round(z0 + Math.sin(a / 10.2) * r)));
  counts[seen.size]++;
}
console.log('biomes in view (1..5 kinds):', counts.slice(1).join(' / '), ' of 150 spots');

// sand up high, and the share of each biome
let high = 0, highSand = 0; const share = [0, 0, 0, 0, 0];
for (let k = 0; k < 20000; k++) {
  const x = Math.floor((rnd() - 0.5) * 20000), z = Math.floor((rnd() - 0.5) * 20000), c = g.column(x, z);
  share[c.biome]++;
  if (c.h > SEA_LEVEL + 14) { high++; if (c.top === BLOCK.sand) highSand++; }
}
console.log('sand on ground over 14 above the sea:', (100 * highSand / high).toFixed(2) + '%', ' biome shares %:', share.map(n => (n / 200).toFixed(0)).join(' / '));

// caves
let rock = 0, cave = 0; const runs = [0, 0, 0, 0, 0];
for (let k = 0; k < 300; k++) {
  const x = Math.floor((rnd() - 0.5) * 6000), z = Math.floor((rnd() - 0.5) * 6000), h = g.column(x, z).h;
  let run = 0;
  for (let y = 8; y < h - 4; y++) {
    const air = g.blockAt(x, y, z) === BLOCK.air; rock++;
    if (air) { cave++; run++; } else if (run) { runs[Math.min(4, run)]++; run = 0; }
  }
}
const total = runs.reduce((a, b) => a + b, 0);
console.log('cave share of rock:', (100 * cave / rock).toFixed(2) + '%', ' tunnel heights 1/2/3/4+ blocks:', runs.slice(1).map(n => (100 * n / total).toFixed(0) + '%').join(' / '));

// walkable land
const steps = { all: [0, 0, 0], mountains: [0, 0, 0] };
for (let k = 0; k < 40000; k++) {
  const x = Math.floor((rnd() - 0.5) * 20000), z = Math.floor((rnd() - 0.5) * 20000), c = g.column(x, z);
  if (c.h <= SEA_LEVEL + 1) continue;
  const n = g.column(x + 1, z);
  if (n.h <= SEA_LEVEL + 1) continue;
  const d = Math.abs(c.h - n.h), bucket = d <= 1 ? 0 : d <= 3 ? 1 : 2;
  steps.all[bucket]++;
  if (c.biome === 2) steps.mountains[bucket]++;
}
const pct = a => { const t = a[0] + a[1] + a[2]; return a.map(v => (100 * v / t).toFixed(1) + '%').join(' / '); };
console.log('steps between land columns, 0-1 / 2-3 / 4+ blocks:  all land', pct(steps.all), '   highlands', pct(steps.mountains));

// floating: rock or earth only 1-2 blocks thick with open air under it, near the top of mountain-biome columns
let cols = 0, floating = 0;
for (let k = 0; k < 3000; k++) {
  const x = Math.floor((rnd() - 0.5) * 20000), z = Math.floor((rnd() - 0.5) * 20000), c = g.column(x, z);
  if (c.biome !== 2 || c.h <= SEA_LEVEL + 8) continue;
  cols++;
  for (let y = c.h - 12; y < c.h - 1; y++) {
    if (g.blockAt(x, y, z) !== BLOCK.air || g.blockAt(x, y + 1, z) === BLOCK.air) continue;
    let thick = 0;
    while (thick < 3 && g.blockAt(x, y + 1 + thick, z) !== BLOCK.air) thick++;
    if (thick <= 2) { floating++; break; }
  }
}
console.log('highland columns with thin (1-2 block) rock hanging over air:', (100 * floating / cols).toFixed(2) + '%');
