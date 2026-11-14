from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','h5'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; player.pitch=-0.1; inv[IRON_SWORD]=1; HOTBAR[0]=IRON_SWORD; sel=0; updateHotbar(); }")
    pg.wait_for_timeout(2000); fs=[]
    for s in (None, 0.75, 0.5, 0.25):
        if s is not None: pg.evaluate("(s)=>{ window.__sw=setInterval(()=>{ swingT=s; },2); }", s)
        pg.wait_for_timeout(500); fn='/tmp/h5_%d.png'%len(fs); pg.screenshot(path=fn, clip={'x':550,'y':160,'width':550,'height':400}); fs.append(fn)
        pg.evaluate("()=>{ clearInterval(window.__sw); swingT=0; }")
    S=Image.new('RGB',(550*2,800))
    for i,f in enumerate(fs): S.paste(Image.open(f),((i%2)*550,(i//2)*400))
    S.save('/tmp/held5.png'); print(errs)
