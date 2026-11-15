from playwright.sync_api import sync_playwright
import json, sys
# The horse: bought from a farmer, mounted with use, ridden much faster with a raised view, left where you get down, remembered in the save.
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','horse'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    # a flat field, cleared of trees, to ride on
    pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; tod=0.25; let X=null;
      for(let x=-300;x<300&&!X;x+=5) for(let z=-300;z<300;z+=5){ const c=colInfo(x,z); if(c.top!==GRASS||c.open||c.h<=SEA+2||nearVillage(x,z)) continue; let ok=true; for(let a=-3;a<=3&&ok;a++) for(let b=-26;b<=3;b++){ const q=colInfo(x+a,z+b); if(q.h!==c.h||q.top!==GRASS){ ok=false; break; } } if(ok){ X=[x,z,c.h]; break; } }
      window.__X=X; player.x=X[0]+0.5; player.z=X[1]+0.5; player.y=X[2]+1; player.yaw=0; player.pitch=0; }""")
    pg.wait_for_timeout(2500)
    r=pg.evaluate("""()=>{ const X=window.__X, o={}; mobs.length=0; for(let a=-3;a<=3;a++) for(let b=-26;b<=3;b++) for(let k=1;k<8;k++) setB(X[0]+a,X[2]+k,X[1]+b,AIR);
      const far={ job:'farmer', village:[0,0], name:'T', x:player.x, z:player.z }; talkNpc=far;
      gold=100; buyHorse(far); o.poor=[!!horse, gold];
      gold=500; const j0=journal.length; buyHorse(far); o.bought=[!!horse, gold, !!horseMob(), journal.slice(j0).some(e=>e.t.startsWith('Bought a horse'))];
      gold=500; buyHorse(far); o.second=gold; talkNpc=null;
      const m=horseMob(); o.tame=[BEAST.horse.tame, npcHostile(m)]; const hp=m.hp; beastHit(m, 50); o.unhurt=m.hp===hp;
      o.eye0=[EYE_H,BODY_H]; return o; }""")
    print(json.dumps(r))
    if not (r['poor']==[False,100] and r['bought']==[True,200,True,True] and r['second']==500 and r['tame']==[True,False] and r['unhurt'] and r['eye0']==[1.6,1.69]): bad.append('buying')
    def run(ms):
        pg.evaluate("()=>{ const X=window.__X; player.x=X[0]+0.5; player.z=X[1]+0.5; player.y=X[2]+1; player.yaw=0; player.pitch=0; if(!running) toggleRun(); keys.KeyW=true; window.__z0=player.z; }")
        pg.wait_for_timeout(ms); return pg.evaluate("()=>{ keys.KeyW=false; return window.__z0-player.z; }")
    foot=run(2500)
    m=pg.evaluate("""()=>{ const o={}, X=window.__X, h=horseMob(); player.x=X[0]+0.5; player.z=X[1]+0.5; player.y=X[2]+1; h.x=player.x+1; h.z=player.z; h.y=player.y;
      o.mount=mountHorse(h); o.riding=riding(); o.eye=[EYE_H,BODY_H]; o.at=[player.x===h.x, h.ridden]; return o; }""")
    ride=run(2500)
    f=pg.evaluate("""()=>{ const o={}, h=horseMob(); o.under=[Math.abs(h.x-player.x)<0.01, Math.abs(h.z-player.z)<0.01, h.ridden===true]; o.notHit=ratRay(player.x, player.y+EYE_H, player.z, 0,-1,0, 4)===null;
      camSetup(); o.camY=+(CAM.y-player.y).toFixed(2);
      toggleSneak(); o.down=[riding(), sneaking, EYE_H, !!horseMob(), horseMob().ridden, Math.hypot(horse.x-player.x, horse.z-player.z)<2.5];
      const hx=horse.x, hz=horse.z; mobs.length=0; horseTick(); o.back=[!!horseMob(), horseMob() && Math.abs(horseMob().x-hx)<0.01];
      saveWorld(); const meta=JSON.parse(localStorage.getItem(wkey(currentWorld,'world'))); o.saved=!!(meta.horse && Math.abs(meta.horse.x-hx)<0.01 && meta.horse.mounted===false);
      // no room under a low roof
      const px=Math.floor(player.x), py=Math.floor(player.y), pz=Math.floor(player.z); setB(px,py+2,pz,STONE); const h2=horseMob(); h2.x=player.x; h2.z=player.z; mountHorse(h2); o.low=riding(); setB(px,py+2,pz,AIR);
      return o; }""")
    print('foot', round(foot,2), 'ride', round(ride,2), json.dumps(m), json.dumps(f)); print(errs)
    if not (m['mount'] and m['riding'] and m['eye']==[2.45,2.54] and m['at']==[True,True]): bad.append('mounting')
    if not (foot>3 and 1.6<ride/foot<2.1): bad.append('riding speed')
    if not (f['under']==[True,True,True] and f['notHit'] and f['camY']==2.45): bad.append('in the saddle')
    if not (f['down']==[False,False,1.6,True,False,True] and f['back']==[True,True] and f['saved'] and f['low'] is False): bad.append('getting down and coming back')
    b.close()
print('HORSE TEST FAILED', bad) if bad else print('horse ok')
sys.exit(1 if (bad or errs) else 0)
