from playwright.sync_api import sync_playwright
import sys
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    for seed in sys.argv[1:] or ['12345']:
        pg.evaluate("openMenu&&openMenu()"); pg.fill('#newName','s'+seed); pg.fill('#newSeed',seed); pg.click('#newBtn'); pg.wait_for_timeout(1500)
        print(seed, pg.evaluate("""()=>{ paused=true; const out=[];
          for(let rx=-2;rx<=2;rx++) for(let rz=-2;rz<=2;rz++){ const v=villageAt(rx,rz); if(!v||!v.sewer) continue; const S=v.sewer;
            const stand=(x,y,z)=>!collides(x+0.5,y+0.01,z+0.5) && collides(x+0.5,y-0.2,z+0.5);
            const start=[S.hut[0]-1,S.hut[1],S.hut[2]]; if(!stand(...start)){ out.push([rx,rz,'no landing']); continue; }
            const seen=new Set([start.join(',')]), q=[start]; let goalT=false, goalR=0; const goal=[v.cx+7, S.Fs+1, v.cz+1];
            while(q.length && seen.size<20000){ const [x,y,z]=q.shift();
              if(x===goal[0]&&z===goal[2]&&Math.abs(y-goal[1])<0.1) goalT=true;
              for(const r of S.rooms) if(Math.abs(x+0.5-r.x)<1 && Math.abs(z+0.5-r.z)<1 && !r.hit){ r.hit=true; goalR++; }
              for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]]) for(const dy of [0,0.5,-0.5,-1]){ const n=[x+dx,y+dy,z+dz], k=n.join(',');
                if(seen.has(k)||Math.abs(n[0]-v.cx)>45||Math.abs(n[2]-v.cz)>45||n[1]>S.hut[1]+0.1) continue; if(stand(...n)){ seen.add(k); q.push(n); } } }
            // also the way back up: from the tunnel to the landing, climbing only half steps
            const seen2=new Set([goal.join(',')]), q2=[goal]; let up=false;
            while(q2.length && seen2.size<20000){ const [x,y,z]=q2.shift(); if(x===start[0]&&z===start[2]&&Math.abs(y-start[1])<0.1){ up=true; break; }
              for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]]) for(const dy of [0,0.5,-0.5]){ const n=[x+dx,y+dy,z+dz], k=n.join(',');
                if(seen2.has(k)||Math.abs(n[0]-v.cx)>45||Math.abs(n[2]-v.cz)>45) continue; if(stand(...n)){ seen2.add(k); q2.push(n); } } }
            out.push([rx,rz,'down:'+goalT,'up:'+up,'rooms '+goalR+'/'+S.rooms.length,'arms '+S.arms.join(',')]);
          } return out; }"""), errs)
    b.close()
