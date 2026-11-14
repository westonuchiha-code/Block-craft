from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','bed'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const o={}; tod=0.3;
      const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1;
      for(let dx=-8;dx<=8;dx++) for(let dz=-14;dz<=2;dz++){ setB(px+dx,gy,pz+dz,PLANKS); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=-0.45; player.vy=0;
      inv[PLANKS]=6; inv[LITTER]=3; craftMode='craft';
      const r=RECIPES.find(r=>r.out[0]===BED0); o.can=canCraft(r); craftRecipe(r); o.bed=inv[BED0]; o.litter=inv[LITTER]||0;
      HOTBAR[0]=BED0; sel=0; placeBlock();
      o.cells=[]; for(let dz=-6;dz<=0;dz++){ const b=getB(px,gy+1,pz+dz); if(IS_BED[b]) o.cells.push([dz,b-BED0]); }
      o.inv=inv[BED0];
      // a second bed sideways for the picture
      setB(px+2,gy+1,pz-3,BED0+2); setB(px+3,gy+1,pz-3,BED0+3);
      window.T={px,pz,gy};
      return o; }"""))
    pg.wait_for_timeout(800); pg.screenshot(path='/tmp/bed1.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("""()=>{ const o={}; const {px,pz,gy}=T; sel=1; HOTBAR[1]=0;
      placeBlock(); o.dayMsg=document.getElementById('sleepov').textContent; o.spawn=bedSpawn&&[bedSpawn[0]-px,bedSpawn[1]-gy,bedSpawn[2]-pz];
      tod=0.75; placeBlock(); o.nightMsg=document.getElementById('sleepov').textContent; return o; }"""))
    pg.wait_for_timeout(1800)
    print(pg.evaluate("""()=>{ const o={}; const {px,pz,gy}=T; o.tod=tod;
      player.x+=5; respawn(); o.resp=[player.x-px,player.y-gy,player.z-pz];
      // walk onto bed? break: punch head
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.pitch=-0.45;
      for(let i=0;i<20;i++) punch();
      o.left=[]; for(let dz=-6;dz<=0;dz++){ if(IS_BED[getB(px,gy+1,pz+dz)]) o.left.push(dz); }
      o.drops=itemDrops.map(d=>d.id); respawn(); o.spawnAfter=bedSpawn; 
      o.icons=[iconSrc(BED0).width, iconSrc(LITTER).width];
      return o; }"""), errs)
    pg.evaluate("()=>{ inv[LITTER]=4; inv[BED0]=1; inv[PLANKS]=3; openCraft(3); craftSel=visibleRecipes().findIndex(r=>r.out[0]===BED0); renderCraft(); }")
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/bed2.png',clip={'x':60,'y':285,'width':270,'height':210})
    b.close()
