# Smoke test: the game opens to its title screen, a world builds, the player stands in it, and nothing throws.
from common import *
import sys
with sync_playwright() as p:
    b, page, errors = open_game(p)
    title = page.evaluate("()=>[document.querySelector('.screen.open .title')?.textContent, [...document.querySelectorAll('.screen.open .item')].map(e=>e.textContent)]")
    print('title screen:', title)
    page.screenshot(path='/tmp/claude-0/-home-user-Block-craft/49148b77-0114-5300-b5b9-1304725e4d54/scratchpad/v2_title.png')
    ok = start_world(page)
    page.wait_for_timeout(4000)
    st = page.evaluate("()=>({state:game.state, x:game.player.x, y:game.player.y, z:game.player.z, chunks:game.world.chunks.size, sections:game.renderer.sections.size, tris:game.renderer.stats.triangles, dirty:game.renderer.dirty.size, onGround:game.player.onGround})")
    print('in world:', ok, json.dumps(st))
    page.screenshot(path='/tmp/claude-0/-home-user-Block-craft/49148b77-0114-5300-b5b9-1304725e4d54/scratchpad/v2_world.png')
    print('errors:', errors[:5])
    b.close()
    sys.exit(0 if ok and not errors else 1)
