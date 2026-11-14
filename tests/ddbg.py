from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','dd'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.evaluate(open('/tmp/tour.py').read().split('PRE = r"""')[1].split('"""')[0])
    r=pg.evaluate("""async ()=>{ T.freeze(); health=1000; let P=null; for(let x=0;x<400&&!P;x+=4){ const z=UNDER_Z+40, c=underCol(x,z); if(c.hf>UNDER_LAVA+3 && c.hc-c.hf>14){ let ok=true; for(let a=-6;a<=6;a+=3) if(Math.abs(underCol(x+a,z).hf-c.hf)>1) ok=false; if(ok) P=[x,z,c.hf]; } }
      const [x,z,hf]=P; player.x=x+0.5; player.z=z+0.5; player.y=hf+1; await T.sleep(2500); mobs.length=0;
      const d=newBeast('daedra',x+8,hf+1,z); d.angry=30; mobs.push(d); const tr=[];
      for(let i=0;i<20;i++){ await T.sleep(300); const ox=d.x,oy=d.y+1.7,oz=d.z,tx=player.x,ty=player.y+1.2,tz=player.z,dd=Math.hypot(tx-ox,ty-oy,tz-oz); let bl=null; for(let t=1;t<dd-1;t+=0.5){ const q=[Math.floor(ox+(tx-ox)*t/dd),Math.floor(oy+(ty-oy)*t/dd),Math.floor(oz+(tz-oz)*t/dd)]; const b=getB(...q); if(!PASS[b]&&!IS_LAVA[b]){ bl=NAMES[b]+'@'+q; break; } }
        tr.push([+d.x.toFixed(1),+d.y.toFixed(1),+(d.shotCd||0).toFixed(2),d.angry>0?1:0,bl, fx.filter(e=>e.enemy).length, 1000-health]); }
      return {P, py:player.y, tr}; }""")
    print(json.dumps(r)); print(errs)
