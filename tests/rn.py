from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','rn'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    pg.screenshot(path='/tmp/rn0.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("rainNext=0.1")
    pg.wait_for_timeout(6000)
    print(pg.evaluate("[rainOn, rainK.toFixed(2), rainShow.toFixed(2), rainSheltered()]"))
    pg.screenshot(path='/tmp/rn1.png',clip={'x':0,'y':60,'width':390,'height':330})
    # under a roof: put a block above head
    pg.evaluate("setB(Math.floor(player.x),Math.floor(player.y)+3,Math.floor(player.z),STONE)"); pg.wait_for_timeout(2500)
    print(pg.evaluate("[rainShow.toFixed(2), rainSheltered()]"))
    pg.evaluate("setB(Math.floor(player.x),Math.floor(player.y)+3,Math.floor(player.z),AIR); rainLeft=0.1"); pg.wait_for_timeout(8000)
    print(pg.evaluate("[rainOn, rainK.toFixed(2)]"))
    pg.click('#menuBtn') if pg.query_selector('#menuBtn') else pg.evaluate("openMenu()")
    pg.evaluate("document.getElementById('rainBtn').click()"); print(pg.evaluate("[rainMode, document.getElementById('rainBtn').textContent]"), errs); b.close()
