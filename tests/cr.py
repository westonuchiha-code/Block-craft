from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','cr'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={};
      const C=cryptNear(0,0,900); out.count=C.length; out.first=C.slice(0,4).map(P=>P.name+' @'+P.ex+','+P.ez+' h'+P.h);
      const P=C[0]; window.__P=P; beastSpawnT=1e9; tod=0.3; health=1000;
      // stand outside the door, facing in (+z)
      player.x=P.ex+0.5; player.z=P.ez-6.5; player.y=P.h+1; player.yaw=0; await sleep(2500);
      let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; const v=camVectors().f; if(v[2]>bd){bd=v[2];ba=a;} } player.yaw=ba; player.pitch=-0.05;
      out.door=[P.h+1,P.h+2].map(y=>NAMES[getB(P.ex,y,P.ez-3)]);
      return out; }""")
    print(json.dumps(r))
    pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/cr_out.png')
    # walk in and down: hold W
    pg.keyboard.down('KeyW'); 
    for i in range(30):
        pg.wait_for_timeout(500)
        st=pg.evaluate("()=>[+player.x.toFixed(1),+player.y.toFixed(1),+player.z.toFixed(1)]"); print(st, end=" ")
    pg.keyboard.up('KeyW')
    r2=pg.evaluate("()=>{ const P=window.__P; return {pos:[+player.x.toFixed(1),+player.y.toFixed(1),+player.z.toFixed(1)], F:P.F, zc:P.zc, reached: player.y<=P.F+0.6 && player.z>P.zc, undead:mobs.filter(m=>m.crypt).map(m=>m.kind)} }")
    print(json.dumps(r2))
    pg.screenshot(path='/tmp/cr_in.png')
    print(errs[:3]); b.close()
