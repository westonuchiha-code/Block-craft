from playwright.sync_api import sync_playwright
import json, sys
# People in the world: ground shadows, legs that match the ground covered, turning that takes time, bodies that take up room,
# and standing on slabs at the slab's real height.
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1100,'height':560}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','gait'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(5000)
    r=pg.evaluate("""async ()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; tod=0.3; mobs.length=0; const o={}; const sleep=t=>new Promise(r=>setTimeout(r,t));
      let F=null; for(let x=-200;x<200&&!F;x+=5) for(let z=-200;z<200&&!F;z+=5){ const c=colInfo(x,z); if(c.top!==GRASS||c.open||c.h<=SEA+2||nearVillage(x,z)) continue; let ok=true; for(let a=-8;a<=8&&ok;a+=2) for(let b=-8;b<=8;b+=2){ const q=colInfo(x+a,z+b); if(q.h!==c.h||q.top!==GRASS){ ok=false; break; } } if(ok) F=[x,z,c.h]; }
      const [x,z,h]=F; player.x=x+0.5; player.z=z+12.5; player.y=h+1; lastPCX=null; updateChunks(); await sleep(3000);
      for(let i=-8;i<=8;i++) for(let j=-8;j<=8;j++) for(let k=h+1;k<h+5;k++) setB(x+i,k,z+j,AIR);
      trySpawnNpcs=function(){}; const m=newNpc(x-6,h+1,z); m.idleT=999; m.state='idle'; mobs.push(m);
      // 1. shadows: a list entry for the villager, darkest at the feet, none far away, and the picture really is darker there
      camSetup(); buildShadows(); o.shadowAtFeet=+shadowAt(m.x,m.y,m.z).toFixed(2); o.shadowFar=shadowAt(m.x+3,m.y,m.z);
      // 2. a stroll: speed, and the legs keep pace with the ground (one full swing cycle per 2.7 x sin(swing) blocks)
      const path=[]; for(let i=-5;i<=6;i++) path.push([x+i,h+1,z]); ratSetPath(m,path); m.state='wander'; const x0=m.x, g0=m.gait||0, t0=performance.now();
      let maxLag=0; for(let i=0;i<40 && m.x<x+5.5;i++){ await sleep(100); let d=m.yaw-m.vyaw; d=Math.abs(Math.atan2(Math.sin(d),Math.cos(d))); if(d>maxLag) maxLag=d; }
      const dist=m.x-x0, secs=(performance.now()-t0)/1000; o.speed=+(dist/secs).toFixed(2); o.cyclesPerBlock=+(((m.gait-g0)/6.2832)/dist).toFixed(3); o.expected=+(1/(2.7*Math.sin(m.gaitA))).toFixed(3); o.swing=+m.gaitA.toFixed(2);
      // 3. turning takes time: told to face the other way, the body is part-way there a moment later
      m.path=null; m.state='idle'; m.idleT=999; m.yaw=m.vyaw+3; await sleep(60); let d1=m.yaw-m.vyaw; d1=Math.abs(Math.atan2(Math.sin(d1),Math.cos(d1))); await sleep(900); let d2=m.yaw-m.vyaw; d2=Math.abs(Math.atan2(Math.sin(d2),Math.cos(d2))); o.turn=[+d1.toFixed(2), +d2.toFixed(2)];
      // 4. bodies take up room: stand on the villager and they step aside
      player.x=m.x+0.05; player.z=m.z; player.y=m.y; await sleep(1200); o.apart=+Math.hypot(player.x-m.x,player.z-m.z).toFixed(2);
      // 5. on a slab they stand on the slab, not half a block above it
      player.x=x+0.5; player.z=z+12.5; for(let i=0;i<=2;i++) setB(x+i,h+1,z+3,slabId(6,0)); const n=newNpc(x-2,h+1,z+3); n.idleT=999; mobs.push(n); ratSetPath(n,[[x-1,h+1,z+3],[x,h+2,z+3],[x+1,h+2,z+3]]); n.state='wander';
      for(let i=0;i<50 && Math.abs(n.x-(x+1.5))>0.1;i++) await sleep(100); o.onSlab=+(n.y-(h+1)).toFixed(2); o.standY=standY(x+1,h+2,z+3)-(h+1);
      return o; }""")
    print(json.dumps(r)); print(errs)
    ok=(r['shadowAtFeet']<=0.5 and r['shadowFar']==1 and 1.4<=r['speed']<=2.3 and abs(r['cyclesPerBlock']-r['expected'])<0.12*r['expected'] and r['swing']<0.6
        and r['turn'][0]>0.6 and r['turn'][1]<0.2 and r['apart']>=0.55 and abs(r['onSlab']-0.5)<0.05 and r['standY']==0.5)
    if not ok: bad.append('gait')
    b.close()
print('GAIT TEST FAILED', bad) if bad else print('people ok')
sys.exit(1 if (bad or errs) else 0)
