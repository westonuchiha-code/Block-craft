from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','arm2'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.evaluate("""()=>{ let X=null; for(let x=-300;x<300&&!X;x+=2)for(let z=-300;z<300;z+=2){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+2){ let ok=true; for(let a=-6;a<=6&&ok;a+=3)for(let b2=-6;b2<=6;b2+=3){ const q=colInfo(x+a,z+b2); if(Math.abs(q.h-c.h)>1){ ok=false; break; } } if(ok){ X=[x,z,c.h]; break; } } }
      const [x,z,h]=X; for(let i=-6;i<=6;i++) for(let j=-6;j<=6;j++){ for(let k=h+1;k<=h+6;k++) setB(x+i,k,z+j,AIR); setB(x+i,h,z+j,GRASS); }
      player.x=x+0.5; player.z=z+0.5; player.y=h+1; player.pitch=0.1; tod=0.3;
      for(const id of [AR(2,0),AR(2,1),AR(2,2),AR(2,3)]){ inv[id]=1; equipArmor(id); } camMode=2; }""")
    pg.wait_for_timeout(1800); pg.screenshot(path='/tmp/arm_iron.png')
    pg.evaluate("()=>{ armor=[null,null,null,null]; for(const id of [AR(0,0),AR(0,1),AR(0,2),AR(0,3)]){ inv[id]=1; equipArmor(id); } inv[DYE0+1]=4; for(let k=0;k<4;k++) dyeArmor(k,1); }")
    pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/arm_dyed.png')
    print(errs[:3]); b.close()
