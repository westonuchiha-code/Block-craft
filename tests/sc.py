from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','sc'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const o={}; tod=0.3;
      const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1;
      for(let dx=-8;dx<=8;dx++) for(let dz=-14;dz<=2;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      const ids=[STONE_BRICK,MOSSY_BRICK,FLAGSTONE,PILLAR,CARVED,CUTTER,FURNACE];
      ids.forEach((id,i)=>{ setB(px-3+i,gy+1,pz-5,id); });
      for(let i=0;i<4;i++){ setB(px-3+i,gy+2,pz-5, i<2? slabId(6,0): stairId(7,0,i)); }
      setB(px+2,gy+2,pz-5,stairId(6,1,0));
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=-0.15; player.vy=0;
      o.ids=[slabId(6,0),stairId(7,1,3),slabId(7,1)]; o.nm=[NAMES[slabId(6,0)],NAMES[stairId(7,0,0)]];
      inv[STONE]=10; inv[STONE_BRICK]=2; inv[LEAVES]=2; inv[PLANKS]=5;
      openCraft(3,'cut'); o.n=visibleRecipes().length; craftRecipe(CUT_RECIPES[0]); o.brick=inv[STONE_BRICK];
      craftRecipe(CUT_RECIPES[5]); o.slab=inv[slabId(5,0)]; craftRecipe(CUT_RECIPES[4]); o.moss=inv[MOSSY_BRICK];
      o.cutterRecipe=RECIPES.some(r=>r.out[0]===CUTTER);
      closeCraft&&closeCraft(); craftOpen=false; document.getElementById('craftMenu').classList.remove('show');
      return o; }"""))
    pg.wait_for_timeout(800); pg.screenshot(path='/tmp/sc1.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("()=>{ inv[STONE]=5; openCraft(3,'cut'); craftSel=6; renderCraft(); }")
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/sc2.png',clip={'x':0,'y':250,'width':390,'height':260}); print(errs); b.close()
