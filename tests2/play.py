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
    # a flat stone platform high in the sky, so the test does not depend on the ground at the spawn point
    page.evaluate("""()=>{ const w=game.world, p=game.player, x0=Math.floor(p.x), z0=Math.floor(p.z), y0=200;
      for(let x=x0-6;x<=x0+6;x++) for(let z=z0-12;z<=z0+6;z++){ w.setBlock(x,y0-1,z,BLOCK.stone); w.setBlock(x,y0-2,z,BLOCK.stone); }
      p.x=x0+0.5; p.z=z0+0.5; p.y=y0; p.vx=p.vy=p.vz=0; p.flying=false; p.yaw=0; p.pitch=0; }""")
    page.wait_for_timeout(1500)
    r['start'] = page.evaluate("()=>[game.player.x, game.player.y, game.player.z, game.player.onGround]")
    page.evaluate("()=>{ hold.moveZ=-1; }"); page.wait_for_timeout(1500)
    r['walked'] = page.evaluate("()=>{ hold.moveZ=0; return +game.player.walked.toFixed(2); }")
    page.evaluate("()=>{ window.maxY=0; hold.jump=true; }"); page.wait_for_timeout(1200)
    r['jumpPeak'] = page.evaluate("()=>{ hold.jump=false; return +window.maxY.toFixed(2); }")
    page.wait_for_timeout(1500)
    # look down at the ground in front, break it, place it back
    # (back to one fixed spot, so breaking and placing do not depend on exactly where the walk ended)
    page.evaluate("()=>{ const p=game.player; p.x=Math.floor(p.x)+0.5; p.z=Math.floor(p.z)+0.5; p.vx=p.vy=p.vz=0; p.yaw=0; p.pitch=-1.2; }")
    for _ in range(20):
        page.wait_for_timeout(250)
        if page.evaluate("()=>!!game.target"): break
    t = page.evaluate("()=>game.target && [game.target.x, game.target.y, game.target.z, game.target.id]")
    r['target'] = t
    page.evaluate("()=>{ hold.attack=true; }")
    for _ in range(20):                                     # (frames are slow in this software renderer: wait for the block, not a fixed time)
        page.wait_for_timeout(500)
        if page.evaluate(f"()=>game.world.getBlock({t[0]},{t[1]},{t[2]})") == 0: break
    r['broken'] = page.evaluate(f"()=>{{ hold.attack=false; return game.world.getBlock({t[0]},{t[1]},{t[2]}); }}")
    page.wait_for_timeout(300)
    count = "()=>{ const p=game.player; let n=0; for(let x=-4;x<=4;x++) for(let y=-4;y<=4;y++) for(let z=-4;z<=4;z++) if(game.world.getBlock(Math.floor(p.x)+x,Math.floor(p.y)+y,Math.floor(p.z)+z)===game.hotbar[2]) n++; return n; }"
    before = page.evaluate(count)
    page.evaluate("()=>{ game.selected=2; hold.use=true; hold.usePressed=true; }")
    for _ in range(20):                                     # (wait for the block, not a fixed time: frames are slow here)
        page.wait_for_timeout(250)
        if page.evaluate(count) > before: break
    page.evaluate("()=>{ hold.use=false; }")
    after = page.evaluate(count); print("stone near the player before, after placing:", before, after, page.evaluate("()=>{ const t=game.target, x=t.x+t.nx, y=t.y+t.ny, z=t.z+t.nz; return [x,y,z, game.world.getBlock(x,y,z), game.player.overlaps(x,y,z), game.player.y, game.player.box()]; }"))
    r["placedStone"] = after > before
    page.evaluate("()=>{ hold.fly=true; hold.jump=true; }")
    for _ in range(40):                                     # (wait until risen, not a fixed time: frames are slow here)
        page.wait_for_timeout(250)
        if page.evaluate("()=>game.player.y") > r['start'][1] + 2.5: break
    r['flyUp'] = page.evaluate("()=>{ hold.jump=false; return [game.player.flying, +game.player.y.toFixed(1)]; }")
    print(json.dumps(r)); print('errors', errors[:3])
    stoneId = page.evaluate("()=>3")
    b.close()
ok = r['walked'] > 3 and r['jumpPeak'] > r['start'][1] + 0.5 and r['target'] and r['broken'] == 0 and r['placedStone'] and r['flyUp'][0] and r['flyUp'][1] > r['start'][1] + 2 and not errors
print('PLAY OK' if ok else 'PLAY FAILED'); sys.exit(0 if ok else 1)
