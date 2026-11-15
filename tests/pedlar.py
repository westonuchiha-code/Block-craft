from playwright.sync_api import sync_playwright
import json, sys
# Travellers on the roads: a pedlar appears on a road near you by day, follows the road toward a village, trades from his pack, offers no work.
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/blockcraft_prototype.html'
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(1500)
    pg.fill('#newName','pedlar'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    # stand on a road well outside the village
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; tod=0.25; const v=villageAt(0,0); let X=null;
      for(let r=60;r<170&&!X;r+=4) for(let a=0;a<64;a++){ const x=Math.floor(v.cx+Math.cos(a*0.098)*r), z=Math.floor(v.cz+Math.sin(a*0.098)*r); if(roadAt(x,z) && !nearVillage(x,z) && colInfo(x,z).h>SEA+1){ X=[x,z]; break; } }
      if(!X) return null; window.__X=X; player.x=X[0]+0.5; player.z=X[1]+0.5; player.y=colInfo(X[0],X[1]).h+1; fly=false; return X; }""")
    print('road at', r)
    if not r: bad.append('no road found')
    else:
        pg.wait_for_timeout(3500)
        s=pg.evaluate("""()=>{ const o={}; mobs.length=0; ratNight=false; travT=1; travellerTick(); const m=mobs.find(q=>q.pedlar); o.spawned=!!m; if(!m) return o;
          window.__m=m; o.dist=Math.round(Math.hypot(m.x-player.x,m.z-player.z)); o.onRoad=roadAt(Math.floor(m.x),Math.floor(m.z)); o.to=m.road.to; o.d0=Math.hypot(m.road.to[0]-m.x, m.road.to[1]-m.z);
          travT=1; travellerTick(); o.one=mobs.filter(q=>q.pedlar).length;
          gold=200; openTalk(m); const html=()=>document.getElementById('talkBody').innerText; o.title=document.getElementById('talkName').textContent;
          o.noWork=!html().includes('ASK FOR WORK'); o.trade=html().includes('TRADE'); talkAction('trade'); o.pack=html().toLowerCase().includes('candle'); talkAction('back'); talkAction('news'); o.news=html().length>40; closeTalk();
          const hp=m.hp; npcHit(m,1); o.noCrime=Object.keys(bounty).length===0; m.fleeT=0; m.hp=hp; return o; }""")
        print(json.dumps(s))
        if not (s.get('spawned') and 30<=s['dist']<=50 and s['onRoad'] and s['one']==1): bad.append('setting out')
        elif not ('Pedlar' in s['title'] and s['noWork'] and s['trade'] and s['pack'] and s['news'] and s['noCrime']): bad.append('talking to him')
        if s.get('spawned'):
            w={}
            for i in range(8):
                pg.wait_for_timeout(5000)
                w=pg.evaluate("()=>{ const m=window.__m; player.x=m.x+6; player.z=m.z+6; player.y=colInfo(Math.floor(player.x),Math.floor(player.z)).h+1; return { d:m.road ? Math.hypot(m.road.to[0]-m.x, m.road.to[1]-m.z) : 0, road:!!m.road, near:[-2,-1,0,1,2].some(a=>[-2,-1,0,1,2].some(b=>roadAt(Math.floor(m.x)+a,Math.floor(m.z)+b))), alive:mobs.includes(m) }; }")
                if s['d0']-w['d']>14: break
            print('walked', round(s['d0']-w['d'],1), json.dumps(w))
            if not (w['alive'] and (s['d0']-w['d']>14 or not w['road']) and w['near']): bad.append('walking the road')
    print(errs); b.close()
print('PEDLAR TEST FAILED', bad) if bad else print('pedlar ok')
sys.exit(1 if (bad or errs) else 0)
