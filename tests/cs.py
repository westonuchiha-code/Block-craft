from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','cs'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    r=pg.evaluate("""()=>{ paused=false; update=function(){};
      const X=Math.floor(player.x)+4, Z=Math.floor(player.z)+6, Y=Math.floor(player.y)+8; const out={};
      for(let dx=-4;dx<=4;dx++) for(let dz=-4;dz<=4;dz++) for(let y=Y-1;y<=Y+3;y++) setB(X+dx,y,Z+dz,y===Y-1?STONE:AIR);
      const st=(dx,dz,f)=>setB(X+dx,Y,Z+dz,stairId(4,0,f));
      const desc=(dx,dz)=>{ const q=getB(X+dx,Y,Z+dz); return IS_STAIR[q] ? [SH_FACE[q],SH_CV[q]] : null; };
      // outer corner: stair facing N at (0,0), then stair facing E at (0,1)?? (south of it) -> facing-N stair has E-facing stair BEHIND? behind = north
      st(0,0,0); st(0,-1,1);            // N-facing, with an E-facing stair on its north (behind): outer
      out.outer=desc(0,0);
      st(2,0,0); st(2,1,1);             // N-facing, E-facing stair in front (south): inner
      out.inner=desc(2,0);
      st(-2,0,0); st(-2,-1,3);          // W-facing behind: outer other side
      out.outerL=desc(-2,0);
      out.straight=(st(0,3,0), desc(0,3));
      setB(X,Y,Z-1,AIR); out.afterBreak=desc(0,0);   // behind removed: back to straight
      out.boxes=[SH_BOXES[cornerId(4,0,0,0)].length, SH_BOXES[cornerId(4,0,0,2)].length];
      out.maxId=cornerId(10,1,3,3);
      window.P={X,Y,Z}; player.x=X+0.5; player.z=Z+5; player.y=Y+1; lastPCX=null; updateChunks(); player.yaw=3.14; player.pitch=-0.5;
      return out; }""")
    print(r)
    pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/cs.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("[WK.on, WK.err||null]"), errs); b.close()
