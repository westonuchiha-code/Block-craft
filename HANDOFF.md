# Blockcraft — handoff brief

Read this whole file before touching the code. It is the working agreement with the developer, a map of the
code, the traps that have already cost time, and what is open. Latest build: `game/blockcraft.html`
(12,020 lines, one self-contained HTML file, no external assets or libraries).

---

## 1. What the game is

**Blockcraft** is a voxel sandbox RPG: **a clean fusion of Minecraft and Daggerfall**. It is *not* a Minecraft
clone with Daggerfall mods bolted on. At its core it plays and feels like Minecraft (you mine, place, craft, farm,
and travel far across a block world), and Minecraft's own mechanics are made to work the way Daggerfall's do
(skills that improve by use, classes, Daggerfall-style gold, villages with shops and quests, reputation, crypts,
a bestiary, a spellmaker, travel by wagon, danger that rises with distance).

- **Target platform: PC** (a Windows / Steam port is planned). It is **not a phone game**.
- The developer builds and playtests on a **Samsung Galaxy S21 Ultra**, held in **landscape with a gamepad**.
  Anything phone-specific may exist only as temporary playtesting scaffolding, and only if he asks for it.
  The on-screen touch controller was **removed** at his request. There is **no portrait mode**: the game is one
  landscape picture; a tall window simply letterboxes it like any PC game.

## 2. Working agreement (follow these exactly)

**How to work and report**
- **Claim only what you actually tested.** He has been told "fixed" when it wasn't, and it angers him (rightly).
  Test in a real browser (headless Chrome via Playwright, see §6) and show proof: a screenshot or a measured number.
- **Look at full frames, not crops,** when judging anything visual (a crop once hid a sword floating in mid-air).
- **Never degrade visuals or gameplay** to fix something else.
- **After each task:** deliver the updated game file plus a **short** summary (what changed, what was verified,
  anything you could not verify). Keep `docs/blockcraft_task_list.txt` updated (append a dated section).
- He writes by voice: long run-on messages, typos, sometimes swearing when frustrated. Read for intent; reply
  plainly and briefly. Ask only when a choice is genuinely his; otherwise make the sensible call and say so.
- When he gives a design rule, it is a rule from then on (list below).

**Design rules he has set**
- Everything is **boxy / voxel**, built from blocks or block-like boxes. No smooth shapes (e.g. the woolbloom must
  not be spherical).
- **Skills** are few and simple (9: weapons, unarmed, magic, athletics, stealth, mining, woodcut, farming, alchemy
  = cooking + alchemy). Skills **never lock** anything. Levelling a gathering skill gives **more materials per
  block** (extra drops / bonus materials), **never more speed**.
- **Mining** is only raised by a pickaxe on pickaxe-blocks **that the world placed** (not player-placed blocks).
- **Breaking:** nothing breaks in one hit **except dirt under a mithril shovel**. Stone takes **≥ 2 hits even with
  the best pickaxe**; bare hands / wood shovel take 4–5 hits minimum on dirt.
- **Tool tiers:** wood → stone → iron → adamantite → mithril (mithril is top; adamantite was slotted below it,
  flagged to him as an interpretation).
- **Classes:** few, Final-Fantasy-style (6 now), picked when a new world starts.
- **Money** is Daggerfall-style gold. **Death** drops a floating sack with a light beam where you died.
- The **pistol was removed** (too modern): it has no source and old saves have it stripped on load. The crossbow stays.
- **Held items** use Minecraft's single "handheld" transform for every tool (see §5, trap 1). Never hand-tune
  per-tool poses.

## 3. Current state (2026-11-14)

All 33 tests in the suite pass on this build. Recent work, newest first:
1. **GPU renderer (WebGL2), full resolution.** The 3D picture used to be drawn per-pixel on the CPU at 288×180 by
   default (that is why the resolution was low). It is now a fragment-shader port of the same renderer and draws
   at the window's real resolution (e.g. 1728×1080 on a 1080p screen, capped at 2560 wide). Verified pixel-for-pixel
   against the CPU renderer in 10 scenes (< 0.5 % of pixels differ by > 24 levels; only edge rounding). Overlays
   (crosshair, held tool, items, effects) are drawn sharp at the same size. Default: GPU when WebGL2 runs on real
   graphics hardware; the CPU renderer on software-only WebGL; the menu's **RENDERER** button overrides.
   WebGL context loss falls back to the CPU renderer instantly and resumes the GPU when restored.
2. **On-screen controller removed**; portrait-specific code removed; "Tap" wording removed; tests use a landscape
   desktop window.
3. **Held tools rebuilt on Minecraft's transform** (handheld.json first-person-right-hand + ItemInHandRenderer arm
   offset and swing), one transform for every tool; the old per-tool pose table was deleted.
4. Helmets drawn on the character; village standing tab lists villages by name; fire timer backlog bug fixed;
   **critical save bug fixed** (a duplicate `regionOf` broke chunk saving; renamed the homestead one
   `villageRegionOf`); speed work (memoised crypt/road lookups, packed placed-block map).

**Not yet verified (no real GPU in the build sandbox):** GPU speed on the S21 Ultra and on a PC. Ask him how it
runs before optimising.

## 4. Open items

- **GPU speed check** on his hardware; if needed add a resolution-scale setting (generic PC option).
- **Aspect:** DONE 2026-11-14. The logical picture is 16:9 (`RES_LEVELS`); adamantite confirmed below mithril.
- **`tp3`/`og2` worker differences:** RESOLVED 2026-11-14. Test artefact (class picker left open, loop frozen). Tests fixed; 0 differences.
- **Windows / Steam port** (planned, not started; e.g. Electron / Tauri / NW.js wrapper; saves currently live in
  `localStorage`).
- Pistol cleanup: DONE 2026-11-14 (only the id and the save-load strip remain).
- Held items in third person still use simple boxes (`heldBoxes`); first person was rebuilt (see trap 1).
- Possibly open, check the code first: villages in snow and desert biomes; the adamantite/mithril order
  (confirm with him); a further efficiency pass.
- `docs/blockcraft_task_list.txt` is a **chronological log**. Older `NEXT:` lines are mostly done; verify against
  the code before treating one as open. The newest sections are at the bottom.

## 5. Traps that already cost time (read before editing)

1. **Held items.** Everything in the first-person hand goes through one pipeline: `heldModel(id)` (quads) → `drawHeldPosed` →
   `drawHeldQuads`, with Minecraft's transforms. Tools and flat items: arm translate (0.56, −0.52, −0.72); swing per ItemInHandRenderer;
   display translate (1.13, 3.2, 1.13)/16, rotate Z 25° then Y **+90°** (Minecraft writes −90; our sprite x runs the other way), scale 0.68.
   Blocks and shaped blocks: rotate Y 45°, scale 0.4 (shaped ones are baked from `shapedHit`, centred, lifted 0.15). Empty hand:
   `heldMatrixArm` (renderPlayerArm). 70° hand camera. The resting picture is cached (`HELD_SPR`). Do not add per-item pose tuning.
2. **No phone layouts.** Headless Chrome without touch emulation stretched the old view over a tall screen, and
   "fixes" were built for a layout the user never sees. Test in landscape (e.g. 1100×560, 1920×1080).
3. **Duplicate function names silently override** (one script, function declarations hoist). That is how
   `regionOf` broke saving. Before adding a function, grep the name.
4. **GLSL reserved words:** `cast`, `half` (and others) are reserved; a shader that fails to compile leaves
   `GPU.err` set and the game on the CPU renderer. Check `GPU.err` after shader edits.
5. **Block textures hash with the world seed** (`texColor` uses `SEED`), so GPU textures are baked per seed,
   on demand (`gpuEnsure`). Some full-cube blocks have ids above 256 (andesite 1072, granite, diorite, tuff…), so
   never assume "blocks < 256".
6. **Texture array limit:** `MAX_ARRAY_TEXTURE_LAYERS` is often 2048; the GPU uses min(1024, limit). A world uses ~500.
7. **Chunk change tracking for the GPU:** every chunk edit must bump `c.gv` (done in `wkEdit`, `computeDerived`,
   `lightFinish`). A new code path that writes `c.data` / `c.light` / `c.top` without those hooks will show stale
   blocks on the GPU.
8. **Exactness quirks** reproduced on the GPU: `ccHash` multiplies through doubles (ported bit-for-bit as `jsMul`);
   sugarcane stalk indices use JS `Math.floor` results hard-coded; coordinates are relative to the camera's chunk
   (`uBase`) because the Underworld is at z = 480,000.
9. **Adding anything visible means porting it to both renderers.** A new block shape → `shapedHit` kinds in the
   shader + `gpuBake` tables; a new plant → `plantHit`; a new creature type → `gpuEntities` (box creature or
   jointed body). Then run `tests/gpu.py`.
10. **The CPU renderer is still the fallback** and the reference for exactness tests; keep it working.

## 6. Testing

- Needs Python 3 + Playwright and Chrome (tests use `/usr/bin/google-chrome` and the game at
  `/home/claude/blockcraft_prototype.html`; see `tests/README.md` to repoint them).
- **Suite:** `bash tests/suite.sh` (33 scripts, ~15 min). It is a regression/smoke harness: a test fails on a
  non-zero exit, a Python traceback or page errors; many also print values to read. `gpu.py` compares GPU vs CPU
  pictures in 6 scenes and fails on mismatch. `sv.py` checks save → reload keeps edits.
- **Conventions:** worlds are created via `#newName` / `#newSeed` / `#newBtn`, then the class picker must be
  answered:
  `pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")`.
  Freeze spawns when staging: `beastSpawnT=1e9; ogreSpawnT=1e9`. Builder buttons sit in collapsed `<details>`;
  click them with `document.getElementById('testBtn').click()`.
- **Headless WebGL is software (SwiftShader):** correct but ~1 frame/s at full HD. The game therefore defaults to the
  CPU renderer there; force the GPU with `localStorage.setItem('bc_gpu','1')`. For GPU screenshots, pause
  (`paused=true`), call `gpuRender(); renderOverlay();` once, wait, then screenshot with a long timeout; use
  `click(..., no_wait_after=True)` while the GPU runs.
- **Screenshot tour:** `tests/tour.py` walks every feature and writes ~66 shots plus a log of oddities.
- Useful one-offs: `gpucmp.py` (GPU vs CPU with side-by-side and diff images), `held4.py` (held tools in full
  frames), `beforeafter.py`, `ctxloss.py`.

## 7. Code map (`game/blockcraft.html`, approximate line numbers)

| Lines | Area |
|---|---|
| 1–470 | HTML/CSS: menu (WORLDS / ADVENTURE / SETTINGS / BUILDER TOOLS), HUD, menus (character sheet, map, talk, chest, crafting) |
| 470–985 | Character creator (skin painting `ccPaint`, 3D preview) |
| 985–1405 | World constants (`H`=120, `CS`=16, `NB`=2048, `SEA`=16), block/item tables, crops, flowers, woods, cooking, beast drops, metals (`METALS`, `MT`), armor (`ARMOR_MATS`, `AR`), shaped blocks (`SH_BOXES`, `SH_BASE`…) |
| 1406–2040 | Hashing (`h3`, `vnoise`), terrain, biomes, crypts (`cryptPlan`), trees, the Underworld (`UNDER_Z`=480000), test hall |
| 2295–2750 | Villages (`villageAt`, `VREG`=192, houses, plaza), roads/signposts/names (`roadChunk`, `villageName`) |
| 2751–3000 | Chunks (`chunkKey`=cx*131072+cz, `getChunk`, `setB`/`getB`, `computeDerived`, light), multi-core CPU rendering part 1 |
| 3000–3420 | Saves (`localStorage` `bc.w.<id>.<part>`, regions of 32 chunks, `saveWorld`/`scheduleSave`, `packPlaced`) |
| 3419–3732 | Player, collision, `cast()` (CPU DDA ray cast), camera, third person, player body (`bodyIntersect`) |
| 3732–5072 | CPU rendering: block textures (`texColor`), plants, flowers, sky, clouds, `render()` |
| 5073–5131 | Multi-core rendering part 2 (`wkStart`, workers run this same script with `IS_WORKER`) |
| 5132–6212 | **GPU renderer**: shader `GPU_FS` (stage 1 world, stage 2 shaped/plants, stage 3 creatures), `gpuInit`, `gpuBake`, `gpuEnsure`, `gpuSync`, `gpuModel`, `gpuEntities`, `gpuRender`, `depthAt`, `gpuSet` |
| 6213–6530 | Input, actions, breaking (`HITS`, `baseHits`, `TIER_POW`), leaf decay, saplings |
| 6531–7296 | NPCs, talking/trading (`SHOPS`, `PRICE`), quests + reputation, villagers, homesteads, map/wagons/inns |
| 7297–8503 | Rats, cats, woolbloom, wild beasts (`BEAST`, `updateBeast`), danger bands (`dangerAt`), bats/slaughterfish |
| 8504–9248 | Water flow, lava (cools to cobble/obsidian), grass spread, crops, tilled soil, falling trees, chests, beds |
| 9249–10106 | Crafting, crafting menu/grid, dropped items |
| 10107–10475 | Hand and held item (`drawHand`, tool sprites, `drawHeldMC`) |
| 10476–11250 | Magic (spellmaker, `castBook`), fire (`ignite`, `fireTick`), weather, cyclops/ogres, ranged weapons |
| 11250–11730 | Survival, classes (`CLASSES`), skills (`trainSkill`), character sheet, dying (`deathSacks`), eating, controller |
| 11733–12020 | `update()`, main loop (`frame`, `renderFrame`), menu wiring, export/import |

**Settings in `localStorage`:** `bc_gpu` (renderer override), `bc_res` (CPU sharpness), `bc_mc` (multi-core),
`bc_rain`, `bc_debug`. World saves: keys starting `bc.w.`.

## 8. GPU renderer in one paragraph

`renderFrame()` → `gpuRender()` when `GPU.on`. A full-screen triangle runs `GPU_FS`, which marches each pixel's ray
through a wrapping 256×120×256 `R16UI` 3D texture (block id | torch light << 11) holding the 16×16 chunks around
the camera, with the same empty-space skipping as `cast()` (per-column texture: roof height, biome, chunk maxY,
4×4 group height). Block textures are baked from `texColor` into a `RGBA16F` texture array on demand. Shaped
blocks use a box table plus per-kind colouring; plants are generated per cell in the shader; creatures arrive each
frame in a float texture (box creatures with boxes; jointed bodies with pose, models and skins uploaded once).
`renderOverlay()` then draws HUD-space overlays on the 2D canvas `#c` above, scaled to the GPU picture size.

## 9. Files in this kit

- `game/blockcraft.html`: the game (open in Chrome).
- `docs/`: task list (chronological log + newest status at the bottom), game plan, feature notes, playtest list,
  village ideas.
- `tests/`: `suite.sh` and every test/tool script (see `tests/README.md`).
- `images/`: renderer before/after at 1080p, a full 1080p GPU frame, and an overview of 66 feature screenshots
  (that overview was taken with the old CPU renderer, before the GPU work).
- `KICKOFF_PROMPT.md`: a message to start the new session with.
