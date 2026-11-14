from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.screenshot(path='/tmp/ui_title.png')
    pg.fill('#newName','ui'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.evaluate("()=>{ openMenu(); document.getElementById('mSettings').open=true; }"); pg.wait_for_timeout(400); pg.screenshot(path='/tmp/ui_menu.png')
    pg.evaluate("()=>{ closeMenu(); paused=false; inv[PLANKS]=10; inv[COBBLE]=20; openCraft(3); }"); pg.wait_for_timeout(400); pg.screenshot(path='/tmp/ui_craft.png')
    pg.evaluate("()=>{ closeCraft(); inv[COBBLE]=5; gold=42; die(); }"); pg.wait_for_timeout(400); pg.screenshot(path='/tmp/ui_death.png')
    print(errs[:3]); b.close()
