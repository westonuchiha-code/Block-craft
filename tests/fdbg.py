from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','fd'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.evaluate(open('/tmp/tour.py').read().split('PRE = r"""')[1].split('"""')[0])
    r=pg.evaluate("""async ()=>{ T.freeze(); rainMode='off'; rainOn=false; health=1000; const [x0,z0,h]=T.flat(9); player.x=x0+0.5; player.z=z0-12; player.y=h+1; await T.sleep(2000); T.clear(x0,z0,h,12);
      for(let i=-2;i<=2;i++) for(let j=-2;j<=2;j++) for(let k=1;k<=4;k++){ if(Math.abs(i)===2||Math.abs(j)===2||k===4) setB(x0+i,h+k,z0+j,PLANKS); }
      inv[TINDERBOX]=1; HOTBAR[0]=TINDERBOX; sel=0; player.x=x0-3.5; player.z=z0+0.5; player.y=h+1; player.yaw=Math.PI/2; player.pitch=0; await T.sleep(100);
      const f=camVectors().f; placeBlock(); player.x=x0-9.5; player.z=z0-7.5; player.y=h+2.5; const where=[...fires.keys()]; const out={f:f.map(v=>+v.toFixed(2)), where, rain:[rainOn, typeof raining!=='undefined'?raining:null], biome:biomeAt(x0,z0)};
      const s=[]; for(let i=0;i<6;i++){ await T.sleep(1000); s.push(fires.size); } out.s=s; return out; }""")
    print(json.dumps(r)); print(errs)
