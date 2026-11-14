from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','wb3'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("""()=>{ let X=null; for(let x=-300;x<300&&!X;x+=2)for(let z=-300;z<300;z+=2){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+2){ let ok=true; for(let a=-12;a<=12&&ok;a+=4)for(let b2=-12;b2<=12;b2+=4){ const q=colInfo(x+a,z+b2); if(Math.abs(q.h-c.h)>1||q.top!==GRASS){ ok=false; break; } } if(ok){ X=[x,z,c.h]; break; } } }
      const [x,z,h]=X; for(let i=-3;i<=9;i++) for(let j=-5;j<=5;j++){ for(let k=h+1;k<=h+7;k++) setB(x+i,k,z+j,AIR); setB(x+i,h,z+j,GRASS); }
      mobs.length=0; const m=newWb(x+4,h+1,z); m.yaw=-Math.PI/2; m.idleT=999; m.state='idle'; m.shedT=999; mobs.push(m); const ct=newCat(x+4,h+1,z+2); mobs.push(ct); globalThis.__m=m; globalThis.__P=[x,z,h];
      wbSpawnT=9999; player.x=x-1.5; player.z=z+.5; player.y=h+1.4; let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.05){ player.yaw=a; const f=camVectors().f; if(f[0]>bd){bd=f[0];ba=a;} } player.yaw=ba; player.pitch=0.03; tod=0.27; }""")
    pg.wait_for_timeout(2000); pg.screenshot(path='/tmp/wb3a.png')
    pg.evaluate("()=>{ __m.shake=3; __m.seedsLeft=0; }"); pg.wait_for_timeout(500); pg.screenshot(path='/tmp/wb3b.png')
    print(errs); b.close()
