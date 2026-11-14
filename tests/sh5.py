from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','sh5'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const o={}; o.d=[DROP[301]===300, DROP[257]===256, canHarvest(301,0), canHarvest(stairId(4,0,0),0), HARD[301]];
      const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1;
      for(let dx=-3;dx<=3;dx++) for(let dz=-8;dz<=0;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+5;y++) setB(px+dx,y,pz+dz,AIR); }
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=-0.3;
      setB(px,gy+1,pz-3,stairId(0,0,1)); player.pitch=-0.25; sel=3; HOTBAR[3]=0;
      let t=target(); o.t=t&&[t.b,t.x-px,t.z-pz];
      for(let i=0;i<30;i++) punch(); o.after=getB(px,gy+1,pz-3); o.drops=itemDrops.map(d=>d.id);
      const ic=[256,268,300,315].map(i=>iconSrc(i).width); o.ic=ic;
      return o; }"""), errs)
    b.close()
