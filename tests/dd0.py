from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(e.stack))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','dd'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    print(pg.evaluate("""()=>{ try{ const px=Math.floor(player.x), pz=Math.floor(player.z)+14, gy=Math.floor(player.y)-1;
      for(let dx=-8;dx<=8;dx++) for(let dz=-8;dz<=8;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      inv[doorId(1,0,0,0)]=20; HOTBAR[0]=doorId(1,0,0,0); sel=0; player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=-0.5;
      const t=target(); placeBlock(); return [t&&[t.x-px,t.y-gy,t.z-pz,t.b], inv[doorId(1,0,0,0)]]; }catch(e){ return e.stack; } }"""))
    pg.wait_for_timeout(500); print(errs[:2]); b.close()
