from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','bst'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500); pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.evaluate("""()=>{ let X=null; for(let x=-300;x<300&&!X;x+=2)for(let z=-300;z<300;z+=2){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+2){ let ok=true; for(let a=-12;a<=12&&ok;a+=4)for(let b2=-12;b2<=12;b2+=4){ const q=colInfo(x+a,z+b2); if(Math.abs(q.h-c.h)>1||q.top!==GRASS){ ok=false; break; } } if(ok){ X=[x,z,c.h]; break; } } }
      const [x,z,h]=X; for(let i=-4;i<=12;i++) for(let j=-8;j<=8;j++){ for(let k=h+1;k<=h+8;k++) setB(x+i,k,z+j,AIR); setB(x+i,h,z+j,GRASS); }
      globalThis.__P=[x,z,h]; beastSpawnT=1e9; wbSpawnT=1e9; catSpawnT=1e9; ratSpawnT=1e9; tod=0.27; }""")
    for kind in ['bear','tiger','spider','scorpion']:
        pg.evaluate("""(k)=>{ const [x,z,h]=__P; mobs.length=0; const m=newBeast(k,x+6,h+1,z); m.yaw=-Math.PI/2-0.6; m.idleT=999; mobs.push(m); globalThis.__m=m;
          for(const mm of mobs) mm.angry=0; BEAST[k]._ag=BEAST[k].aggro; BEAST[k].aggro=0;
          player.x=x+0.5; player.z=z+0.5; player.y=h+1.4; let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.05){ player.yaw=a; const f=camVectors().f; if(f[0]>bd){bd=f[0];ba=a;} } player.yaw=ba; player.pitch=-0.3; player.y=h+2.6; document.getElementById('hotbar').style.display='none'; }""", kind)
        pg.wait_for_timeout(1200); pg.screenshot(path=f'/tmp/bst_{kind}.png')
        pg.evaluate("(k)=>{ BEAST[k].aggro=BEAST[k]._ag; }", kind)
    # function: a tiger hunts and bites, killing gives drops
    r = pg.evaluate("""async ()=>{ const [x,z,h]=__P; mobs.length=0; health=20; const m=newBeast('tiger',x+9,h+1,z); mobs.push(m);
        player.x=x+0.5; player.z=z+0.5; player.y=h+1;
        const h0=health; await new Promise(r=>setTimeout(r,5000)); const bit = h0-health, dist=Math.hypot(m.x-player.x,m.z-player.z);
        const before = itemDrops.length; for(let i=0;i<30&&!m.dead;i++){ m.iframe=0; mobHit(m,5); }
        await new Promise(r=>setTimeout(r,300));
        const got = itemDrops.slice(before).map(d=>NAMES[d.id]);
        // bear stays calm at distance, angers when hit
        mobs.length=0; health=20; const br=newBeast('bear',x+8,h+1,z); mobs.push(br); await new Promise(r=>setTimeout(r,2500)); const calm=br.angry<=0 && health===20;
        br.iframe=0; mobHit(br,1); const ang=br.angry>0;
        const cook = COOK_RECIPES.filter(r=>r.out[0]===STEAK||r.out[0]===MEAT_STEW).map(r=>r.name);
        // wild spawn per biome
        const cnt={}; for(let t=0;t<400;t++){ const xx=Math.floor(Math.random()*6000-3000), zz=Math.floor(Math.random()*6000-3000); const b=biomeAt(xx,zz); for(const k in BEAST) if(BEAST[k].where(b,50)) cnt[k+':'+b]=(cnt[k+':'+b]||0)+1; }
        return {bit, dist:+dist.toFixed(2), killed:m.dead, got, calm, ang, cook, food:[FOOD_VAL[RAW_MEAT],FOOD_VAL[STEAK],FOOD_VAL[MEAT_STEW]], cnt}; }""")
    print(json.dumps(r))
    # natural spawning: stand in world, night, force spawns
    r2 = pg.evaluate("""async ()=>{ mobs.length=0; tod=0.75; ratNight=true; let n=0; for(let i=0;i<60;i++){ trySpawnBeasts(); } const k={}; for(const m of mobs) if(BEAST[m.kind]) k[m.kind]=(k[m.kind]||0)+1; return [biomeAt(player.x,player.z), k]; }""")
    print(r2)
    print(errs); b.close()
