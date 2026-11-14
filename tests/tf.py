from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':780}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','tf'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    r=pg.evaluate("""()=>{
      const out={};
      // find a tree near spawn
      let T=null; for(let rx=-60;rx<=60&&!T;rx++)for(let rz=-60;rz<=60;rz++){ if(h3(rx,0,rz,SEED+99)>=0.055) continue; const t=rootTree(rx,rz); if(t){ T=t; break; } }
      const bt=buildTree(T.sp,T.shape,T.x,T.y,T.z); const lid=LOG_IDS[T.sp];
      for(const [X,Y,Z] of bt.logs) getB(X,Y,Z);           // load chunks
      const logs=bt.logs.map(([X,Y,Z])=>[X,Y,Z]); const ys=logs.map(l=>l[1]); const minY=Math.min(...ys), maxY=Math.max(...ys);
      const colx=T.x, colz=T.z; const trunk=[]; for(let y=minY;y<=maxY;y++) if(getB(colx,y,colz)===lid) trunk.push(y);
      out.trunkBefore=[trunk[0],trunk[trunk.length-1],trunk.length];
      // chop the bottom log
      breakNow({x:colx,y:trunk[0],z:colz,b:lid}, null);
      out.queued=treeFalls.length;
      for(let i=0;i<80;i++) updateTreeFalls(0.05);
      const after=[]; for(let y=minY-1;y<=maxY+1;y++) if(getB(colx,y,colz)===lid) after.push(y);
      out.trunkAfter=[after[0],after[after.length-1],after.length];
      out.left=treeFalls.length;
      // a player-built tower of logs: must NOT cascade
      const bx=colx+20, bz=colz+20, gy=colInfo(bx,bz).h+1; getB(bx,gy,bz);
      for(let k=0;k<5;k++) setB(bx,gy+k,bz,lid);
      breakNow({x:bx,y:gy,z:bz,b:lid}, null); out.towerQueued=treeFalls.length;
      for(let i=0;i<40;i++) updateTreeFalls(0.05);
      let tw=0; for(let k=0;k<5;k++) if(getB(bx,gy+k,bz)===lid) tw++; out.towerLogsStill=[tw, getB(bx,gy+1,bz)===lid];
      return out; }""")
    print(r,errs); b.close()
