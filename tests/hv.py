from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
V=[(90,25),(-90,25),(90,-25),(-90,-25)]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1024,'height':576}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hv'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; player.pitch=-0.1; }")
    pg.wait_for_timeout(1500); ims=[]
    for y,z in V:
        for n in ('IRON_SWORD','IRON_PICK'):
            pg.evaluate("([y,z,n])=>{ self.__hmcY=y; self.__hmcZ=z; const id=eval(n); inv[id]=1; HOTBAR[0]=id; sel=0; updateHotbar(); }",[y,z,n]); pg.wait_for_timeout(500)
            pg.screenshot(path='/tmp/hv.png'); im=Image.open('/tmp/hv.png').resize((512,288)); ImageDraw.Draw(im).text((8,30),'Y%d Z%d %s'%(y,z,n),fill=(255,255,0)); ims.append(im)
    S=Image.new('RGB',(1024,288*4))
    for i,im in enumerate(ims): S.paste(im,((i%2)*512,(i//2)*288))
    S.save('/tmp/hv_all.png'); print(errs)
