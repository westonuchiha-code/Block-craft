from playwright.sync_api import sync_playwright
import sys
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    for seed in sys.argv[1:] or ['12345']:
        pg.evaluate("openMenu&&openMenu()")
        pg.fill('#newName','v'+seed); pg.fill('#newSeed',seed); pg.click('#newBtn'); pg.wait_for_timeout(1500)
        print(seed, pg.evaluate("""()=>{ paused=true; const res=[];
          for(let rx=-2;rx<=2;rx++) for(let rz=-2;rz<=2;rz++){ const v=villageAt(rx,rz); if(!v) continue;
            // make sure chunks exist
            const solid=(x,y,z)=>{ const b=getB(x,y,z); return b!==AIR && !PASS[b]; };
            const free=(x,y,z)=>{ const b=getB(x,y,z); return PASS[b] && !IS_WATER[b] || IS_DOOR[b] || IS_GATE[b]; };
            const stand=(x,y,z)=>solid(x,y-1,z) && free(x,y,z) && free(x,y+1,z);
            let okc=0;
            for(const h of v.houses){
              const start=h.out, seen=new Set([start.join(',')]), q=[start]; let found=false;
              while(q.length && !found && seen.size<6000){ const [x,y,z]=q.shift();
                if(Math.abs(x-v.cx)<=3 && Math.abs(z-v.cz)<=3){ found=true; break; }
                for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]]) for(const dy of [0,1,-1]){ const nx=x+dx, ny=y+dy, nz=z+dz, k=nx+','+ny+','+nz;
                  if(seen.has(k) || Math.hypot(nx-v.cx,nz-v.cz)>48) continue; if(stand(nx,ny,nz)){ seen.add(k); q.push([nx,ny,nz]); break; } } }
              if(found) okc++;
            }
            res.push([rx,rz,v.houses.length,okc]);
          } return res; }"""), errs)
    b.close()
