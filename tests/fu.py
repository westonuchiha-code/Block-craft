from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    pg.evaluate("""()=>{ health=20; paused=false; const o=testPlan().rooms[6]; player.x=o.x0+10; player.z=TEST_Z+o.side*(4+12); player.y=TEST_FY+1; player.yaw=Math.PI; player.pitch=0.1; lastPCX=null; updateChunks(); }""")
    pg.wait_for_timeout(2500)
    pg.screenshot(path='/tmp/fu1.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("""()=>{ const r={}; r.names=[tableId(1),chairId(2,3),benchId(0,1),BARREL,CRATE].map(i=>NAMES[i]);
      r.drops=[chairId(2,3),benchId(0,1),tableId(2)].map(i=>DROP[i]);
      r.rec=RECIPES.filter(x=>/table|chair|bench|barrel|crate/.test(x.name)).length;
      // place test: give items, aim at floor
      inv[chairId(1,0)]=2; inv[tableId(1,0)]=1; inv[BARREL]=1; r.ok=!!iconCanvas(chairId(1,0)) && !!iconCanvas(tableId(0)) && !!iconCanvas(benchId(0,0));
      const o=testPlan().rooms[6]; r.coll=collidesBlockAt(tableId(0),Math.floor(player.x),TEST_FY+1,Math.floor(player.z)); return r; }"""))
    print(errs); b.close()
