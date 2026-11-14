from playwright.sync_api import sync_playwright
import sys
f=sys.argv[1] if len(sys.argv)>1 else 'blockcraft_prototype.html'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780})
    pg=ctx.new_page()
    pg.goto('file:///home/claude/'+f); pg.wait_for_timeout(1000)
    pg.fill('#newName','mb'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    print(pg.evaluate("""()=>{ paused=true; const o={}; tod=0.2;
      const res=[];
      for(const [yaw,pitch] of [[0,-0.1],[1.5,0.2],[3,-0.6],[4.5,0.0]]){
        player.yaw=yaw; player.pitch=pitch;
        render(); let t=performance.now(); for(let i=0;i<8;i++) render(); const rt=(performance.now()-t)/8;
        const {f,r,u}=camVectors(); const ex=player.x, ey=player.y+1.6, ez=player.z, aspect=RW/RH;
        const W={len:0,t0:-1,top:false}; let hits=0;
        t=performance.now();
        for(let k=0;k<4;k++) for(let py=0;py<RH;py++){ const sy=1-(py+0.5)/RH*2; for(let px=0;px<RW;px++){ const sx=(px+0.5)/RW*2-1;
          let dx=f[0]+r[0]*sx*aspect*TAN+u[0]*sy*TAN, dy=f[1]+r[1]*sx*aspect*TAN+u[1]*sy*TAN, dz=f[2]+r[2]*sx*aspect*TAN+u[2]*sy*TAN; const l=Math.hypot(dx,dy,dz);
          const h=cast(ex,ey,ez,dx/l,dy/l,dz/l,VIEW_DIST,W,HIT_A); if(h) hits++; } }
        const ct=(performance.now()-t)/4;
        res.push([yaw,pitch,+rt.toFixed(1),+ct.toFixed(1),Math.round(hits/4/518.4)]);
      }
      return res; }"""))
    b.close()
