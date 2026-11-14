from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hd'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; player.pitch=-0.1; }")
    pg.wait_for_timeout(2000); fs=[]
    for nm,sw in (('IRON_PICK',None),('IRON_SWORD',None),('MITH_SWORD',None),('IRON_SWORD',0.35),('IRON_SWORD',0.6)):
        pg.evaluate("([n,s])=>{ const id=eval(n); inv[id]=1; HOTBAR[0]=id; sel=0; updateHotbar(); if(s!==null){ swingT=1e-9; } }", [nm,sw])
        if sw is not None:
            pg.evaluate("(s)=>{ window.__sw=setInterval(()=>{ swingT=s; },2); }", sw)
        pg.wait_for_timeout(600); fn='/tmp/h3_%d.png'%len(fs); pg.screenshot(path=fn, clip={'x':560,'y':180,'width':360,'height':380}); fs.append(fn)
        pg.evaluate("()=>{ clearInterval(window.__sw); swingT=0; }")
    S=Image.new('RGB',(360*len(fs),380))
    for i,f in enumerate(fs): S.paste(Image.open(f),(i*360,0))
    S.save('/tmp/held3.png'); print(errs)
