from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','bf'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={}; beastSpawnT=1e9; health=1000;
      // a lake
      let L=null; for(let x=-200;x<200&&!L;x+=3)for(let z=-200;z<200;z+=3){ const c=colInfo(x,z); if(c.h<SEA-3&&!c.open){ let ok=true; for(const [a,b2] of [[2,0],[-2,0],[0,2],[0,-2]]) if(colInfo(x+a,z+b2).h>=SEA-2) ok=false; if(ok && colInfo(x+8,z).h>SEA+1 && colInfo(x+14,z).h>SEA+1){ L=[x,z,c.h]; break; } } }
      out.lake=L; const [lx,lz,lh]=L;
      player.x=lx+8.5; player.z=lz+0.5; player.y=colInfo(lx+8,lz).h+1; await sleep(2000);
      const f=newBeast('fish',lx,lh+1,lz); mobs.push(f); await sleep(2500); out.fishCalmOnShore=f.angry<=0 || !bodyInWater;
      player.x=lx+2.5; player.y=lh+1; player.z=lz+0.5; await sleep(3000); out.fishAngry=[bodyInWater, f.angry>0, Math.round(Math.hypot(f.x-player.x,f.z-player.z))];
      const h0=health; await sleep(3000); out.fishBit=h0-health;
      // a fish on land
      player.x=lx+8.5; player.y=colInfo(lx+8,lz).h+1; const fx=lx+14, fz=lz; const g=newBeast('fish',fx,colInfo(fx,fz).h+1,fz); g.angry=0; mobs.push(g); await sleep(7500); out.landFishDead=g.dead||!mobs.includes(g);
      // a bat
      f.dead=true; let bx=lx+40; while(colInfo(bx,lz).h<=SEA+2) bx+=5; player.x=bx+0.5; player.z=lz+0.5; player.y=colInfo(bx,lz).h+1; await sleep(1500);
      const bt=newBeast('bat',Math.floor(player.x)+8,Math.floor(player.y)+4,Math.floor(player.z)); mobs.push(bt); bt.angry=20;
      const d0=Math.hypot(bt.x-player.x,bt.z-player.z); const h1=health; out.trace=[]; for(let i=0;i<8;i++){ await sleep(500); out.trace.push([+(bt.x-player.x).toFixed(1),+(bt.y-player.y).toFixed(1),+(bt.z-player.z).toFixed(1),bt.angry>0?1:0]); } out.bat=[Math.round(d0), +Math.hypot(bt.x-player.x,bt.z-player.z).toFixed(1), h1-health, +bt.y.toFixed(1)];
      // spawning
      mobs.length=0; tod=0.75; ratNight=true; for(let i=0;i<20;i++) trySpawnFlyers({}); out.spawned=mobs.map(m=>m.kind).join(',');
      out.cook=COOK_RECIPES.some(r=>r.out[0]===COOKED_FISH);
      return out; }""")
    print(json.dumps(r)); print(errs[:3]); b.close()
