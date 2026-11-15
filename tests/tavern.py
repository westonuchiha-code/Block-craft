from playwright.sync_api import sync_playwright
import json, sys
# Taverns (worlds from worldGen 7): one per village with an innkeeper, a spare bed to rent, a board of food and fresh rumours;
# the rest of the village is exactly where it was without it; villagers gather there in the evening and go home at night.
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','tavern'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const o={gen:worldGen,n:0,t:0,g:0}; const names=new Set(), sig={};
      const S=v=>v.houses.filter(h=>h.job!=='innkeeper').map(h=>[h.x,h.z,h.F,h.w,h.d,h.r].join(':')).join('|');      // where every building stands (who lives in one may differ: a new world always has a guard)
      for(let rx=-5;rx<=5;rx++) for(let rz=-5;rz<=5;rz++){ const v=villageAt(rx,rz); if(!v||!v.houses) continue; o.n++; sig[rx+','+rz]=S(v);
        if(v.tavern!==undefined){ o.t++; const h=v.houses[v.tavern]; if(h.guest && h.job==='innkeeper' && v.tavern===v.houses.length-1) o.g++; names.add(tavernName(rx,rz)); } }
      o.names=names.size; o.signs=0; o.lamps=0; o.guards=0; for(let rx=-5;rx<=5;rx++) for(let rz=-5;rz<=5;rz++){ const v=villageAt(rx,rz); if(v&&v.houses&&v.houses.some(h=>h.job==='guard')) o.guards++; }
      for(let rx=-5;rx<=5;rx++) for(let rz=-5;rz<=5;rz++){ const v=villageAt(rx,rz); if(!v||v.tavern===undefined) continue; let sg=0, lp=0;
        for(const q of v.late){ if(q[3]===TSIGN0||q[3]===TSIGN0+1) sg++; if(q[3]===LANTERN0) lp++; }
        let found=0; for(const arr of v.cells.values()) for(let i=1;i<arr.length;i+=2) if(arr[i]===TSIGN0||arr[i]===TSIGN0+1) found++;
        if(sg===1 && found===1) o.signs++; if(lp===2) o.lamps++; }
      { const v=villageAt(0,0), h=v.houses[v.tavern]; o.near=[tavernNear(h.x,h.z)===tavernName(0,0), tavernNear(h.x+60,h.z)===null]; }
      worldGen=6; villageCache.clear(); o.old=0; o.same=0; o.oldTav=0;                         // the same world as an older build made it
      for(const k in sig){ const [rx,rz]=k.split(',').map(Number), v=villageAt(rx,rz); if(!v||!v.houses) continue; o.old++; if(S(v)===sig[k] && v.houses.length===sig[k].split('|').length) o.same++; if(v.tavern!==undefined) o.oldTav++; }
      worldGen=7; villageCache.clear();
      const v=villageAt(0,0), h=v.houses[v.tavern]; window.__h=h; window.__v=v;
      player.x=v.cx+0.5; player.z=v.cz+0.5; player.y=v.g+12; fly=true; tod=0.3; return o; }""")
    print(json.dumps(r))
    if not (r['gen']==7 and r['t']>=0.9*r['n'] and r['g']==r['t'] and r['names']>=10): bad.append('taverns per village')
    if not (r['signs']==r['t'] and r['lamps']==r['t'] and r['near']==[True,True]): bad.append('sign and lamps')
    if r['guards']!=r['n']: bad.append('a guard in every village')
    if not (r['old']==r['n'] and r['same']==r['n'] and r['oldTav']==0): bad.append('older worlds changed')
    pg.wait_for_timeout(5000)
    t=pg.evaluate("""()=>{ const o={}, k=mobs.find(m=>m.kind==='npc' && m.job==='innkeeper'); if(!k) return {none:1};
      gold=50; openTalk(k); o.title=document.getElementById('talkName').textContent;
      const html=()=>document.getElementById('talkMenu').innerHTML;
      o.room=html().includes('RENT A ROOM'); const seen0=cryptSeen.size, j0=journal.length;
      talkAction('news'); const s1=cryptSeen.size; talkAction('news'); o.rumours=[s1-seen0, cryptSeen.size-s1];
      talkAction('room'); o.gold=gold; o.bed=bedSpawn && bedSpawn.join(',')===window.__h.guest.join(','); o.isBed=!!IS_BED[getB(...window.__h.guest)];
      o.journal=journal.slice(j0).some(e=>e.t.includes('Took a room at '+tavernName(0,0)));
      o.stew=SHOPS.innkeeper.sell.includes(MEAT_STEW); talkAction('trade'); o.trade=html().includes('meat stew')||html().includes('MEAT STEW')||html().includes('stew');
      closeTalk(); tod=0.44; return o; }""")
    print(json.dumps(t))
    if t.get('none') or not ('Innkeeper' in t['title'] and t['room'] and t['rumours']==[1,1] and t['gold']==42 and t['bed'] and t['isBed'] and t['journal'] and t['stew'] and t['trade']): bad.append('innkeeper')
    q="""()=>{ const h=window.__h, W=(h.r&1)?h.d:h.w, D=(h.r&1)?h.w:h.d, inn=m=>Math.abs(m.x-0.5-h.x)<=(W-1)/2 && Math.abs(m.z-0.5-h.z)<=(D-1)/2;
      const L=mobs.filter(m=>m.kind==='npc' && m.house && m.job!=='guard' && m.job!=='innkeeper');      // (people of the village: a pedlar passing through has no house)
      return { drinkers:L.filter(npcDrinks).length, inTavern:L.filter(m=>npcDrinks(m)&&inn(m)).length, soberIn:L.filter(m=>!npcDrinks(m)&&inn(m)).length,
               home:(()=>{ window.__home=window.__home||new Set(); for(const m of L) if(Math.hypot(m.x-0.5-m.house.inside[0], m.z-0.5-m.house.inside[2])<2.5) window.__home.add(m.home); return L.filter(m=>window.__home.has(m.home)).length; })(),      // (has been home: at night some step out again to see off the rats)
               all:L.length, hour:tavernHour() }; }"""
    e={}
    for i in range(16):
        pg.wait_for_timeout(6000); pg.evaluate("()=>{ if(tod>0.5 || tod<0.42) tod=0.45; }"); e=pg.evaluate(q)
        if e['drinkers'] and e['inTavern']==e['drinkers']: break
    print('evening', json.dumps(e))
    if not (e['hour'] and e['drinkers']>=1 and e['inTavern']==e['drinkers'] and e['soberIn']==0): bad.append('evening at the tavern')
    pg.evaluate("()=>{ tod=0.62; window.__home=new Set(); }"); n={}
    for i in range(16):
        pg.wait_for_timeout(6000); pg.evaluate("()=>{ if(tod>0.9 || tod<0.6) tod=0.62; }"); n=pg.evaluate(q)
        if n['home']==n['all'] and n['inTavern']==0: break
    print('night', json.dumps(n)); print(errs)
    if not (not n['hour'] and n['home']>=n['all']-1 and n['all']>=3 and n['inTavern']==0): bad.append('home at night')      # (one may be out seeing off the rats at any moment)
    b.close()
print('TAVERN TEST FAILED', bad) if bad else print('tavern ok')
sys.exit(1 if (bad or errs) else 0)
