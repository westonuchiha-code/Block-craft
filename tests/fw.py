from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','fw'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const o={}; tod=0.3;
      const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1;
      for(let dx=-8;dx<=8;dx++) for(let dz=-14;dz<=2;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      // small house: 5x5 planks wall ring, roof, with windows in front wall (z=pz-6 line)
      for(let dx=-2;dx<=2;dx++) for(let dz=-8;dz<=-4;dz++) for(let y=1;y<=3;y++){
        const edge=(dx===-2||dx===2||dz===-8||dz===-4); if(edge) setB(px+dx,gy+y,pz+dz,PLANKS);
      }
      for(let dx=-2;dx<=2;dx++) for(let dz=-8;dz<=-4;dz++) setB(px+dx,gy+4,pz+dz,PLANKS);
      setB(px,gy+1,pz-4,AIR); setB(px,gy+2,pz-4,AIR);
      setB(px-1,gy+2,pz-4,WIN0); setB(px+1,gy+2,pz-4,WIN0+2);
      setB(px+2,gy+2,pz-6,WIN0+1); setB(px-2,gy+2,pz-6,WIN0+3);
      setB(px+3,gy+1,pz-2,FURNACE);
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0.5; player.pitch=-0.05; player.vy=0;
      o.names=[NAMES[WIN0],NAMES[WIN0+2],NAMES[FURNACE]];
      // furnace menu
      inv[SAND]=8; inv[COAL_ITEM]=2; inv[COBBLE]=10;
      return o; }"""))
    pg.wait_for_timeout(900)
    pg.screenshot(path='/tmp/fw1.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("""()=>{ const o={};
      openCraft(3,'smelt'); o.n=visibleRecipes().length;
      const r=SMELT_RECIPES[0]; craftRecipe(r); o.glass=inv[GLASS]; o.sand=inv[SAND]; o.coal=inv[COAL_ITEM];
      craftRecipe(SMELT_RECIPES[1]); o.stone=inv[STONE];
      closeCraft&&closeCraft();
      craftMode='craft'; const w=RECIPES.find(r=>r.name.startsWith('Window')); craftRecipe(w); o.win=inv[WIN0];
      return o; }"""))
    pg.wait_for_timeout(300)
    pg.screenshot(path='/tmp/fw2.png')
    # place a window in front
    print(pg.evaluate("""()=>{ const o={}; const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y);
      HOTBAR[0]=WIN0; sel=0; player.yaw=0; player.pitch=-0.6; 
      placeBlock(); o.cells=[]; for(let dz=-5;dz<=0;dz++){ const b=getB(px,gy,pz+dz); if(b>=316) o.cells.push([dz,b]); }
      o.inv=inv[WIN0]; return o; }"""), errs)
    b.close()
