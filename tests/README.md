# Tests

Playwright scripts that drive the game in headless Chrome. Requirements: Python 3, `pip install playwright`,
and Chrome or Chromium.

## Point them at your copy

The scripts were written for one machine and contain these absolute paths:

- the game: `file:///home/claude/blockcraft_prototype.html`
- the browser: `executable_path='/usr/bin/google-chrome'`
- the runner `suite.sh` does `cd /tmp` and runs `python3 <name>.py` there
- a few scripts write images to `/tmp/...` or `/home/claude/screenshots`

Easiest: put the game at `/home/claude/blockcraft_prototype.html` and these scripts in `/tmp`. Or rewrite the
paths once, for example:

```bash
GAME="$PWD/../game/blockcraft.html"
sed -i "s#/home/claude/blockcraft_prototype.html#$GAME#g" *.py
sed -i "s#executable_path='/usr/bin/google-chrome'#executable_path='$(which chromium || which google-chrome)'#g" *.py
sed -i "s#cd /tmp#cd \"$PWD\"#" suite.sh
```

## Run

- `bash suite.sh`: the regression suite (35 scripts, about 20 minutes). Each line prints `name rc=<exit code>`
  and the script's last output line. A failure is a non-zero exit, `ERR` (traceback), or page errors in the
  printed list. Many scripts also print values meant to be read, not only asserted.
- `python3 gpu.py`: renders 6 scenes with the CPU renderer and the GPU renderer at the same size and fails if
  more than 0.5 % of pixels differ by more than 24 levels.
- `python3 gpucmp.py [scene,scene,...]`: the same comparison with images (`/tmp/gpucmp.png`: CPU | GPU | difference).
  Scenes: field, village, night, water, under, k_beasts, k_village, k_ogre, k_third, k_daedra.
- `python3 sv.py`: save, reload, check the edit survived.
- `python3 tour.py`: a screenshot tour of every feature (~66 images, about 9 minutes) plus a log of anything odd.

## Suite contents (by subject)

| Test | Covers |
|---|---|
| sv | saving and reloading keeps edits |
| gpu | GPU picture matches the CPU picture |
| guild | guilds: joining, perks, ranks from guild work, journal, save and reload |
| delve | delves: lifted world shape, every chamber and the master reachable on foot, master kill, chests, quest, map entry |
| sh2, sh4, sh5, sc, bb | stairs, slabs and other shaped blocks, recipes |
| fe | fences |
| door, dd | doors (walk-through, open/closed, double doors) |
| bed, hf | beds, respawn point, reach |
| cs | corner stairs with the multi-core renderer |
| fu | furniture |
| mg, mg2 | magic: magicka, casting, spell charges, saving |
| gun | ranged weapons: the crossbow (and that the pistol is gone) |
| old | old worlds (no villages) still load |
| og2, tp3, wk2, wk5, wk7 | multi-core CPU renderer: worker frames vs single-thread frames (fail on any difference or if workers make no frames) |
| mino | minotaur |
| ch | chests and their contents through save/load |
| uw2, us3, bt | the Underworld: portal, lamps, chests, render |
| tr2 | the test hall layout |
| lt, lt2, rn3 | rain, wetness, rain state through save/load |
| cl | cats and catnip |

Other useful scripts here (not in the suite): `hs` homesteads, `qs` quests, `ec` economy, `cr2` crypts, `fi` fire,
`bf` bats and fish, `uw` Underworld daedra, `tv` travel/map/wagons, `arm` armor, `f2` death sack, `yield` mining
yield, `hits` break hits, `held4` held tools in full frames, `ctxloss` WebGL context loss and recovery.

## Headless notes

- After creating a world, answer the class picker:
  `pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")`
- Headless WebGL is software (SwiftShader): correct but very slow, so the game uses its CPU renderer there unless
  `localStorage.setItem('bc_gpu','1')` forces the GPU. With the GPU forced, use small windows or render single frames
  (`paused=true; gpuRender(); renderOverlay();`), and click with `no_wait_after=True`.
- Use landscape windows (e.g. 1100×560 or 1920×1080). The game has no portrait or touch layout.
