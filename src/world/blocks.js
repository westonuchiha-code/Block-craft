// Every kind of block, in one list. A block's id (its number in the world data) is given out in the order blocks are defined here,
// so ids change when blocks are added or moved. That is allowed: anything stored outside the running game (saved worlds, tests)
// must refer to blocks by their key ('stone', 'water'), never by number. Saves keep a key list to translate their ids.
//
// Fields of a definition:
//   name       what the player sees
//   render     'cube'     a full opaque block
//              'cutout'   a full block whose texture has holes (leaves): see-through, drawn without blending
//              'glass'    a full see-through block; faces between two of them are not drawn
//              'liquid'   water and lava: drawn on their own, see-through, slightly lowered top
//              'cross'    two crossed flat pictures (grass tufts, flowers)
//              'none'     not drawn (air)
//   textures   tile names: { all } or { top, bottom, side }
//   tint       'grass' or 'foliage': the texture is coloured by the biome where the block stands
//   solid      you collide with it (default: true for cube, cutout and glass)
//   hardness   seconds to break by hand (Infinity: never)
//   light      light it gives off, 0..15

export const BLOCKS = [];
/** Block ids by key, e.g. BLOCK.grass. */
export const BLOCK = {};

function define(key, def) {
  const render = def.render ?? 'cube';
  const block = {
    id: BLOCKS.length,
    key,
    name: def.name,
    render,
    textures: normaliseTextures(def.textures),
    tint: def.tint ?? null,
    solid: def.solid ?? (render === 'cube' || render === 'cutout' || render === 'glass'),
    opaque: render === 'cube',
    hardness: def.hardness ?? 1,
    light: def.light ?? 0,
    drops: def.drops ?? key,
  };
  BLOCKS.push(block);
  BLOCK[key] = block.id;
  return block;
}

function normaliseTextures(t) {
  if (!t) return null;
  if (t.all) return { top: t.all, bottom: t.all, side: t.all };
  return { top: t.top ?? t.side, bottom: t.bottom ?? t.top ?? t.side, side: t.side };
}

// ---- the world's own materials ----
define('air',        { name: 'Air', render: 'none', solid: false, hardness: 0 });
define('bedrock',    { name: 'Bedrock', textures: { all: 'bedrock' }, hardness: Infinity });
define('stone',      { name: 'Stone', textures: { all: 'stone' }, hardness: 3, drops: 'cobblestone' });
define('cobblestone',{ name: 'Cobblestone', textures: { all: 'cobblestone' }, hardness: 3.5 });
define('andesite',   { name: 'Andesite', textures: { all: 'andesite' }, hardness: 3 });
define('granite',    { name: 'Granite', textures: { all: 'granite' }, hardness: 3 });
define('diorite',    { name: 'Diorite', textures: { all: 'diorite' }, hardness: 3 });
define('tuff',       { name: 'Tuff', textures: { all: 'tuff' }, hardness: 2.5 });
define('mossy_rock', { name: 'Mossy Rock', textures: { all: 'mossy_rock' }, hardness: 3 });
define('dirt',       { name: 'Dirt', textures: { all: 'dirt' }, hardness: 1 });
define('grass',      { name: 'Grass Block', textures: { top: 'grass_top', side: 'grass_side', bottom: 'dirt' }, tint: 'grass', hardness: 1.2, drops: 'dirt' });
define('sand',       { name: 'Sand', textures: { all: 'sand' }, hardness: 1 });
define('sandstone',  { name: 'Sandstone', textures: { top: 'sandstone_top', side: 'sandstone_side' }, hardness: 2.5 });
define('red_sand',   { name: 'Red Sand', textures: { all: 'red_sand' }, hardness: 1 });
define('red_sandstone', { name: 'Red Sandstone', textures: { top: 'red_sandstone_top', side: 'red_sandstone_side' }, hardness: 2.5 });
define('terracotta', { name: 'Terracotta', textures: { all: 'terracotta' }, hardness: 3 });
define('light_terracotta', { name: 'Pale Terracotta', textures: { all: 'light_terracotta' }, hardness: 3 });
define('red_terracotta',   { name: 'Red Terracotta', textures: { all: 'red_terracotta' }, hardness: 3 });
define('gravel',     { name: 'Gravel', textures: { all: 'gravel' }, hardness: 1.2 });
define('snow',       { name: 'Snow', textures: { all: 'snow' }, hardness: 0.8 });
define('ice',        { name: 'Ice', render: 'glass', textures: { all: 'ice' }, hardness: 1.2 });
define('cactus',     { name: 'Cactus', textures: { top: 'cactus_top', side: 'cactus_side' }, hardness: 1 });
define('water',      { name: 'Water', render: 'liquid', textures: { all: 'water' }, solid: false, hardness: Infinity });
define('lava',       { name: 'Lava', render: 'liquid', textures: { all: 'lava' }, solid: false, hardness: Infinity, light: 15 });
define('obsidian',   { name: 'Obsidian', textures: { all: 'obsidian' }, hardness: 25 });

// ---- ores ----
define('coal_ore',       { name: 'Coal Ore', textures: { all: 'coal_ore' }, hardness: 4 });
define('iron_ore',       { name: 'Iron Ore', textures: { all: 'iron_ore' }, hardness: 5 });
define('mithril_ore',    { name: 'Mithril Ore', textures: { all: 'mithril_ore' }, hardness: 7 });
define('adamantite_ore', { name: 'Adamantite Ore', textures: { all: 'adamantite_ore' }, hardness: 9 });

// ---- trees: five woods, each with its log, planks and leaves ----
export const WOODS = ['maple', 'oak', 'birch', 'spruce', 'palm'];
for (const wood of WOODS) {
  const title = wood[0].toUpperCase() + wood.slice(1);
  define(`${wood}_log`,    { name: `${title} Log`, textures: { top: `${wood}_log_top`, side: `${wood}_log_side` }, hardness: 2.5 });
  define(`${wood}_planks`, { name: `${title} Planks`, textures: { all: `${wood}_planks` }, hardness: 2 });
  define(`${wood}_leaves`, { name: `${title} Leaves`, render: 'cutout', textures: { all: `${wood}_leaves` },
                             tint: wood === 'maple' ? 'foliage' : null, hardness: 0.3 });
}

// ---- small plants ----
define('tall_grass', { name: 'Tall Grass', render: 'cross', textures: { all: 'tall_grass' }, tint: 'grass', solid: false, hardness: 0 });

// ---- made things ----
define('glass',     { name: 'Glass', render: 'glass', textures: { all: 'glass' }, hardness: 0.5 });
define('glowstone', { name: 'Glowstone', textures: { all: 'glowstone' }, hardness: 0.5, light: 15 });

// ---- quick lookups by id, for the hot loops (meshing, collision, light) ----
export const IS_SOLID = Uint8Array.from(BLOCKS, b => (b.solid ? 1 : 0));
export const IS_OPAQUE = Uint8Array.from(BLOCKS, b => (b.opaque ? 1 : 0));
export const LIGHT_OF = Uint8Array.from(BLOCKS, b => b.light);

/** The id of a wood's block, e.g. woodBlock('oak', 'log'). */
export const woodBlock = (wood, part) => BLOCK[`${wood}_${part}`];
