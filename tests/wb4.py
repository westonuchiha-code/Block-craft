from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':780,'height':390}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','wb4'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    r=pg.evaluate("""()=>{ const out={};
      let X=null; for(let x=-300;x<300&&!X;x+=2)for(let z=-300;z<300;z+=2){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+2){ X=[x,z,c.h]; break; } }
      const [x,z,h]=X; getB(x,h,z); player.x=x+.5; player.z=z+.5; player.y=h+1; wbSpawnT=9999; mobs.length=0;
      for(let k=h+1;k<h+8;k++) for(let a=-3;a<=3;a++)for(let c=-3;c<=3;c++) setB(x+a,k,z+c,AIR);
      // a seed released above grass
      wbSeeds.push({x:x+2.5,y:h+3,z:z+2.5,vx:0,vz:0,dx:0,dz:0,ph:0,rot:0,age:0});
      for(let i=0;i<400;i++) updateWbSeeds(0.05);
      out.seedLeft=wbSeeds.length;
      // run many seeds so at least one plants (60% chance each)
      for(let n=0;n<12;n++) wbSeeds.push({x:x-2.5+n*0.1,y:h+3,z:z-2.5,vx:0,vz:0,dx:0,dz:0,ph:n,rot:0,age:0});
      for(let i=0;i<400;i++) updateWbSeeds(0.05);
      let planted=[]; for(let a=-8;a<=8;a++)for(let c=-8;c<=8;c++){ if(getB(x+a,h+1,z+c)===WBP0) planted.push([x+a,h+1,z+c]); }
      out.planted=planted.length; out.reg=wbPlants.size;
      const [px,py,pz]=planted[0]||[x,h+1,z]; if(!planted.length) setB(px,py,pz,WBP0);
      // growth: force timers
      const stages=[]; for(let i=0;i<4;i++){ const e=wbPlants.get(px+','+py+','+pz); if(e) e.t=0; updateWbPlants(0.01); stages.push(getB(px,py,pz)-WBP0); } out.stages=stages;
      // harvest
      const before=itemDrops.length; wbHarvest(px,py,pz); out.afterHarvest=getB(px,py,pz)-WBP0; out.woolDrops=itemDrops.length-before;
      for(let i=0;i<2;i++){ const e=wbPlants.get(px+','+py+','+pz); if(e) e.t=0; updateWbPlants(0.01); } out.regrown=getB(px,py,pz)-WBP0;
      // break ripe plant: wool + sprout
      const b2=itemDrops.length; breakNow({x:px,y:py,z:pz,b:WBP0+2}, null); out.breakDrops=itemDrops.length-b2; out.afterBreak=getB(px,py,pz);
      // ground removed pops sprout
      setB(px,py,pz,WBP0+1); setB(px,py-1,pz,DIRT); setB(px,py-1,pz,STONE); const e2=wbPlants.get(px+','+py+','+pz); if(e2) e2.t=0; updateWbPlants(0.01); out.poppedWhenNoGround=getB(px,py,pz);
      out.icon=blockIcon(WBP0+2)?1:0; out.names=[NAMES[WBP0],NAMES[WBP0+2]];
      return out; }""")
    print(r,errs); b.close()
