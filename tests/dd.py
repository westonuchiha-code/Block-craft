from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','dd'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    res=pg.evaluate("""()=>{ const out=[]; tod=0.3; mobs.length=0; trySpawnOgre=function(){};
      const px=Math.floor(player.x)+2, pz=Math.floor(player.z)+14, gy=Math.floor(player.y)-1; window.T={px,pz,gy};
      for(let dx=-8;dx<=8;dx++) for(let dz=-8;dz<=8;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      inv[doorId(1,0,0,0)]=20; HOTBAR[0]=doorId(1,0,0,0); HOTBAR[1]=0; sel=0;
      const YAW=[0,Math.PI/2,Math.PI,-Math.PI/2], DIR=[[0,-1],[1,0],[0,1],[-1,0]];
      for(let f=0;f<4;f++) for(const order of [0,1]){
        // clear, then place two doors side by side while facing direction f; order 0 = left one first, 1 = right one first
        for(let dx=-6;dx<=6;dx++) for(let dz=-6;dz<=6;dz++) for(let y=gy+1;y<gy+4;y++) setB(px+dx,y,pz+dz,AIR);
        const d=DIR[f], right=DIR[(f+1)&3];
        const cells=[[px+d[0]*3, pz+d[1]*3],[px+d[0]*3+right[0], pz+d[1]*3+right[1]]];     // [left, right] as seen by the player
        for(const k of (order?[1,0]:[0,1])){ const c=cells[k];
          player.x=c[0]+0.5-d[0]*2.2; player.z=c[1]+0.5-d[1]*2.2; player.y=gy+1; player.yaw=YAW[f]; player.pitch=-0.62; placeBlock(); }
        const L=getB(cells[0][0],gy+1,cells[0][1]), Rr=getB(cells[1][0],gy+1,cells[1][1]);
        const ok = IS_DOOR[L] && IS_DOOR[Rr] && SH_FACE[L]===f && SH_FACE[Rr]===f;
        // hinge sides: left door must hinge on its left (away from the right door), right door on its right
        const boxEdge=b=>{ if(!SH_BOXES[b]) return '-'; const B=SH_BOXES[b][0]; return B[2]>0.5?'S':B[3]<0.5?'W':B[5]<0.5?'N':'E'; };
        // open the left one: both must open
        player.x=cells[0][0]+0.5-d[0]*2.2; player.z=cells[0][1]+0.5-d[1]*2.2; sel=1; player.pitch=-0.3; placeBlock(); sel=0;
        const L2=getB(cells[0][0],gy+1,cells[0][1]), R2=getB(cells[1][0],gy+1,cells[1][1]);
        out.push({f, order, ok, mirL:SH_MIR[L], mirR:SH_MIR[Rr], openL:SH_OPEN[L2], openR:SH_OPEN[R2], edgeL:boxEdge(L2), edgeR:boxEdge(R2)});
      }
      return out; }""")
    for r in res: print(r)
    # picture: a pair, closed then open, facing north
    pg.evaluate("""()=>{ const {px,pz,gy}=T; for(let dx=-6;dx<=6;dx++) for(let dz=-6;dz<=6;dz++) for(let y=gy+1;y<gy+4;y++) setB(px+dx,y,pz+dz,AIR);
      for(let dx=-3;dx<=4;dx++) for(let y=1;y<=3;y++) if(!((dx===0||dx===1)&&y<=2)) setB(px+dx,gy+y,pz-4,PLANKS);
      for(const dx of [0,1]){ player.x=px+dx+0.5; player.z=pz-1.3; player.y=gy+1; player.yaw=0; player.pitch=-0.5; placeBlock(); }
      player.x=px+1; player.z=pz+0.5; player.pitch=-0.05; }""")
    pg.wait_for_timeout(700); pg.screenshot(path='/tmp/dd1.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("()=>{ toggleDoor(T.px,T.gy+1,T.pz-5); player.z=T.pz-1.5; player.pitch=-0.15; }"); pg.wait_for_timeout(700); pg.screenshot(path='/tmp/dd2.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(errs); b.close()
