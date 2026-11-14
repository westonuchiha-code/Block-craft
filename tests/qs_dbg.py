from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','qs'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000); pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={};
      let V=null; for(let a=-1;a<=1&&!V;a++)for(let c=-1;c<=1&&!V;c++){ const v=villageAt(a,c); if(v)V=v; }
      const vc=villageCentre(V); player.x=vc[0]; player.z=vc[1]; player.y=colInfo(Math.floor(vc[0]),Math.floor(vc[1])).h+2; tod=0.3; beastSpawnT=1e9;
      await sleep(6000);
      const npcs=mobs.filter(m=>m.kind==='npc'); const giver=npcs.find(m=>m.job!=='guard');
      // offers of each kind
      const kinds={}; for(let d=0;d<40;d++){ dayNo=d; const q=questOffer(giver); kinds[q.kind]=(kinds[q.kind]||0)+1; } dayNo=0; out.kinds=kinds;
      // HUNT
      let q; for(let d=0;d<60;d++){ dayNo=d; q=questOffer(giver); if(q.kind==='hunt') break; } out.huntText=q.text;
      openTalk(giver); talkOffer=q; talkAction('accept'); out.accepted=quests.length; closeCraft();
      const hq=quests[0]; player.x=hq.at[0]; player.z=hq.at[1]; player.y=colInfo(hq.at[0],hq.at[1]).h+3; await sleep(5000);
      const tgt=mobs.find(m=>m.questId===hq.id); out.targetSpawned=!!tgt; out.targetKind=tgt&&tgt.kind;
      if(tgt){ for(let i=0;i<40&&!tgt.dead;i++){ tgt.iframe=0; mobHit(tgt,5);} } await sleep(800); out.huntState=hq.state;
      player.x=vc[0]; player.z=vc[1]; player.y=colInfo(Math.floor(vc[0]),Math.floor(vc[1])).h+2; await sleep(5000);
      let g2=null; for(let w=0;w<30&&!g2;w++){ g2=mobs.find(m=>m.home===giver.home); if(!g2) await sleep(500); } if(!g2){ const t0=tod; await sleep(2000); const t1=tod; let ex='none'; try{ trySpawnNpcs(); }catch(e){ ex=String(e)+' '+e.stack.slice(0,300); } return {t0,t1,ex, after:mobs.filter(m=>m.kind==='npc').length, paused, craftOpen, npcSpawnT, st:JSON.stringify(villagerState), npcs:mobs.filter(m=>m.kind==='npc').map(m=>m.home+':'+m.job), d:Math.hypot(player.x-giver.house.out[0],player.z-giver.house.out[2]), stand:npcCanStand(...giver.house.out), giverDead:giver.dead, night:ratNight, tod, inStand:npcCanStand(...giver.house.inside), inB:NAMES[getB(...giver.house.inside)], inBelow:NAMES[getB(giver.house.inside[0],giver.house.inside[1]-1,giver.house.inside[2])]}; } const g0=gold; openTalk(g2); out.reportBtn=document.getElementById('talkBody').innerHTML.includes('REPORT'); talkAction('turnin'); out.huntPaid=gold-g0; out.rep=repOf(g2.village); closeCraft();
      // FETCH
      for(let d=0;d<80;d++){ dayNo=d; q=questOffer(g2); if(q.kind==='fetch') break; } openTalk(g2); talkOffer=q; talkAction('accept'); inv[q.item]=q.n+1; renderTalk();
      out.fetchBtn=document.getElementById('talkBody').innerHTML.includes('HAND OVER'); const g1=gold; talkAction('turnin'); out.fetchPaid=gold-g1; out.fetchLeft=inv[q.item]; closeCraft();
      // DELIVER
      for(let d=0;d<80;d++){ dayNo=d; q=questOffer(g2); if(q.kind==='deliver') break; } out.delText=q.kind==='deliver'?q.text:'none';
      if(q.kind==='deliver'){ openTalk(g2); talkOffer=q; talkAction('accept'); closeCraft(); out.parcel=inv[PARCEL];
        // go to recipient village
        player.x=q.tvc[0]; player.z=q.tvc[1]; player.y=colInfo(Math.floor(q.tvc[0]),Math.floor(q.tvc[1])).h+2; await sleep(7000);
        const rcp=mobs.find(m=>m.home===q.to); out.recipient=rcp?rcp.name+'/'+q.toName:'missing';
        if(rcp){ const g3=gold; openTalk(rcp); out.giveBtn=document.getElementById('talkBody').innerHTML.includes('GIVE PARCEL'); talkAction('deliver'); out.delPaid=gold-g3; out.parcelAfter=inv[PARCEL]; closeCraft(); }
      }
      // EXPIRY
      dayNo=0; for(let d=0;d<80;d++){ dayNo=d; q=questOffer(g2); if(q.kind==='fetch') break; } openTalk(g2); talkOffer=q; talkAction('accept'); closeCraft();
      const r0=repOf(g2.village); for(let i=0;i<6;i++) questDawn(); out.expired=quests.length===0; out.repDrop=repOf(g2.village)-r0;
      // violence lowers standing; shunned
      const vv=mobs.find(m=>m.kind==='npc'&&m.job!=='guard'&&m.village); const r1=repOf(vv.village); vv.iframe=0; mobHit(vv,1); out.hitRep=repOf(vv.village)-r1;
      villageRep[vkey(vv.village)]=-40; for(const m of mobs) m.angry=0; openTalk(vv); out.shunned=document.getElementById('talkBody').textContent.includes("don't deal"); closeCraft(); villageRep[vkey(vv.village)]=20;
      // new hunt for the log screenshot
      for(let d=0;d<60;d++){ dayNo=d; q=questOffer(vv); if(q.kind==='hunt') break; } openTalk(vv); talkOffer=q; talkAction('accept'); closeCraft();
      for(let d=0;d<60;d++){ dayNo=d+100; q=questOffer(g2); if(q.kind==='deliver') break; } openTalk(g2); talkOffer=q; talkAction('accept'); closeCraft();
      return out; }""")
    print(json.dumps(r, indent=0))
    pg.evaluate("()=>openQuests()"); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/qs_log.png'); pg.evaluate("()=>closeQuests()")
    pg.evaluate("()=>{ const m=mobs.find(m=>m.kind==='npc'&&m.job!=='guard'&&!quests.some(q=>q.giver===m.home)); openTalk(m); talkAction('work'); }"); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/qs_offer.png')
    print(errs[:3]); b.close()
