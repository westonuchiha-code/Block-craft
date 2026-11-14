from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','o'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000)
    print(pg.evaluate("""()=>{ saveWorld(); openMenu(); const id=currentWorld; const k=wkey(id,'world'); const m=JSON.parse(localStorage.getItem(k)); const had=m.gen; delete m.gen; m.player=null; localStorage.setItem(k,JSON.stringify(m)); loadWorld(id); window.__m=JSON.parse(localStorage.getItem(k)).gen;
      return [window.__m, had, worldGen, !!villageAt(0,0), Math.round(player.x), Math.round(player.z)]; }"""), errs)
    b.close()
