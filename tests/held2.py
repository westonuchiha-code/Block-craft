from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hd'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; player.pitch=-0.3; inv[IRON_SWORD]=1; HOTBAR[0]=IRON_SWORD; sel=0; updateHotbar(); }")
    pg.wait_for_timeout(2000); fs=[]
    for roll in [0.9,1.2,1.5,1.8]:
        pg.evaluate("(r)=>{ HELD_POSE[3].roll=r; }", roll); pg.wait_for_timeout(500)
        fn='/tmp/r_%s.png'%roll; pg.screenshot(path=fn, clip={'x':650,'y':200,'width':300,'height':360}); fs.append(fn)
    S=Image.new('RGB',(300*len(fs),360))
    for i,f in enumerate(fs): S.paste(Image.open(f),(i*300,0))
    S.save('/tmp/rolls.png'); print(errs, pg.evaluate("()=>JSON.stringify(toolSprite(IRON_SWORD).grip)+' '+JSON.stringify(toolSprite(IRON_PICK).grip)"))
