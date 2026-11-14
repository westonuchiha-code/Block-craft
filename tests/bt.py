from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','bt'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ mobs.length=0; player.z+=UNDER_Z; lastPCX=null; updateChunks();
      // stand on the cavern floor
      let y=UNDER_LAVA+2, x=Math.floor(player.x), z=Math.floor(player.z), found=null;
      for(let r=0;r<30&&!found;r++) for(let dx=-r;dx<=r&&!found;dx++) for(let dz=-r;dz<=r;dz++){ const g=ogreGround(x+dx+0.5,z+dz+0.5,24,3,false); if(g!==null&&g>UNDER_LAVA+2){ found=[x+dx,g,z+dz]; break; } }
      player.x=found[0]+0.5; player.y=found[1]; player.z=found[2]+0.5; safeT=3; fallPeakY=player.y; lastPCX=null; updateChunks();
      trySpawnBeetles(true); trySpawnBeetles(true); window.M=mobs.slice();
      return {n:mobs.length, kinds:mobs.map(m=>m.kind), d:mobs.map(m=>Math.hypot(m.x-player.x,m.z-player.z).toFixed(0)), hp:health}; }"""), errs)
    for t in range(7):
        pg.wait_for_timeout(1500)
        print(pg.evaluate("[M.map(m=>Math.hypot(m.x-player.x,m.z-player.z).toFixed(1)+(m.hostile?'!':'')).join(' '), health, dead]"))
        if t==3:
            pg.evaluate("()=>{ const m=M[0]; player.yaw=Math.atan2(m.x-player.x, -(m.z-player.z)); player.pitch=0; }"); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/bt1.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("()=>{ const m=M[0]; m.iframe=0; mobHit(m,30); return [m.dead, WK.on, WK.err||null]; }"), errs)
    b.close()
