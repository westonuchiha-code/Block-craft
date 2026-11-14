from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','fe'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const o={}; tod=0.3;
      const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1;
      for(let dx=-8;dx<=8;dx++) for(let dz=-14;dz<=2;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=-0.5; player.vy=0;
      inv[fenceId(1,0)]=20; HOTBAR[0]=fenceId(1,0); sel=0;
      // place by setB a row, an L, and wall join
      for(let dx=-3;dx<=1;dx++) setB(px+dx,gy+1,pz-5,fenceId(1,0));
      setB(px+1,gy+1,pz-6,fenceId(1,0)); setB(px+1,gy+1,pz-7,fenceId(1,0));
      setB(px+3,gy+1,pz-5,PLANKS);  // solid neighbor to the east of row end? row end at px+1, gap px+2
      setB(px+2,gy+1,pz-5,fenceId(1,0));
      o.masks=[-3,-2,1,2,3].map(dx=>getB(px+dx,gy+1,pz-5)-fenceId(1,0)*0-(FENCE0+16));
      // place with placeBlock where aiming
      let t=target(); o.t=t&&[t.x-px,t.z-pz,t.ny];
      placeBlock();
      o.placed=[]; for(let dz=-5;dz<=0;dz++){ const b=getB(px,gy+1,pz+dz); if(IS_FENCE[b]) o.placed.push([dz,b-FENCE0-16]); }
      // collision: can't walk through at head-height 1.2 above ground
      const gyy=gy+1; o.col=[collides(px+1.5,gyy,pz-4.5-1+0.0), collides(px+1.5,gyy+1.2,pz-4.5-1), collides(px+1.5,gyy+1.6,pz-5.5)];
      // break row end and see neighbor update
      setB(px+1,gy+1,pz-5,AIR); o.after=getB(px,gy+1,pz-5)-(FENCE0+16);
      return o; }"""))
    pg.evaluate("()=>{ const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y); setB(px+1,gy,pz-5,fenceId(1,0)); player.yaw=0.5; player.pitch=-0.15; }")
    pg.wait_for_timeout(800); pg.screenshot(path='/tmp/fe1.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("()=>{ const px=Math.floor(player.x), pz=Math.floor(player.z); player.x=px+0.5; player.z=pz-0.5; player.yaw=0; return 0}"))
    pg.keyboard.down('w'); pg.wait_for_timeout(2500); pg.keyboard.up('w')
    print(pg.evaluate("[player.x,player.y,player.z]"), errs)
    b.close()
