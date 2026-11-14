from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    pg.evaluate("""()=>{ const o=testPlan().rooms[2]; player.x=o.x0+10; player.z=TEST_Z+o.side*5.5; player.y=TEST_FY+1; player.yaw=0; lastPCX=null; updateChunks(); }""")
    for i in range(6):
        pg.wait_for_timeout(500)
        print(pg.evaluate("[testRoomName, mobs.length, mobs.map(m=>m.kind+':'+m.x.toFixed(0)+','+(m.z-TEST_Z).toFixed(0)+','+m.y).slice(0,3).join(' '), testPlan().rooms[2].mobPos]"))
    print(errs); b.close()
