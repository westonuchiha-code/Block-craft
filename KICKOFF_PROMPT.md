# Paste this into the new session (attach the zip with it)

---

I'm handing you my game project, **Blockcraft**: a voxel sandbox RPG that fuses Minecraft and Daggerfall.
It's one self-contained HTML file (`game/blockcraft.html`). The attached kit has the game, a handoff brief, my task
log and notes, the test suite, and reference images.

Before doing anything:
1. Unzip the kit and read `HANDOFF.md` completely. It has my rules for how to work with me, the design rules I've
   set, a map of the code, traps that already cost time, and what's open.
2. Set up the tests per `tests/README.md` (Python + Playwright + headless Chrome) and run `bash tests/suite.sh`
   to confirm a clean baseline (all 34 should pass).
3. Then tell me in a few sentences what state the project is in and what you think the next step is. Don't
   change code yet.

The most important rules:
- Only tell me something works if you tested it in the browser, and show me proof (full-frame screenshots, not crops).
- This is a **PC game**. I develop on my phone (Galaxy S21 Ultra, landscape, with a gamepad), but nothing
  phone-specific goes in unless I ask for it as temporary playtesting help. No portrait mode, no touch controls.
- Never make the visuals or gameplay worse to fix something else.
- After each task: send me the updated game file and a short summary, and add to the task log.
- Anything that draws on screen has to work in **both** renderers (GPU and the CPU fallback); `tests/gpu.py` checks that.

---
