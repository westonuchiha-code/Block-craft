from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','fi'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={}; beastSpawnT=1e9; rainMode='off'; rainOn=false; health=1000;
      let X=null; for(let x=-400;x<400&&!X;x+=3)for(let z=-400;z<400;z+=3){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+2&&!nearVillage(x,z)){ let ok=true; for(let a=-8;a<=8&&ok;a+=2)for(let b2=-8;b2<=8;b2+=2){ const q=colInfo(x+a,z+b2); if(Math.abs(q.h-c.h)>0){ ok=false; break; } } if(ok){ X=[x,z,c.h]; break; } } }
      const [x0,z0,h]=X; player.x=x0+0.5; player.z=z0-10; player.y=h+1; await sleep(1500);
      for(let i=-9;i<=9;i++) for(let j=-9;j<=9;j++){ for(let k=h+1;k<=h+8;k++) setB(x0+i,k,z0+j,AIR); setB(x0+i,h,z0+j,GRASS); }
      // a plank hut with a stone hut next to it
      let wood=0; for(let i=-2;i<=2;i++) for(let j=-2;j<=2;j++) for(let k=1;k<=4;k++){ const wall=Math.abs(i)===2||Math.abs(j)===2||k===4; if(wall){ setB(x0+i,h+k,z0+j,PLANKS); wood++; } }
      for(let i=4;i<=7;i++) for(let j=-2;j<=2;j++) for(let k=1;k<=3;k++) setB(x0+i,h+k,z0+j,STONE);
      // light it with a tinderbox
      inv[TINDERBOX]=1; HOTBAR[0]=TINDERBOX; sel=0; player.x=x0-3.5; player.z=z0+0.5; player.y=h+1; let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; const v=camVectors().f; if(v[0]>bd){bd=v[0];ba=a;} } player.yaw=ba; player.pitch=0.0;
      placeBlock(); out.lit=fires.size; player.x=x0-10.5; player.z=z0-8;
      const series=[]; for(let s=0;s<16;s++){ await sleep(2000); let wl=0; for(let i=-2;i<=2;i++) for(let j=-2;j<=2;j++) for(let k=1;k<=4;k++) if(getB(x0+i,h+k,z0+j)===PLANKS) wl++; series.push(wl+'/'+fires.size); if(s===4) window.__shot=1; }
      out.series=series; out.wood=wood;
      let st=0; for(let i=4;i<=7;i++) for(let j=-2;j<=2;j++) for(let k=1;k<=3;k++) if(getB(x0+i,h+k,z0+j)===STONE) st++; out.stoneLeft=st;
      // fire in the open on bare grass dies quickly
      ignite(x0+3,h+1,z0-6); const f0=fires.size; await sleep(5000); out.bareGrassFire=[f0, getB(x0+3,h+1,z0-6)===FIRE];
      // water puts it out
      setB(x0-6,h+1,z0-6,PLANKS); ignite(x0-6,h+2,z0-6); setB(x0-5,h+2,z0-6,WATER); await sleep(1000); out.waterOut=getB(x0-6,h+2,z0-6)!==FIRE;
      // standing in it
      health=20; setB(Math.floor(player.x),Math.floor(player.y),Math.floor(player.z),FIRE); await sleep(1600); out.burnHurt=20-health;
      return out; }""")
    print(json.dumps(r)); print(errs[:3]); b.close()
