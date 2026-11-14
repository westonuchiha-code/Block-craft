from playwright.sync_api import sync_playwright
import sys
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hd'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; player.pitch=-0.3; }")
    pg.wait_for_timeout(2000); fs=[]
    for nm in ['IRON_PICK','IRON_SWORD','STONE_SWORD','IRON_AXE']:
        pg.evaluate("(n)=>{ const id=globalThis[n]!==undefined?globalThis[n]:eval(n); inv[id]=1; HOTBAR[0]=id; sel=0; updateHotbar(); }", nm)
        pg.wait_for_timeout(700); fn='/tmp/held_%s.png'%nm; pg.screenshot(path=fn, clip={'x':650,'y':260,'width':300,'height':300}); fs.append(fn)
    S=Image.new('RGB',(300*len(fs),300))
    for i,f in enumerate(fs): S.paste(Image.open(f),(i*300,0))
    S.save(sys.argv[1] if len(sys.argv)>1 else '/tmp/held.png'); print(errs)
