from playwright.sync_api import sync_playwright
from PIL import Image
import json, sys
cfg = json.loads(sys.argv[1]) if len(sys.argv)>1 else None
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    out=[]
    for (w,h) in ((1100,560),(844,390),(1280,800)):
        pg=b.new_context(viewport={'width':w,'height':h}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
        pg.fill('#newName','h4'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
        pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; player.pitch=-0.1; }")
        if cfg: pg.evaluate("(c)=>{ Object.assign(HELD_POSE[3], c); }", cfg)
        pg.wait_for_timeout(1500)
        for nm in ('IRON_PICK','IRON_SWORD','STONE_SWORD'):
            pg.evaluate("(n)=>{ const id=eval(n); inv[id]=1; HOTBAR[0]=id; sel=0; updateHotbar(); }", nm); pg.wait_for_timeout(600)
            fn='/tmp/h4_%d_%s.png'%(w,nm); pg.screenshot(path=fn); out.append((w,fn))
        print(w, errs)
    L=[Image.open(f) for w,f in out if w==1100]; P=[Image.open(f) for w,f in out if w==844]; T=[Image.open(f) for w,f in out if w==1280]
    S=Image.new('RGB',(550*3, 715),(0,0,0))
    for i,im in enumerate(L): S.paste(im.resize((550,280)),(i*550,0))
    for i,im in enumerate(P): S.paste(im.resize((422,195)),(i*432,290))
    for i,im in enumerate(T): S.paste(im.resize((336,210)),(i*346,495))
    S.save('/tmp/held4.png')
