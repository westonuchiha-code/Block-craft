from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    pg.evaluate("""()=>{ health=20; const o=testPlan().rooms[1]; player.x=o.x0+10; player.z=TEST_Z+o.side*5.5; player.y=TEST_FY+1; lastPCX=null; updateChunks(); }""")
    pg.wait_for_timeout(2500)
    def dist(): return pg.evaluate("mobs.filter(m=>m.kind==='cat').map(m=>Math.hypot(m.x-player.x,m.z-player.z)).reduce((a,b)=>a+b,0)/Math.max(1,mobs.filter(m=>m.kind==='cat').length)")
    # move to far end of room then hold catnip
    pg.evaluate("""()=>{ const o=testPlan().rooms[1]; player.z=TEST_Z+o.side*20.5; lastPCX=null; }""")
    pg.wait_for_timeout(500)
    d0=dist()
    pg.evaluate("inv[CATNIP]=5; HOTBAR[sel]=CATNIP;")
    pg.wait_for_timeout(9000)
    print(pg.evaluate("mobs.filter(m=>m.kind==='cat').map(m=>[m.state,m.x.toFixed(1),(m.z-TEST_Z).toFixed(1),m.curiousT&&m.curiousT.toFixed(1)])")); print(pg.evaluate('[player.x,player.z-TEST_Z, HOTBAR[sel]===CATNIP]'))
    d1=dist(); print('cat avg dist before/after holding catnip', round(d0,1), round(d1,1))
    # ogre loot
    pg.evaluate("""()=>{ mobs.length=0; itemDrops.length=0; const m=newOgre(Math.floor(player.x)+3,Math.floor(player.y),Math.floor(player.z),'ogre'); mobs.push(m); ogreHit(m,999); const m2=newOgre(Math.floor(player.x)-3,Math.floor(player.y),Math.floor(player.z),'mino'); mobs.push(m2); ogreHit(m2,999); }""")
    print(pg.evaluate("(()=>{ const c={}; for(const d of itemDrops) c[NAMES[d.id]]=(c[NAMES[d.id]]||0)+1; return c; })()"), errs); b.close()
