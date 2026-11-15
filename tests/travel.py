from playwright.sync_api import sync_playwright
import json, sys
# Wagon travel: careful (dearer, slower, arrive fed and whole) and reckless (cheaper, quicker, hungry, the road may take its toll).
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1920,'height':1080}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','travel'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(6000)
    r=pg.evaluate("""async ()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const o={}; const sleep=t=>new Promise(r=>setTimeout(r,t));
      // learn of the next village so there is somewhere to go
      const [rx,rz]=[Math.floor(player.x/VREG),Math.floor(player.z/VREG)]; let dest=null; for(let a=-3;a<=3&&!dest;a++) for(let b=-3;b<=3&&!dest;b++){ if(!a&&!b) continue; const v=villageAt(rx+a,rz+b); if(v&&v.houses){ visitedV.add((rx+a)+','+(rz+b)); dest=(rx+a)+','+(rz+b); } }
      const P=knownPlaces().find(q=>q.key===dest), home=knownPlaces().find(q=>q.key!==dest); o.places=knownPlaces().length;
      const c=wagonCost(P,false), r=wagonCost(P,true); o.careful=[c.gold,c.hours,c.risk]; o.reckless=[r.gold,r.hours,+r.risk.toFixed(2)];
      openMap(); const side=document.getElementById('mapSide').innerText; o.buttons=[side.includes('CAREFUL'), side.includes('RECKLESS')]; closeMap();
      // careful: pay, arrive fed and whole
      gold=500; food=5; health=6; const d0=dayNo, t0=tod; wagonTo(dest,false); await sleep(600);
      o.afterCareful={paid:500-gold, food, whole:health===maxHP(), near:Math.hypot(player.x-P.x,player.z-P.z)<20, hoursPassed:Math.round((((dayNo-d0)+(tod-t0))*24))};
      // reckless back, many times with the dice loaded both ways
      const R=Math.random; let tolls=0, n=0; for(let i=0;i<12;i++){ const here=atPlace(); const to=here && here.key===dest ? home : P; if(!to) break; gold=300; food=18; health=maxHP(); const g0=gold, h0=health;
        Math.random = i%2 ? ()=>0.001 : ()=>0.999; const rc=wagonCost(to,true); wagonTo(to.key,true); Math.random=R; await sleep(150); n++;
        const lost=(g0-gold)-rc.gold, hurtBy=h0-health; if(lost>0||hurtBy>0) tolls++; if(i%2===0 && (lost>0||hurtBy>0)) o.tollWithoutRoll=true; if(i%2===1 && !(lost>0||hurtBy>0)) o.noTollOnRoll=true; if(food>=18) o.notHungry=true; }
      o.recklessTrips=n; o.tolls=tolls; o.journal=journal.filter(e=>e.t.startsWith('Travelled')).length; o.tollLine=journal.some(e=>/Robbers|overturned/.test(e.t));
      return o; }""")
    print(json.dumps(r)); print(errs)
    c,k=r['careful'],r['reckless']
    ok=(r['places']>=2 and r['buttons']==[True,True] and k[0]<c[0] and k[1]<=c[1] and c[2]==0 and k[2]>0 and r['afterCareful']['paid']==c[0] and r['afterCareful']['food']>=14 and r['afterCareful']['whole'] and r['afterCareful']['near']
        and abs(r['afterCareful']['hoursPassed']-c[1])<=1 and r['recklessTrips']==12 and r['tolls']==6 and not r.get('tollWithoutRoll') and not r.get('noTollOnRoll') and not r.get('notHungry') and r['journal']==13 and r['tollLine'])
    if not ok: bad.append('travel')
    b.close()
print('TRAVEL TEST FAILED', bad) if bad else print('travel ok')
sys.exit(1 if (bad or errs) else 0)
