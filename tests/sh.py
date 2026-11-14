from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','sh'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000); pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={};
      let V=null; for(let a=-1;a<=1&&!V;a++)for(let c=-1;c<=1&&!V;c++){ const v=villageAt(a,c); if(v)V=v; }
      const vc=villageCentre(V); player.x=vc[0]; player.z=vc[1]; player.y=colInfo(Math.floor(vc[0]),Math.floor(vc[1])).h+2; tod=0.3; beastSpawnT=1e9;
      await sleep(6000);
      const npcs=mobs.filter(m=>m.kind==='npc'); out.jobs=npcs.map(m=>m.job);
      // aim at a shopkeeper and press use
      const m=npcs.find(m=>SHOPS[m.job]); player.x=m.x; player.z=m.z+2.2; player.y=m.y; m.idleT=99; m.state='idle'; m.path=null;
      const dx=m.x-player.x, dz=m.z-player.z; let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; player.pitch=0.05; const v=camVectors().f; const d=(v[0]*dx+v[2]*dz)/Math.hypot(dx,dz); if(d>bd){bd=d;ba=a;} } player.yaw=ba;
      for(let pt=-0.5;pt<=0.5;pt+=0.05){ player.pitch=pt; const {f}=camVectors(); const mh=ratRay(player.x,player.y+1.6,player.z,f[0],f[1],f[2],3.6); if(mh&&mh.m===m) break; }
      placeBlock(); out.opened=talkNpc===m; out.job=m.job;
      gold=100; talkAction('news'); out.news=talkLine;
      talkAction('trade'); const id=SHOPS[m.job].sell[0]; const n0=inv[id]||0; talkBuy(id); out.buy=[NAMES[id], (inv[id]||0)-n0, 100-gold];
      const sid=SHOPS[m.job].buy[0]; inv[sid]=5; const g0=gold; talkSell(sid); out.sell=[NAMES[sid], inv[sid], gold-g0];
      renderTalk(); return out; }""")
    print(json.dumps(r))
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/sh_trade.png')
    pg.evaluate("()=>{ talkAction('back'); }"); pg.wait_for_timeout(200); pg.screenshot(path='/tmp/sh_talk.png')
    r2=pg.evaluate("""()=>{ const out={}; tod=0.75; ratNight=true; talkAction('trade'); out.closed=document.getElementById('talkBody').textContent.includes('closed');
      closeCraft(); out.closedUi=!talkNpc && !craftOpen;
      const c=mobs.find(m=>m.kind==='npc'&&m.job!=='guard'); c.job='cleric'; openTalk(c); health=6; gold=100; talkAction('heal'); out.heal=[health, gold]; closeCraft();
      return out; }""")
    print(r2); print(errs[:3]); b.close()
