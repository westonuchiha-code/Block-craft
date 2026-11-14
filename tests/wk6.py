from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2500)
    print(pg.inner_text('#mcBtn'))
    pg.click('#mcBtn'); print(pg.inner_text('#mcBtn'), pg.evaluate("WK.on"))
    pg.fill('#newName','a'); pg.fill('#newSeed','111'); pg.click('#newBtn'); pg.wait_for_timeout(2000)
    pg.evaluate("openMenu()"); pg.click('#mcBtn'); pg.wait_for_timeout(2500); print(pg.inner_text('#mcBtn'))
    pg.click('#resumeBtn'); pg.wait_for_timeout(2000)
    print(pg.evaluate("({on:WK.on, frames:WK.frames, err:WK.err||null})"), errs)
    pg.screenshot(path='/tmp/wk6.png',clip={'x':0,'y':60,'width':390,'height':330})
    b.close()
