from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','wt'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    pg.evaluate("""()=>{ tod=0.25; update=function(){}; const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1;
      for(let dx=-6;dx<=6;dx++) for(let dz=-14;dz<=1;dz++){ for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); setB(px+dx,gy,pz+dz, dz<-5?WATER:GRASS); setB(px+dx,gy-1,pz+dz,SAND); setB(px+dx,gy-2,pz+dz,SAND); if(dz<-5) setB(px+dx,gy-1,pz+dz,WATER); }
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=-0.12; mobs.length=0;
      const a=newNpc(px-1,gy+1,pz-3, npcGenerate(Math.random,'cleric')); a.yaw=3.14; mobs.push(a);      // on the shore, water behind
      const b2=newNpc(px+2,gy-1,pz-7, npcGenerate(Math.random,'guard')); mobs.push(b2);                  // standing in the water
      mobs.push(newCat(px+1,gy+1,pz-4)); }""")
    pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/wt.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("[NPCS_IN_WORLD, WK.on, WK.err||null]"), errs); b.close()
