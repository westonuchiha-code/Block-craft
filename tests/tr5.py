from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    pg.evaluate("""()=>{ const o=testPlan().rooms[9]; player.x=o.x0+9+1.0; player.z=TEST_Z+14.5; player.y=TEST_FY+1; lastPCX=null; updateChunks(); }""")
    pg.wait_for_timeout(3000)
    print('gate', pg.evaluate("[isUnder(player.z), isTestZ(player.z), Math.round(player.z-UNDER_Z), health]"))
    pg.wait_for_timeout(2500)
    print('after', pg.evaluate("[isUnder(player.z), isTestZ(player.z), Math.round(player.z-UNDER_Z)]"), errs)
    pg.evaluate("openMenu()"); print(pg.evaluate("getComputedStyle(document.getElementById('hallBtn')).display")); b.close()
