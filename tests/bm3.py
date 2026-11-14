from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    pg.evaluate("health=20; paused=false; testPadGo({k:6})"); pg.wait_for_timeout(4000)
    # find the flattest snowy spot with trees: search around and stand 14 up looking down
    pg.evaluate("""()=>{ player.y+=3; player.vy=0; player.yaw=2.4; player.pitch=-0.1; fallPeakY=player.y; safeT=5; }""")
    pg.wait_for_timeout(300)
    pg.evaluate("safeT=5; player.vy=0"); pg.wait_for_timeout(9000)
    pg.screenshot(path='/tmp/bm_snow2.png',clip={'x':0,'y':60,'width':390,'height':330}); print(errs); b.close()
