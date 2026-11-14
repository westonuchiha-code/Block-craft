from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','bb'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const o={}; tod=0.3;
      const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1; window.T={px,pz,gy};
      for(let dx=-10;dx<=10;dx++) for(let dz=-16;dz<=2;dz++){ setB(px+dx,gy,pz+dz,dz>-3&&Math.abs(dx)<2?PATH:GRASS); for(let y=gy+1;y<gy+12;y++) setB(px+dx,y,pz+dz,AIR); }
      const S=(x,y,z,b)=>setB(px+x,gy+y,pz+z,b);
      // sample house 7 wide (x -3..3), 5 deep (z -10..-6), walls 3 high
      for(let x=-3;x<=3;x++) for(let z=-10;z<=-6;z++){ S(x,0,z,FLAGSTONE);
        const edge=x===-3||x===3||z===-10||z===-6, corner=(x===-3||x===3)&&(z===-10||z===-6);
        for(let y=1;y<=3;y++) if(edge) S(x,y,z, corner?BEAM : y===1?STONE_BRICK : (x+z)%3===0?FRAME_X:(x+z)%3===1?FRAME:FRAME_D1); }
      S(0,1,-6,doorId(2,0,0,0)); S(0,2,-6,doorId(2,0,0,1)); S(-2,2,-6,WIN0+2); S(2,2,-6,WIN0+2);
      // gable roof along x: stairs rising from z=-11 (facing S tall side = +z => facing 2) and z=-5 (facing N)
      for(let x=-4;x<=4;x++){ for(let k=0;k<3;k++){ S(x,4+k,-11+k,stairId(8,0,2)); S(x,4+k,-5-k,stairId(8,0,0)); } S(x,7,-8,slabId(8,0)); S(x,6,-8,SHINGLE);}
      for(const x of [-3,3]){ for(let y=4;y<=6;y++) for(let z=-10+(y-4);z<=-6-(y-4);z++) if(getB(px+x,gy+y,pz+z)===AIR) S(x,y,z,PLASTER); }
      // samples row
      [PLASTER,FRAME,FRAME_X,FRAME_D1,FRAME_D2,BEAM,SHINGLE,SLATE,THATCH,HAY,BOOKSHELF,HEDGE].forEach((id,i)=>S(-6+i,1,-3,id));
      S(5,1,-4,fenceId(2,0)); S(5,2,-4,fenceId(2,0)); S(5,3,-4,LANTERN0+1);
      S(-5,3,-4,PLANKS); S(-5,2,-4,LANTERN0);
      S(-6,2,-3,stairId(10,0,0)); S(-5,2,-3,slabId(9,0)); S(1,2,-3,stairId(9,0,1));
      player.x=px+0.5; player.z=pz+2.5; player.y=gy+1; player.yaw=0; player.pitch=0.05; player.vy=0;
      o.light=getLightAt(px+5,gy+2,pz-3);
      inv[SAND]=2; inv[GRAVEL]=2; inv[33]=2; inv[STICK]=5; craftMode='craft';
      craftRecipe(RECIPES.find(r=>r.name==='Plaster')); craftRecipe(RECIPES.find(r=>r.name==='Hedge')); o.made=[inv[PLASTER],inv[HEDGE],inv[33]];
      o.hard=[HARD[stairId(8,0,0)],KIND[stairId(9,0,0)],REQ_TIER[slabId(9,0)],HARD[doorId(1,0,0,0)],HAND_OK.has(fenceId(3,0)),HARD[slabId(3,0)]];
      o.nm=[NAMES[stairId(8,0,0)],NAMES[slabId(10,1)]];
      return o; }"""), errs)
    pg.wait_for_timeout(900); pg.screenshot(path='/tmp/bb1.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("()=>{ tod=0.75; player.z=T.pz-1.5; player.pitch=0.1; }"); pg.wait_for_timeout(900); pg.screenshot(path='/tmp/bb2.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(errs); b.close()
