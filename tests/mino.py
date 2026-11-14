from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','mn'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const v=nearestVillage(2); window.V=v; const S=v.sewer; mobs.length=0; trySpawnOgre=function(){};
      const o={spots:S.spots.length}; trySpawnMino(true); o.surface=mobs.length;           // on the surface: must not spawn
      player.x=v.cx+9.5; player.z=v.cz+1.5; player.y=S.Fs+1; player.yaw=-Math.PI/2; player.pitch=0; lastPCX=null; updateChunks();
      let rare=0; for(let i=0;i<400;i++){ mobs.length=0; trySpawnMino(); if(mobs.length) rare++; } o.rate=rare/400;
      mobs.length=0; trySpawnMino(true); o.spawned=mobs.map(m=>[m.kind,(m.x-v.cx).toFixed(0),(m.z-v.cz).toFixed(0),m.hp]); window.m=mobs[0];
      return o; }"""), errs)
    for t in range(6):
        pg.wait_for_timeout(1500)
        print(pg.evaluate("m ? [(Math.hypot(m.x-player.x,m.z-player.z)).toFixed(1), m.hostile, health, dead, (m.x-V.cx).toFixed(1), (m.z-V.cz).toFixed(1)] : null"))
        if t==2: pg.screenshot(path='/tmp/mino1.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.screenshot(path='/tmp/mino2.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("[WK.on, WK.err||null]"), errs); b.close()
