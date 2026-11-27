# Playing: walk forward, jump, break the block pointed at (held), place one back (pressed), fly up and land.
from common import *
import sys
with sync_playwright() as p:
    b, page, errors = open_game(p, 960, 540)
    start_world(page, 12345)
    page.wait_for_timeout(1500)
    # drive the game with a scripted input state each frame
    page.evaluate("""()=>{ window.hold={}; game.input.update=()=>{ const s=game.input.emptyState(); Object.assign(s, hold); game.input.state=s; hold.usePressed=false; hold.attackPressed=false; hold.fly=false; window.maxY=Math.max(window.maxY||0, game.player.y); }; }""")
    r = {}
    r['start'] = page.evaluate("()=>[game.player.x, game.player.y, game.player.z, game.player.onGround]")
    page.evaluate("()=>{ hold.moveZ=-1; }"); page.wait_for_timeout(1500)
    r['walked'] = page.evaluate("()=>{ hold.moveZ=0; return +game.player.walked.toFixed(2); }")
    page.evaluate("()=>{ window.maxY=0; hold.jump=true; }"); page.wait_for_timeout(1200)
    r['jumpPeak'] = page.evaluate("()=>{ hold.jump=false; return +window.maxY.toFixed(2); }")
    page.wait_for_timeout(1500)
    # look down at the ground in front, break it, place it back
    page.evaluate("()=>{ game.player.pitch=-1.2; }"); page.wait_for_timeout(300)
    t = page.evaluate("()=>game.target && [game.target.x, game.target.y, game.target.z, game.target.id]")
    r['target'] = t
    page.evaluate("()=>{ hold.attack=true; }"); page.wait_for_timeout(2500)
    r['broken'] = page.evaluate(f"()=>{{ hold.attack=false; return game.world.getBlock({t[0]},{t[1]},{t[2]}); }}")
    page.wait_for_timeout(300)
    count = "()=>{ const p=game.player; let n=0; for(let x=-4;x<=4;x++) for(let y=-4;y<=4;y++) for(let z=-4;z<=4;z++) if(game.world.getBlock(Math.floor(p.x)+x,Math.floor(p.y)+y,Math.floor(p.z)+z)===game.hotbar[2]) n++; return n; }"
    before = page.evaluate(count)
    page.evaluate("()=>{ game.selected=2; hold.use=true; hold.usePressed=true; }"); page.wait_for_timeout(300)
    page.evaluate("()=>{ hold.use=false; }")
    r['placedStone'] = page.evaluate(count) == before + 1
    page.evaluate("()=>{ hold.fly=true; hold.jump=true; }"); page.wait_for_timeout(800)
    r['flyUp'] = page.evaluate("()=>{ hold.jump=false; return [game.player.flying, +game.player.y.toFixed(1)]; }")
    print(json.dumps(r)); print('errors', errors[:3])
    stoneId = page.evaluate("()=>3")
    b.close()
ok = r['walked'] > 1 and r['jumpPeak'] > r['start'][1] + 0.5 and r['target'] and r['broken'] == 0 and r['placedStone'] and r['flyUp'][0] and r['flyUp'][1] > r['start'][1] + 2 and not errors
print('PLAY OK' if ok else 'PLAY FAILED'); sys.exit(0 if ok else 1)
