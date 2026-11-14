from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','npc'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    r=pg.evaluate("""()=>{
      tod=0.25; mobs.length=0; npcSpawnT=0; for(let i=0;i<30;i++){ npcSpawnT=0; trySpawnNpcs(); }
      const out={npcs:mobs.filter(m=>m.kind==='npc').map(m=>m.name+':'+m.job)};
      // line up one of each job in front of the player on flat ground
      mobs.length=0; const jobs=NPC_JOBS.map(j=>j.job);
      const px=Math.floor(player.x), pz=Math.floor(player.z);
      // clear a flat platform
      const gy=Math.floor(player.y)-1;
      for(let dx=-6;dx<=6;dx++) for(let dz=-14;dz<=0;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+6;y++) setB(px+dx,y,pz+dz,AIR); }
      jobs.forEach((j,i)=>{ const n=newNpc(px-4+(i%5)*2, gy+1, pz-5-Math.floor(i/5)*3, npcGenerate(Math.random,j)); n.yaw=Math.PI; n.hx=Math.floor(n.x); n.hz=Math.floor(n.z); n.state='idle'; n.idleT=999; mobs.push(n); });
      player.pitch=-0.05; player.yaw=0; tod=0.25;
      return out; }""")
    print(r)
    pg.wait_for_timeout(1500)
    pg.screenshot(path='/tmp/npc_line.png',clip={'x':0,'y':60,'width':390,'height':330})
    # walking NPC
    pg.evaluate("""()=>{ for(const m of mobs){ m.idleT=0; m.state='idle'; } }""")
    pg.wait_for_timeout(2500)
    pg.screenshot(path='/tmp/npc_w2.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("mobs.filter(m=>m.kind==='npc').map(m=>[m.job,m.moving,Math.round(m.limb*10)/10])"), errs)
    b.close()
