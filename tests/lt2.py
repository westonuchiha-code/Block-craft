from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','lt2'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const x=Math.floor(player.x)+3, z=Math.floor(player.z)+3, t=getTopP(x,z); setB(x,t,z,TILLED); window.S={x,y:t,z}; return [getB(x,t,z)===TILLED]; }"""))
    pg.evaluate("rainOn=true; rainLeftT=1; tillTimer=20")
    pg.wait_for_timeout(3500)
    print('wet while raining', pg.evaluate("getB(S.x,S.y,S.z)===TILLED_WET"), pg.evaluate("[typeof tillTimer]"))
    print(errs); b.close()
