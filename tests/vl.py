from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','vl'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000); pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={};
      let V=null,R=null; for(let a=-1;a<=1&&!V;a++)for(let c=-1;c<=1&&!V;c++){ const v=villageAt(a,c); if(v){V=v;R=[a,c];} }
      if(!V) return 'no village';
      const vc=villageCentre(V); player.x=vc[0]; player.z=vc[1]; player.y=colInfo(Math.floor(vc[0]),Math.floor(vc[1])).h+2; tod=0.3; beastSpawnT=1e9;
      await sleep(6000);
      const npcs=()=>mobs.filter(m=>m.kind==='npc');
      out.houses=V.houses.length; out.npcs=npcs().length; out.jobs=npcs().map(m=>m.job);
      // daytime wandering
      const p0=npcs().map(m=>[m.x,m.z]); await sleep(5000); out.moved=npcs().filter((m,i)=>p0[i]&&Math.hypot(m.x-p0[i][0],m.z-p0[i][1])>1).length;
      // a bear walks into the village: guards and villagers kill it
      const g=npcs().find(m=>m.job==='guard'); out.guard=!!g;
      const br=newBeast('bear',Math.floor(vc[0])+3,Math.floor(g.y),Math.floor(vc[1])); br.x=g.x+3; br.z=g.z; br.y=g.y; mobs.push(br);
      await sleep(12000); out.bearDead=br.dead||!mobs.includes(br); out.bearHp=br.hp;
      // night: they go home
      tod=0.75; await sleep(14000);
      out.homeAtNight=npcs().filter(m=>m.job!=='guard'&&m.house&&Math.hypot(m.x-m.house.inside[0]-0.5,m.z-m.house.inside[2]-0.5)<1.5).length+'/'+npcs().filter(m=>m.job!=='guard').length;
      // kill a villager -> dead until dawn -> back
      const v=npcs().find(m=>m.job!=='guard'); const key=v.home; v.iframe=0; mobHit(v,999); await sleep(800);
      out.deadState=JSON.stringify(villagerState[key]); out.goneFromMobs=!mobs.some(m=>m.home===key);
      villagerDawn(); out.afterDawn=JSON.stringify(villagerState[key]||null); tod=0.3; await sleep(4000); out.respawned=mobs.some(m=>m.home===key);
      // break its bed, kill again, dawn -> gone
      const h=V.houses[+key.split(':')[1]]; setB(h.bed[0],h.bed[1],h.bed[2],AIR);
      const v2=mobs.find(m=>m.home===key); if(v2){ v2.iframe=0; mobHit(v2,999); } await sleep(800); villagerDawn(); out.bedless=JSON.stringify(villagerState[key]);
      // guards turn on you
      const g2=npcs().find(m=>m.job==='guard'); const other=npcs().find(m=>m!==g2); other.iframe=0; mobHit(other,1); out.guardAngry=g2.angry>0;
      // gold
      const g0=gold; spawnGold(Math.floor(player.x),Math.floor(player.y),Math.floor(player.z),25); await sleep(1500); out.gold=gold-g0;
      return out; }""")
    print(json.dumps(r))
    print(errs[:5]); b.close()
