from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','sh3'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{
      const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1;
      for(let dx=-8;dx<=8;dx++) for(let dz=-14;dz<=2;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      for(let k=0;k<4;k++){ for(let h=0;h<k;h++) setB(px,gy+1+h,pz-3-k,COBBLE); setB(px,gy+1+k,pz-3-k,stairId(4,0,0)); }
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=0; player.vy=0;
      window.T={px,pz,gy};
      return [px,pz,gy,getB(px,gy+1,pz-3),collides(px+0.5,gy+1,pz-3+0.5), collides(px+0.5,gy+1,pz-2.5)]; }"""))
    for i in range(6):
        pg.keyboard.down('w'); pg.wait_for_timeout(600)
        print(pg.evaluate("[player.x.toFixed(2),player.y.toFixed(2),player.z.toFixed(2),onGroundLast]"))
    pg.keyboard.up('w')
    print(errs)
    b.close()
