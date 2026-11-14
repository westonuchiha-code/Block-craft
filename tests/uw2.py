from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','uw'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ mobs.length=0; trySpawnOgre=function(){};
      const px=Math.floor(player.x)+3, pz=Math.floor(player.z)+12, gy=Math.floor(player.y)-1; window.T={px,pz,gy};
      for(let dx=-4;dx<=5;dx++) for(let dz=-4;dz<=4;dz++){ setB(px+dx,gy,pz+dz,STONE_BRICK); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      for(let i=-1;i<=2;i++) for(let j=0;j<=4;j++) if(i===-1||i===2||j===0||j===4) setB(px+i,gy+j,pz-2,GATE);
      const lit=lightGate(px-1,gy+2,pz-2); player.x=px+1; player.z=pz-1.5; player.y=gy+1; return lit; }"""))
    pg.wait_for_timeout(2600)
    print('down:', pg.evaluate("[isUnder(player.z), portalLock, health, [Math.floor(player.x),Math.floor(player.y),Math.floor(player.z)-UNDER_Z]]")); 
    pg.evaluate("()=>{ window.G=[player.x,player.y,player.z]; player.z+=1.2; }"); pg.wait_for_timeout(400)
    print('stepped out, lock:', pg.evaluate("portalLock"))
    pg.evaluate("()=>{ player.x=G[0]; player.y=G[1]; player.z=G[2]; }"); pg.wait_for_timeout(2800)
    print('up:', pg.evaluate("[isUnder(player.z), Math.round(player.x-T.px), Math.round(player.y-T.gy), Math.round(player.z-T.pz), health, mobs.length]"), errs)
    # save, reload, the underworld gate must still be there
    print(pg.evaluate("""()=>{ saveWorld(); const id=currentWorld; openMenu(); loadWorld(id); const g=G.map(Math.floor); return [IS_PORTAL[getB(g[0],g[1],g[2])], getB(T.px,T.gy+1,T.pz-2)===PORTAL0]; }"""))
    # vista: fly up in the underworld
    pg.evaluate("()=>{ paused=false; update=function(){}; player.x=G[0]; player.z=G[2]+6; player.y=52; lastPCX=null; updateChunks(); player.yaw=0.6; player.pitch=-0.25; }")
    for i,yaw in enumerate([0.6,2.2,3.8,5.4]):
        pg.evaluate("y=>{ player.yaw=y; }",yaw); pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/uv%d.png'%i,clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("[WK.on, WK.err||null]"), errs); b.close()
