// Biomes: a temperature map and a moisture map pick one per area. The shape of the land is shared; each biome brings its own
// ground, colours and trees.

export const BIOMES = [
  { key: 'autumn',    name: 'Autumn Woods',   grass: [150, 145, 75],  foliage: [200, 95, 35] },
  { key: 'forest',    name: 'Green Forest',   grass: [92, 140, 58],   foliage: [64, 128, 44] },
  { key: 'highlands', name: 'Pine Highlands', grass: [76, 112, 74],   foliage: [38, 86, 56] },
  { key: 'frost',     name: 'Frostlands',     grass: [170, 188, 176], foliage: [44, 92, 70] },
  { key: 'desert',    name: 'Sunscorch',      grass: [186, 170, 96],  foliage: [88, 150, 52] },
];

export const BIOME = Object.fromEntries(BIOMES.map((b, i) => [b.key, i]));

// Which trees grow where: [wood, shape, weight]. Shapes are built in trees.js.
export const TREES_BY_BIOME = {
  [BIOME.autumn]:    [['maple', 'round', 55], ['birch', 'round', 30], ['oak', 'great', 15]],
  [BIOME.forest]:    [['oak', 'round', 50], ['birch', 'round', 30], ['spruce', 'conifer', 20]],
  [BIOME.highlands]: [['spruce', 'conifer', 65], ['birch', 'round', 20], ['oak', 'great', 15]],
  [BIOME.frost]:     [['spruce', 'conifer', 85], ['birch', 'round', 15]],
  [BIOME.desert]:    [['palm', 'palm', 100]],
};
