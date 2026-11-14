from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','og'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    print(pg.evaluate("""()=>{ tod=0.25; mobs.length=0; trySpawnOgre=function(){};
      const px=Math.floor(player.x), pz=Math.floor(player.z)+30, gy=Math.floor(player.y)-1; window.T={px,pz,gy};
      for(let dx=-14;dx<=14;dx++) for(let dz=-34;dz<=4;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+12;y++) setB(px+dx,y,pz+dz,AIR); }
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=0.12;
      const m=newOgre(px,gy+1,pz-11); m.yaw=Math.PI; m.idleT=99; mobs.push(m); window.m=m;
      const n=newNpc(px+3,gy+1,pz-11, npcGenerate(Math.random,'guard')); n.yaw=3.14; mobs.push(n);
      return [m.hp, ogreGround(m.x,m.z,m.y)]; }"""), errs)
    pg.wait_for_timeout(900); pg.screenshot(path='/tmp/og1.png',clip={'x':0,'y':60,'width':390,'height':330})
    print('calm', pg.evaluate("[m.hostile, m.x-T.px, m.z-T.pz]"))
    # shoot it -> hostile, chases
    pg.evaluate("()=>{ inv[PISTOL]=1; HOTBAR[0]=PISTOL; sel=0; punch(); }"); pg.wait_for_timeout(1300)
    print('shot', pg.evaluate("[m.hp, m.hostile, (m.z-T.pz).toFixed(1), health]")); pg.screenshot(path='/tmp/og2.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.wait_for_timeout(2200); pg.screenshot(path='/tmp/og3.png',clip={'x':0,'y':60,'width':390,'height':330})
    print('close', pg.evaluate("[(Math.hypot(m.x-player.x,m.z-player.z)).toFixed(1), health, dead, WK.on, WK.err||null]"))
    pg.wait_for_timeout(2500)
    print('later', pg.evaluate("[health, dead, m.hp]"), errs)
    print(pg.evaluate("""()=>{ if(dead) return 'dead'; for(let i=0;i<20;i++){ m.iframe=0; mobHit(m,8); } return [m.dead, itemDrops.length]; }"""))
    b.close()
