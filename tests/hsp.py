from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1024,'height':576}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','sp'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; player.pitch=-0.1; inv[IRON_SWORD]=1; HOTBAR[0]=IRON_SWORD; sel=0; updateHotbar(); spell='fire'; spellCharges=5; swordSpell=true; }")
    pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/hsp1.png')
    pg.evaluate("()=>{ spell='bolt'; }"); pg.wait_for_timeout(500); pg.screenshot(path='/tmp/hsp2.png')
    S=Image.new('RGB',(1024,288)); S.paste(Image.open('/tmp/hsp1.png').resize((512,288)),(0,0)); S.paste(Image.open('/tmp/hsp2.png').resize((512,288)),(512,0)); S.save('/tmp/hsp.png'); print(errs)
