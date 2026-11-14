from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','door'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const o={}; tod=0.3;
      const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1; window.T={px,pz,gy};
      for(let dx=-8;dx<=8;dx++) for(let dz=-14;dz<=2;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      // wall with a doorway at z=pz-4
      for(let dx=-3;dx<=3;dx++) for(let y=1;y<=3;y++) if(!(dx===0&&y<=2)) setB(px+dx,gy+y,pz-4,PLANKS);
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=-0.25; player.vy=0;
      const D=doorId(1,0,0,0), G=gateId(1,0,0); inv[D]=3; inv[G]=3; inv[fenceId(1,0)]=5; HOTBAR[0]=D; HOTBAR[1]=G; sel=0;
      // aim at the ground inside the doorway
      player.pitch=-0.42; let t=target(); o.t=t&&[t.x-px,t.y-gy,t.z-pz,t.ny];
      placeBlock(); o.door=[getB(px,gy+1,pz-4)-DOOR0, getB(px,gy+2,pz-4)-DOOR0];
      // fence row with a gate to the right
      setB(px+3,gy+1,pz-2,fenceId(1,0)); setB(px+5,gy+1,pz-2,fenceId(1,0)); setB(px+4,gy+1,pz-2,gateId(1,0,0));
      o.fm=[getB(px+3,gy+1,pz-2)-FENCE0-16, getB(px+5,gy+1,pz-2)-FENCE0-16];
      return o; }"""))
    pg.wait_for_timeout(700); pg.screenshot(path='/tmp/door1.png',clip={'x':0,'y':60,'width':390,'height':330})
    # walk into closed door
    pg.keyboard.down('w'); pg.wait_for_timeout(1800); pg.keyboard.up('w')
    print('closed walk z', pg.evaluate("player.z-T.pz"))
    print(pg.evaluate("""()=>{ const {px,pz,gy}=T; const o={}; player.z=pz+0.5; player.pitch=-0.2; sel=2; HOTBAR[2]=0;
      placeBlock(); o.open=[getB(px,gy+1,pz-4)-DOOR0, getB(px,gy+2,pz-4)-DOOR0]; toggleDoor(px+4,gy+1,pz-2); o.gate=getB(px+4,gy+1,pz-2)-GATE0; return o; }"""))
    pg.wait_for_timeout(500); pg.screenshot(path='/tmp/door2.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.keyboard.down('w'); pg.wait_for_timeout(2200); pg.keyboard.up('w')
    print('open walk z', pg.evaluate("player.z-T.pz"))
    print(pg.evaluate("""()=>{ const {px,pz,gy}=T; const o={}; 
      // gate walk-through check by collision
      o.gateOpenPass=!collides(px+4.5,gy+1,pz-1.5); toggleDoor(px+4,gy+1,pz-2); o.gateClosedBlock=collides(px+4.5,gy+1,pz-1.5);
      // break the door top half
      breakNow({x:px,y:gy+2,z:pz-4,b:getB(px,gy+2,pz-4)},0); o.left=[getB(px,gy+1,pz-4),getB(px,gy+2,pz-4)]; o.drops=itemDrops.map(d=>d.id-DOOR0);
      o.rec=RECIPES.filter(r=>/door|gate/.test(r.name)).length; o.ic=[iconSrc(doorId(0,0,0,0)).width,iconSrc(gateId(0,0,0)).width];
      return o; }"""), errs)
    b.close()
