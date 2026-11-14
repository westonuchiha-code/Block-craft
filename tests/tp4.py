from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','tp'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    pg.evaluate("()=>{ tod=0.25; mobs.length=0; trySpawnOgre=function(){}; inv[STONE_SWORD]=1; inv[CROSSBOW]=1; HOTBAR[0]=STONE_SWORD; HOTBAR[3]=CROSSBOW; sel=0; camMode=2; player.pitch=0; player.yaw=0.9; CAM_D=1; }")
    pg.wait_for_timeout(800); pg.screenshot(path='/tmp/tp_f1.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("()=>{ sel=3; }"); pg.wait_for_timeout(800); pg.screenshot(path='/tmp/tp_f2.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(errs); b.close()
