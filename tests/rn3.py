from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','rn3'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    pg.evaluate("rainOn=true; rainLeftT=0.4; saveWorld()"); id=pg.evaluate("currentWorld")
    pg.evaluate("rainOn=false; rainLeftT=0; openMenu(); loadWorld(arguments[0])" if False else "0")
    pg.evaluate("i=>{ rainOn=false; rainLeftT=0; loadWorld(i); }",id); pg.wait_for_timeout(3000)
    print(pg.evaluate("[rainOn, rainLeftT]"), errs); b.close()
