from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hm'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.evaluate("""()=>{ beastSpawnT=1e9; mobs.length=0; let X=null; for(let x=-300;x<300&&!X;x+=5) for(let z=-300;z<300;z+=5){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+2&&!nearVillage(x,z)){ let ok=true; for(let a=-6;a<=6;a+=3) for(let q=-6;q<=6;q+=3) if(Math.abs(colInfo(x+a,z+q).h-c.h)>0) ok=false; if(ok){ X=[x,z,c.h]; break; } } }
      const [x,z,h]=X; for(let i=-8;i<=8;i++) for(let j=-8;j<=8;j++) for(let k=h+1;k<h+8;k++) setB(x+i,k,z+j,AIR); player.x=x+0.5; player.z=z+0.5; player.y=h+1; player.yaw=0.6; player.pitch=0.35; camMode=2; tod=0.3; }""")
    pg.wait_for_timeout(2500)
    shots=[]
    for m,nm in ((0,'leather'),(1,'chitin'),(2,'iron'),(3,'adamantite'),(4,'mithril')):
        pg.evaluate("(m)=>{ mobs.length=0; for(let k=0;k<4;k++){ const id=AR(m,k); inv[id]=1; equipArmor(id); } }", m)
        pg.wait_for_timeout(1200); fn='/tmp/helm_%s.png'%nm; pg.screenshot(path=fn, clip={'x':430,'y':120,'width':240,'height':260}); shots.append(fn)
    pg.evaluate("()=>{ camMode=1; player.pitch=0.4; }"); pg.wait_for_timeout(1200); pg.screenshot(path='/tmp/helm_back.png', clip={'x':430,'y':120,'width':240,'height':260}); shots.append('/tmp/helm_back.png')
    pg.evaluate("()=>{ unequipArmor(0); camMode=2; player.pitch=0.35; }"); pg.wait_for_timeout(1200); pg.screenshot(path='/tmp/helm_none.png', clip={'x':430,'y':120,'width':240,'height':260}); shots.append('/tmp/helm_none.png')
    print(pg.evaluate("()=>({wk:WK.on, pts:armorPoints()})"), errs)
    from PIL import Image
    S=Image.new('RGB',(240*len(shots),260))
    for i,f in enumerate(shots): S.paste(Image.open(f),(i*240,0))
    S.save('/tmp/helms.png')
