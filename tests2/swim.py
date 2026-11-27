# Swimming out of water: a pool whose bank stands a full block above the water. Hold forward and jump: you must climb out.
from common import *
import sys
with sync_playwright() as p:
    b, page, errors = open_game(p, 960, 540)
    start_world(page, 12345)
    page.wait_for_timeout(1000)
    page.evaluate("""()=>{ window.hold={}; game.input.update=()=>{ const s=game.input.emptyState(); Object.assign(s, hold); game.input.state=s; }; }""")
    setup = page.evaluate("""()=>{ const w=game.world, p=game.player, x0=Math.floor(p.x), z0=Math.floor(p.z), y0=Math.floor(p.y)+6;
      for(let x=x0-3;x<=x0+3;x++) for(let z=z0-6;z<=z0+3;z++){ w.setBlock(x,y0-1,z, 2); for(let y=y0;y<=y0+6;y++) w.setBlock(x,y,z,0); }   // a stone floor in the air, cleared above
      for(let x=x0-3;x<=x0+3;x++) for(let z=z0-6;z<=z0+3;z++) for(let y=y0;y<=y0+2;y++){ const edge = x===x0-3||x===x0+3||z===z0+3||z===z0-6; w.setBlock(x,y,z, edge?2:(y<=y0+1? BLOCK_WATER :0)); }
      for(let x=x0-3;x<=x0+3;x++) for(let z=z0-9;z<=z0-6;z++) w.setBlock(x,y0+2,z,2);    // the bank, its top one block above the water's surface
      p.x=x0+0.5; p.z=z0+0.5; p.y=y0; p.yaw=0; p.pitch=0; p.flying=false; p.vx=p.vy=p.vz=0; return [x0,y0,z0]; }""".replace('BLOCK_WATER', '17'))      # 17 = water, 2 = stone (ids from src/world/blocks.js)
    print('pool at', setup, 'in water:', page.evaluate("()=>game.player.inWater"))
    page.evaluate(f"()=>{{ hold.moveZ=-1; hold.jump=true; window.onBank=false; const f=game.input.update; game.input.update=()=>{{ f(); const p=game.player; if(p.z<{setup[2]-6}+0.2){{ hold.moveZ=0; hold.jump=false; }} if(p.onGround && p.y>={setup[1]+3}-0.01 && p.z<{setup[2]-6}+0.3) window.onBank=true; }}; }}")
    for _ in range(16):
        page.wait_for_timeout(500)
        st = page.evaluate("()=>[+game.player.y.toFixed(2), +game.player.z.toFixed(2), game.player.inWater, game.player.onGround]")
        if page.evaluate("()=>window.onBank"): break
    print('ended at y, z, inWater, onGround:', st, errors[:2])
    ok = page.evaluate("()=>window.onBank") and st[0] >= setup[1] + 3
    b.close(); print('SWIM OK' if ok else 'SWIM FAILED'); sys.exit(0 if ok else 1)
