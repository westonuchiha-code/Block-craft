from playwright.sync_api import sync_playwright
from PIL import Image
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    cases=[('phone sideways',844,390,True),('phone upright',390,844,True),('desktop',1100,560,False)]; ims=[]
    for name,w,h,touch in cases:
        kw={'viewport':{'width':w,'height':h}}
        if touch: kw.update(has_touch=True,is_mobile=True,device_scale_factor=2)
        ctx=b.new_context(**kw); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
        pg.fill('#newName','or'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
        pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; player.pitch=-0.1; inv[IRON_SWORD]=1; HOTBAR[0]=IRON_SWORD; sel=0; updateHotbar(); }")
        pg.wait_for_timeout(2500)
        r=pg.evaluate("()=>({RW,RH, canvas:[canvas.width,canvas.height], controller: !!document.getElementById('touch'), view:[document.getElementById('view').clientWidth,document.getElementById('view').clientHeight], workers:WK.on})")
        print(name, json.dumps(r), errs)
        pg.screenshot(path='/tmp/or.png'); ims.append(Image.open('/tmp/or.png').resize((w//2, h//2))); ctx.close()
    W=sum(i.width for i in ims)+20; H=max(i.height for i in ims); S=Image.new('RGB',(W,H),(60,0,60)); x=0
    for i in ims: S.paste(i,(x,0)); x+=i.width+10
    S.save('/tmp/orient.png')
