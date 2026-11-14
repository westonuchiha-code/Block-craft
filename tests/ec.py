from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','ec'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={};
      let V=null; for(let a=-1;a<=1&&!V;a++)for(let c=-1;c<=1&&!V;c++){ const v=villageAt(a,c); if(v)V=v; }
      const vc=villageCentre(V); player.x=vc[0]; player.z=vc[1]; player.y=colInfo(Math.floor(vc[0]),Math.floor(vc[1])).h+2; tod=0.3; beastSpawnT=1e9;
      await sleep(6000); const npcs=mobs.filter(m=>m.kind==='npc'); out.jobs=npcs.map(m=>m.job);
      const m=npcs.find(m=>m.job!=='guard'); const kinds={}; for(let d=0;d<60;d++){ dayNo=d; const q=questOffer(m); const k=q.kind+(q.order?'-order':''); kinds[k]=(kinds[k]||0)+1; } dayNo=0; out.kinds=kinds;
      // ORDER
      let q; for(let d=0;d<200;d++){ dayNo=d; q=questOffer(m); if(q.order) break; } out.orderText=q.text;
      openTalk(m); talkOffer=q; talkAction('accept'); inv[q.item]=(inv[q.item]||0)+q.n; renderTalk(); const g0=gold; talkAction('turnin'); out.orderPaid=gold-g0; closeCraft();
      // BUILD (lanterns)
      for(let d=0;d<300;d++){ dayNo=d; q=questOffer(m); if(q.kind==='build') break; } out.buildText=q.text;
      openTalk(m); talkOffer=q; talkAction('accept'); closeCraft(); const bq=quests.find(x=>x.kind==='build');
      const J=BUILD_JOBS.find(j=>j.key===bq.job); const item={light:LANTERN0+1,walls:STONE_BRICK,fence:fenceId(0,0),pave:FLAGSTONE,trees:SAP_IDS[0]}[bq.job];
      inv[item]=bq.n+2; HOTBAR[0]=item; sel=0;
      // place them for real with placeBlock: aim at the ground around
      let placed=0; const px=Math.floor(player.x), pz=Math.floor(player.z), py=Math.floor(player.y);
      for(let i=0;i<300 && bq.state!=='done';i++){ const x=px+Math.floor(Math.random()*24)-12, z=pz+Math.floor(Math.random()*24)-12; if(craftOpen) closeCraft(); const h=colInfo(x,z).h; if(bq.job==='trees'){ setB(x,h,z,GRASS); }
        player.x=x+0.5; player.z=z+2.5; player.y=h+1; player.pitch=0.9; let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.05){ player.yaw=a; const v=camVectors().f; if(-v[2]>bd){bd=-v[2];ba=a;} } player.yaw=ba;
        const hit=target(); if(hit){ placeBlock(); placed++; } }
      let realF=0; for(let x=px-10;x<=px+10;x++) for(let z=pz-10;z<=pz+10;z++) for(let y=py-6;y<=py+6;y++) if(IS_FENCE[getB(x,y,z)]||IS_LANTERN[getB(x,y,z)]||getB(x,y,z)===FLAGSTONE&&(placedMap.get(placedKey(x,y,z)[0])||new Set()).has(placedKey(x,y,z)[1])) realF++; out.build=[bq.job,bq.got,bq.n,bq.state,placed,realF,inv[item]];
      const g1=gold; openTalk(mobs.find(x=>x.home===bq.giver)); talkAction('turnin'); out.buildPaid=gold-g1; closeCraft();
      // TRAIN
      const tr=npcs.find(x=>TRAINS[x.job]); const sid=TRAINS[tr.job]; gold=500; const s0=skills[sid]; openTalk(tr); talkAction('train'); out.train=[tr.job,sid,s0,skills[sid],500-gold]; talkAction('train'); out.trainAgain=talkLine; closeCraft();
      // REPAIR
      inv[AR(2,1)]=1; equipArmor(AR(2,1)); armor[1].dur=100; const sm={job:'blacksmith',home:'x',village:tr.village,vc:tr.vc,id:999,x:player.x,z:player.z,name:'Smith',pose:{},angry:0,dead:false};
      const g2=gold; talkNpc=sm; talkAction('repair'); out.repair=[gold<g2, armor[1].dur, ARMOR[armor[1].id].dur, g2-gold]; talkNpc=null;
      out.buys=SHOPS.villager.buy.length;
      return out; }""")
    print(json.dumps(r))
    print(errs[:3]); b.close()
