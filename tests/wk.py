from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append('C:'+m.text) if m.type=='error' else None)
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2500)
    print(pg.evaluate("({on:WK.on, ready:WK.ready, n:WK.n, fail:WK.fail, err:WK.err||null, hc:navigator.hardwareConcurrency})"))
    pg.fill('#newName','wk'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    print(pg.evaluate("({on:WK.on, fail:WK.fail, err:WK.err||null, frames:WK.frames||0, busy:WK.busy})"), errs)
    pg.screenshot(path='/tmp/wk1.png',clip={'x':0,'y':60,'width':390,'height':330})
    b.close()
