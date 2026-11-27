// The fixed shape of every world.

/** Width and depth of a chunk, in blocks. A chunk is one column of the world, CHUNK_SIZE x WORLD_HEIGHT x CHUNK_SIZE. */
export const CHUNK_SIZE = 16;

/** Height of a section: chunks are stored and drawn in 16-high slices, so empty sky and buried rock cost nothing to draw. */
export const SECTION_HEIGHT = 16;

/** How tall the world is. Bedrock is at y = 0. */
export const WORLD_HEIGHT = 256;
export const SECTIONS_PER_CHUNK = WORLD_HEIGHT / SECTION_HEIGHT;

/** Every empty block at or below this height is water (the sea, lakes and rivers). */
export const SEA_LEVEL = 56;

/**
 * The land is shaped by curves written for a sea level of 16, then lifted by this much, leaving about 60 blocks of rock
 * under the land for caves and ores.
 */
export const TERRAIN_LIFT = 40;
export const BASE_SEA_LEVEL = SEA_LEVEL - TERRAIN_LIFT;

/** No trees grow on ground higher than this, so mountain tops stay bare. */
export const TREE_LINE = 84;
/** Snow caps start around here (the edge wobbles). */
export const SNOW_LINE = 90;
/** Empty cave space at or below this height fills with lava. */
export const LAVA_LEVEL = 7;

/** The length of a whole day and night, in real seconds: 30 minutes of daylight and 10 of night, as in the first version. */
export const DAY_LENGTH_SECONDS = 2400;
