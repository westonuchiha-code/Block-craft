from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for (w,h,nm) in ((1100,560,'land'),(390,844,'port')):
        pg=b.new_context(viewport={'width':w,'height':h}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
        pg.fill('#newName','hud'+nm); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
        pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
        pg.evaluate("()=>{ inv[IRON_SWORD]=1; HOTBAR[0]=IRON_SWORD; inv[STEAK]=4; HOTBAR[1]=STEAK; sel=1; updateHotbar(); sel=0; updateHotbar(); food=13; health=17; }")
        pg.wait_for_timeout(500); r=pg.evaluate("()=>{ const R=id=>document.getElementById(id).getBoundingClientRect(); const hb=R('hotbar'), it=R('itemName'), ft=R('food'), hr=R('hearts'); return {hotbarBottom:hb.bottom, itemNameBottom:it.bottom, hotbarTop:hb.top, foodTop:ft.top, heartsTop:hr.top, hbLeft:hb.left, hbRight:hb.right, heartsRight:hr.right, foodLeft:ft.left}; }")
        print(nm, r, errs); pg.screenshot(path='/tmp/hud_%s.png'%nm, clip={'x':0,'y':h-130,'width':w,'height':130})
    b.close()
