from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1024,'height':576}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hs'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; player.pitch=-0.1; inv[IRON_SWORD]=1; HOTBAR[0]=IRON_SWORD; sel=0; updateHotbar(); }")
    pg.wait_for_timeout(1500); ims=[]
    for ph in (0,0.15,0.3,0.5,0.7,0.9):
        if ph: pg.evaluate("(p)=>{ window.__sw=setInterval(()=>{ swingT=1-p; },1); }", ph)
        pg.wait_for_timeout(400); pg.screenshot(path='/tmp/hs.png'); pg.evaluate("()=>{ clearInterval(window.__sw); swingT=0; }")
        im=Image.open('/tmp/hs.png').resize((512,288)); ImageDraw.Draw(im).text((8,30),'swing %.2f'%ph,fill=(255,255,0)); ims.append(im)
    S=Image.new('RGB',(1024,288*3))
    for i,im in enumerate(ims): S.paste(im,((i%2)*512,(i//2)*288))
    S.save('/tmp/hsw.png'); print(errs)
