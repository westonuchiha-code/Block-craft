from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    pg.evaluate("""()=>{ health=20; paused=false; const o=testPlan().rooms[6]; window.O=o; player.x=o.x0+4.5; player.z=TEST_Z+o.side*(4+9)+0.5; player.y=TEST_FY+1; player.yaw=Math.PI; player.pitch=-0.35; lastPCX=null; updateChunks(); }""")
    pg.wait_for_timeout(2500)
    pg.screenshot(path='/tmp/fu2.png',clip={'x':0,'y':60,'width':390,'height':330}); print(errs); b.close()
