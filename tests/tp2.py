from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','tp2'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    pg.evaluate("player.pitch=-0.1; camMode=2; keys.KeyW=true; keys.KeyD=true")
    clip={'x':100,'y':120,'width':190,'height':250}
    for i in range(2):
        pg.wait_for_timeout(260); pg.screenshot(path=f'/tmp/tp_w{i}.png',clip=clip)
    print(pg.evaluate("[limbAmp, bodyYaw, player.yaw]"), errs)
    b.close()
