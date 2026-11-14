from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','cr2'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={}; health=1000; beastSpawnT=1e9; tod=0.3;
      let V=null; for(let a=-1;a<=1&&!V;a++)for(let c=-1;c<=1&&!V;c++){ const v=villageAt(a,c); if(v)V=v; }
      const vc=villageCentre(V); player.x=vc[0]; player.z=vc[1]; player.y=colInfo(Math.floor(vc[0]),Math.floor(vc[1])).h+2; await sleep(5000);
      const g=mobs.find(m=>m.kind==='npc'&&m.job==='guard'); let q; for(let d=0;d<100;d++){ dayNo=d; q=questOffer(g); if(q.kind==='crypt') break; } out.text=q.text;
      openTalk(g); talkOffer=q; talkAction('accept'); closeCraft(); const cq=quests[0];
      const P=cryptCache.get(cq.crypt); player.x=P.boss[0]+0.5; player.z=P.boss[2]-3.5; player.y=P.boss[1]; await sleep(3500);
      const L=mobs.find(m=>m.kind==='cryptlord'&&m.crypt===P.key); out.lord=!!L; out.chestTier=JSON.stringify(chestItems(...[...P.chestSet][0].split(',').map(Number)));
      if(L){ const g0=gold; for(let i=0;i<60&&!L.dead;i++){ L.iframe=0; mobHit(L,5);} await sleep(1500); out.state=cq.state; out.cleared=JSON.stringify(cryptState[P.key]); }
      health=maxHP(); player.x=vc[0]; player.z=vc[1]; player.y=colInfo(Math.floor(vc[0]),Math.floor(vc[1])).h+2; await sleep(5000);
      let g2=null; for(let w=0;w<20&&!g2;w++){ g2=mobs.find(m=>m.home===g.home); if(!g2) await sleep(500); }
      const g1=gold; openTalk(g2); talkAction('turnin'); out.paid=gold-g1; closeCraft();
      return out; }""")
    print(json.dumps(r, indent=0)); print(errs[:3]); b.close()
