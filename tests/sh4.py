from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','sh4'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const out={};
      const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1;
      for(let dx=-8;dx<=8;dx++) for(let dz=-14;dz<=2;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=-0.5; player.vy=0;
      const S=slabId(0,0), ST=stairId(4,0,0); inv[S]=10; inv[ST]=10; inv[COBBLE]=5;
      HOTBAR[0]=S; HOTBAR[1]=ST; sel=0;
      let t=target(); out.t1=t&&[t.x-px,t.y-gy,t.z-pz,t.ny];
      placeBlock();
      let cell=null; for(let dz=-6;dz<=0;dz++){ const b=getB(px,gy+1,pz+dz); if(b>=256) cell=[px,gy+1,pz+dz,b]; }
      out.slab=cell&&[cell[2]-pz,cell[3]];
      // aim down on top of the slab from above: merge into planks
      player.x=cell[0]+0.5; player.z=cell[2]+0.5; player.y=gy+2.5; player.pitch=-1.5;
      t=target(); out.t2=t&&[t.x-px,t.y-gy,t.z-pz,t.ny,t.b];
      placeBlock(); out.merged=getB(cell[0],cell[1],cell[2])===PLANKS;
      // stair facing: look east and place on ground
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=Math.PI/2; player.pitch=-0.6; sel=1;
      placeBlock(); let st=null; for(let dx=0;dx<=6;dx++){ const b=getB(px+dx,gy+1,pz); if(IS_STAIR[b]) st=[dx,b,SH_FACE[b],SH_HALF[b]]; } out.stair=st;
      // break stair, check drop type
      const nd=itemDrops.length; 
      return out; }"""))
    # break via punch repeatedly
    print(pg.evaluate("""()=>{ const out={}; const n0=itemDrops.length; HOTBAR[2]=0; sel=2;
      for(let i=0;i<40;i++){ punch(); }
      out.drops=itemDrops.map(d=>d.id); return out; }"""))
    print(errs); b.close()
