// Biomes. The world is divided into large regions (about 700 blocks across, with wavy borders), each one biome, chosen by a
// slow climate map so that neighbouring regions are related (snow fields border pine highlands, not deserts).
// Each biome brings its own colours, its own trees, and its own shape of land:
//   rolling    how much the ground rises and falls
//   mountains  how much of the mountain ridges it raises (the continent decides where ridges can be; the biome how tall)
//   lift       blocks added to (or taken from) the ground everywhere
//   dunes      sand dunes
//   mesas      high desert ground turns into layered red rock instead of sand

export const BIOMES = [
  { key: 'autumn',    name: 'Autumn Woods',   grass: [150, 145, 75],  foliage: [200, 95, 35],
    terrain: { rolling: 1.15, mountains: 0.3, lift: 2, dunes: 0, mesas: false } },
  { key: 'forest',    name: 'Green Forest',   grass: [92, 140, 58],   foliage: [64, 128, 44],
    terrain: { rolling: 0.8, mountains: 0.2, lift: 0, dunes: 0, mesas: false } },
  { key: 'highlands', name: 'Pine Highlands', grass: [76, 112, 74],   foliage: [38, 86, 56],
    terrain: { rolling: 1.3, mountains: 1.45, lift: 6, dunes: 0, mesas: false } },
  { key: 'frost',     name: 'Frostlands',     grass: [170, 188, 176], foliage: [44, 92, 70],
    terrain: { rolling: 0.7, mountains: 0.8, lift: 2, dunes: 0, mesas: false } },
  { key: 'desert',    name: 'Sunscorch',      grass: [186, 170, 96],  foliage: [88, 150, 52],
    terrain: { rolling: 0.45, mountains: 0.35, lift: 0, dunes: 1, mesas: true } },
];

export const BIOME = Object.fromEntries(BIOMES.map((b, i) => [b.key, i]));

/** Pick the biome for a region from the climate at its centre: temperature t and moisture m, both 0..1. */
export function biomeForClimate(t, m) {
  if (t < 0.3) return BIOME.frost;
  if (t < 0.44) return BIOME.highlands;
  if (t > 0.6 && m < 0.5) return BIOME.desert;
  return m > 0.52 ? BIOME.forest : BIOME.autumn;
}

// Which trees grow where: [wood, shape, weight]. Shapes are built in trees.js.
// (Desert palms grow only by water, which generator.js checks.)
export const TREES_BY_BIOME = {
  [BIOME.autumn]:    [['maple', 'round', 55], ['birch', 'round', 30], ['oak', 'great', 15]],
  [BIOME.forest]:    [['oak', 'round', 50], ['birch', 'round', 30], ['spruce', 'conifer', 20]],
  [BIOME.highlands]: [['spruce', 'conifer', 65], ['birch', 'round', 20], ['oak', 'great', 15]],
  [BIOME.frost]:     [['spruce', 'conifer', 85], ['birch', 'round', 15]],
  [BIOME.desert]:    [['palm', 'palm', 100]],
};
