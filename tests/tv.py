from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','tv'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={ gen:worldGen };
      const E=roadEdgesNear(0,0); out.edges=E.map(e=>villageName(...e.ra)+'->'+villageName(...e.rb)+' '+Math.round(e.len)); out.signs=E.flatMap(e=>e.signs.map(s=>s.here+'>'+s.toName+' '+s.dist+' '+s.dir));
      // count road columns along the first edge
      const e=E[0]; let road=0, n=0; for(let t=0;t<e.len;t+=2){ const p=roadPoint(e,t); n++; if(roadAt(Math.floor(p[0]),Math.floor(p[1]))) road++; } out.roadCoverage=road+'/'+n;
      // the actual block at a road point mid-way
      const mid=roadPoint(e,e.len/2), mx=Math.floor(mid[0]), mz=Math.floor(mid[1]), ci=colInfo(mx,mz); out.midBlock=NAMES[blockAt(mx,ci.h,mz)];
      const sg=e.signs[0]; out.signBlock=sg?NAMES[blockAt(sg.x,colInfo(sg.x,sg.z).h+1,sg.z)]:null;
      // walk into the first village -> discovered
      const va=e.va, c=villageCentre(va); player.x=c[0]; player.z=c[1]; player.y=colInfo(Math.floor(c[0]),Math.floor(c[1])).h+2; await sleep(2500);
      out.visited=[...visitedV]; out.explored=explored.size;
      // second village by wagon needs a visit first
      const c2=villageCentre(e.vb); player.x=c2[0]; player.z=c2[1]; player.y=colInfo(Math.floor(c2[0]),Math.floor(c2[1])).h+2; await sleep(2500); out.visited2=[...visitedV];
      // wagon back
      gold=200; const tod0=tod, d0=dayNo; const key=[...visitedV][0]; openMap(); out.side=document.getElementById('mapSide').textContent.slice(0,200);
      wagonTo(key); await sleep(500); out.wagon=[Math.round(Math.hypot(player.x-c[0],player.z-c[1])), 200-gold, +(tod-tod0).toFixed(3), dayNo-d0, craftOpen];
      // rent a room
      await sleep(4000); const inn=mobs.find(m=>m.kind==='npc'&&m.job==='villager'); out.inn=!!inn;
      if(inn){ openTalk(inn); out.roomBtn=document.getElementById('talkBody').innerHTML.includes('RENT A ROOM'); const g0=gold; talkAction('room'); out.room=[g0-gold, JSON.stringify(bedSpawn), talkLine.slice(0,40)]; closeCraft(); }
      return out; }""")
    print(json.dumps(r, indent=0))
    # look down a road
    pg.evaluate("""()=>{ const e=roadEdgesNear(0,0)[0]; let tt=e.len*0.15; while(tt<e.len*0.8 && colInfo(...roadPoint(e,tt).map(Math.floor)).h<=SEA+1) tt+=3; const p=roadPoint(e,tt), q=roadPoint(e,tt+20); player.x=p[0]; player.z=p[1]; player.y=colInfo(Math.floor(p[0]),Math.floor(p[1])).h+1.5; tod=0.3;
      let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; const v=camVectors().f; const d=(v[0]*(q[0]-p[0])+v[2]*(q[1]-p[1])); if(d>bd){bd=d;ba=a;} } player.yaw=ba; player.pitch=-0.15; }""")
    pg.wait_for_timeout(2500); pg.screenshot(path='/tmp/tv_road.png')
    pg.evaluate("()=>{ const s=roadEdgesNear(0,0)[0].signs[1]; player.x=s.x+0.5; player.z=s.z+4.5; player.y=colInfo(s.x,s.z).h+4; }"); pg.wait_for_timeout(2000)
    pg.evaluate("()=>{ const e=roadEdgesNear(0,0)[0]; const s=e.signs[1]; let best=null; for(let a=0;a<6.283;a+=0.3){ const x=Math.floor(s.x+Math.cos(a)*4), z=Math.floor(s.z+Math.sin(a)*4), y=colInfo(x,z).h+1; if(ratCanStand(x,y,z)&&PASS[getB(x,y+1,z)]){ best=[x,y,z]; break; } } player.x=best[0]+0.5; player.z=best[2]+0.5; player.y=best[1]; const dx=s.x+0.5-player.x, dz=s.z+0.5-player.z; let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; const v=camVectors().f; const d=(v[0]*dx+v[2]*dz)/Math.hypot(dx,dz); if(d>bd){bd=d;ba=a;} } player.yaw=ba; player.pitch=-0.1; }")
    pg.wait_for_timeout(2000); pg.screenshot(path='/tmp/tv_sign.png')
    pg.evaluate("()=>{ openMap(); }"); pg.wait_for_timeout(500); pg.screenshot(path='/tmp/tv_map.png')
    print(errs[:3]); b.close()
