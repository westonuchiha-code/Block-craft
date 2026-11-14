from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    names=pg.evaluate("testPlan().rooms.map(o=>o.name)")
    for i,n in enumerate(names):
        pg.evaluate("""i=>{ const o=testPlan().rooms[i]; if(o.side){ player.x=o.x0+9.5+0.5; player.z=TEST_Z+o.side*5.5; player.y=TEST_FY+1; player.yaw=o.side<0?0:Math.PI; }
           else { player.x=o.x0+3; player.z=TEST_Z+0.5; player.y=TEST_FY+1; player.yaw=Math.PI/2; } player.pitch=0.05; lastPCX=null; updateChunks(); }""",i)
        pg.evaluate("health=20"); pg.wait_for_timeout(1800); pg.evaluate("health=20; mobs.length=0"); pg.wait_for_timeout(400)
        info=pg.evaluate("[document.getElementById('testLabel').textContent, mobs.filter(m=>isTestZ(m.z)).map(m=>m.kind+Math.round(m.hp)).join(',')]")
        print(n,info)
        pg.screenshot(path='/tmp/room%d.png'%i,clip={'x':0,'y':60,'width':390,'height':330})
    print(errs); b.close()
