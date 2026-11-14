from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','fw3'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    pg.evaluate("()=>{ inv[SAND]=8; inv[COAL_ITEM]=2; inv[WIN0]=3; openCraft(3,'smelt'); craftSel=0; renderCraft(); }")
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/fw3.png'); print(errs); b.close()
