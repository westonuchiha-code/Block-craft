# Blockcraft: the rebuild

The game is being rebuilt from the ground up for a gaming PC on a big screen (target: an RTX 3070-class card at 4K, played with a
controller from the sofa). The first version is kept, playable, in `legacy/blockcraft_v1.html` until this one has caught up.

## Playing it

`game/blockcraft.html` is the built game (the file launchers and the desktop app open): one file, open it in Chrome or Edge (or point a launcher at it). It is rebuilt from
`src/` with:

    npm install        (once)
    npm run build      writes game/blockcraft.html
    npm run watch      rebuilds whenever a file in src/ changes

## How the code is laid out

Every file does one job and starts with a comment saying what that job is.

| Folder | What lives there |
|---|---|
| `main.js` | Start-up and the main loop. Only wires the parts together. |
| `settings.js` | The player's settings, their ranges, defaults and labels. |
| `core/` | `math.js` small maths helpers; `noise.js` hashing and noise (the world is built from these). |
| `world/` | `constants.js` world size, sea level; `blocks.js` **every block, defined once**; `biomes.js`; `terrain.js` the shape of the land; `trees.js`; `generator.js` the natural world, block by block and chunk by chunk; `chunk.js` storage; `world.js` the loaded world, block reads and writes; `worker.js` builds chunks on other CPU cores. |
| `render/` | `tiles.js` the 16 x 16 block art; `textures.js` puts it on the GPU; `mesher.js` turns sections into triangles with smooth lighting; `materials.js` the block shaders; `sky.js` sky, sun, moon, stars, day and night; `renderer.js` keeps every section's mesh up to date and draws the frame (Three.js). |
| `player/` | `player.js` the body: movement, collision, swimming, flying; `raycast.js` what the player points at. |
| `input/` | `input.js` keyboard, mouse and controller, as gameplay actions and as menu navigation. |
| `ui/` | `menu.js` controller-driven menus; `screens.js` title, pause, settings, loading; `hud.js` crosshair, hotbar, notices; `icons.js` block pictures; `style.css` all styling (sized from the screen height, so it is big on a TV). |

## Rules this code keeps

- **One place per fact.** A block's name, textures, hardness and behaviour are in its one line in `blocks.js`; a setting's range
  and label in `settings.js`. Nothing is a bare number scattered through the code.
- **The world is a pure function of the seed.** Generation never depends on what has been loaded, so workers and the main thread
  agree, and only the player's changes need saving.
- **Nothing runs on the frame's time that could run elsewhere.** Chunks are built on worker threads; meshing is spread across
  frames within a time budget, nearest first.
- **Physics runs in fixed steps** (1/120 s), so the game plays the same at any frame rate.
- **Controller first.** Every screen is a `Menu`: up/down to move, left/right to change, A to select, B to go back. No cursor.
- **Both for a TV and a desk.** All interface sizes are in `em`, and the root size follows the window height and the player's
  "Menu and HUD size" setting.

## Tests

`tests2/run.sh` builds the game and runs the browser tests (headless Chrome with a software GPU):
`smoke.py` (title, world builds, player stands in it), `play.py` (walk, jump, break, place, fly),
`ui4k.py` (the menus on a 4K screen driven by a simulated controller). `views.py` and `water.py` take pictures to look at.

## What is in so far (phase 1: the foundation)

Terrain, biomes, caves, ores, rock strata, five kinds of tree, tall grass, cactus, lakes and rivers, all as in the first version;
the block art; a mesh renderer at native resolution with anti-aliasing, smooth lighting and corner shading, biome colours blended
at the edges, fog, sky, sun, moon and stars, day and night; walking, sprinting, sneaking, swimming, flying; breaking and placing
blocks; the title, pause, settings and loading screens; the hotbar.

Not yet: saving, block light (torches, lava), the inventory, crafting, creatures, villages and everything built on them. These are
ported one system at a time, rewritten in this style, in the order set out in `docs/blockcraft_game_plan.txt`.
