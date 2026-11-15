from playwright.sync_api import sync_playwright
import json, sys
# Bounty hunters: while the province holds 150 gold or more against you, one comes for you outside the villages; never for less, never in a village.
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/blockcraft_prototype.html'
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(1500)
    pg.fill('#newName','hunter'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; travT=1e9; tod=0.25; let X=null;
      for(let x=-300;x<300&&!X;x+=5) for(let z=-300;z<300;z+=5){ const c=colInfo(x,z); if(c.top!==GRASS||c.open||c.h<=SEA+2||nearVillage(x,z)) continue; let ok=true; for(let a=-6;a<=6&&ok;a+=3) for(let b=-6;b<=6;b+=3){ const q=colInfo(x+a,z+b); if(Math.abs(q.h-c.h)>1||q.top!==GRASS){ ok=false; break; } } if(ok){ X=[x,z,c.h]; break; } }
      window.__X=X; player.x=X[0]+0.5; player.z=X[1]+0.5; player.y=X[2]+1; health=1000; }""")
    pg.wait_for_timeout(3000)
    r=pg.evaluate("""()=>{ const o={}, P=provinceAt(player.x,player.z); mobs.length=0; const j0=journal.length;
      bounty={}; bounty[P.key]=100; hunterT=1; hunterTick(); o.petty=mobs.filter(m=>m.hunter).length;
      bounty[P.key]=200; hunterT=1; hunterTick(); const m=mobs.find(q=>q.hunter); o.came=!!m; if(!m) return o;
      window.__m=m; o.d0=Math.hypot(m.x-player.x,m.z-player.z); o.is=[m.bandit===1, m.angry>60, m.name.endsWith('the bounty hunter'), journal.slice(j0).some(e=>e.t.startsWith('A bounty hunter came for me')), !!document.body.innerText.match(/A BOUNTY HUNTER/)];
      hunterT=1; hunterTick(); o.one=mobs.filter(q=>q.hunter).length;
      const v=villageAt(0,0); const sx=player.x, sz=player.z; player.x=v.cx+0.5; player.z=v.cz+0.5; mobs.length=0; hunterT=1; hunterTick(); o.inVillage=mobs.filter(q=>q.hunter).length; player.x=sx; player.z=sz; mobs.push(m);
      return o; }""")
    print(json.dumps(r))
    if not (r['petty']==0 and r.get('came') and 20<=r['d0']<=32 and r['is']==[True,True,True,True,True] and r['one']==1 and r['inVillage']==0): bad.append('the hunter comes')
    else:
        d=99
        for i in range(8):
            pg.wait_for_timeout(3000); d=pg.evaluate("()=>{ const m=window.__m; return Math.hypot(m.x-player.x,m.z-player.z); }")
            if d<4: break
        k=pg.evaluate("()=>{ const m=window.__m, P=provinceAt(player.x,player.z); for(let i=0;i<40 && !m.dead;i++){ m.iframe=0; npcHit(m,10); } return [m.dead, bounty[P.key]]; }")
        print('closed to', round(d,1), k); 
        if not (d<4 and k==[True,200]): bad.append('he closes in, and killing him settles nothing')
    print(errs); b.close()
print('HUNTER TEST FAILED', bad) if bad else print('hunter ok')
sys.exit(1 if (bad or errs) else 0)
