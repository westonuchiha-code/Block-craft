from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','uw'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={}; health=1000;
      // go to the underworld floor
      let P=null; for(let x=0;x<400&&!P;x+=4){ const z=UNDER_Z+40, c=underCol(x,z); if(c.hf>UNDER_LAVA+3 && c.hc-c.hf>14){ let ok=true; for(let a=-6;a<=6;a+=3) if(Math.abs(underCol(x+a,z).hf-c.hf)>1) ok=false; if(ok) P=[x,z,c.hf]; } }
      out.site=P; const [x,z,hf]=P; player.x=x+0.5; player.z=z+0.5; player.y=hf+1; ogreSpawnT=1e9; await sleep(2500);
      for(let i=mobs.length-1;i>=0;i--) mobs.splice(i,1);
      const d=newBeast('daedra',x+9,hf+1,z); mobs.push(d); d.angry=30; const h0=health; await sleep(9000);
      out.daedra=[d.lvl, d.hp, h0-health, fx.length];
      const dr=newBeast('daedroth',x+3,hf+1,z+2); mobs.push(dr); dr.angry=30; const h1=health; await sleep(4000); out.daedroth=[dr.hp, h1-health];
      // spawning
      mobs.length=0; for(let i=0;i<10;i++) trySpawnDaedra(); out.spawned=mobs.map(m=>m.kind).join(',');
      // map tiles in the underworld
      await sleep(1500); out.explored=explored.size; const t=mapTile(Math.floor(x/CS),Math.floor(z/CS)); out.tileOk=!!t;
      return out; }""")
    print(json.dumps(r))
    pg.evaluate("()=>{ for(const m of mobs){ m.angry=0; } BEAST.daedra.aggro=0; BEAST.daedroth.aggro=0; BEAST.daedra.walk=0.0001; BEAST.daedroth.walk=0.0001; const a=mobs.find(m=>m.kind==='daedra'), b=mobs.find(m=>m.kind==='daedroth'); mobs.length=0; const x=Math.floor(player.x), z=Math.floor(player.z), y=Math.floor(player.y); const d=newBeast('daedra',x+5,y,z-1); const r=newBeast('daedroth',x+5,y,z+2); d.yaw=r.yaw=-Math.PI/2; d.idleT=r.idleT=999; mobs.push(d,r); let ba=0,bd=-9; for(let q=0;q<6.283;q+=0.02){ player.yaw=q; const v=camVectors().f; if(v[0]>bd){bd=v[0];ba=q;} } player.yaw=ba; player.pitch=0.05; }")
    pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/uw_daedra.png')
    pg.evaluate("()=>openMap()"); pg.wait_for_timeout(500); pg.screenshot(path='/tmp/uw_map.png')
    print(errs[:3]); b.close()
