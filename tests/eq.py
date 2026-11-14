from playwright.sync_api import sync_playwright
JS="""()=>{ paused=true; tod=0.2; mobs.length=0;
  player.x=8.5; player.z=8.5; updateChunks(); let y=119; while(y>0 && PASS[getB(8,y,8)]) y--; player.y=y+1;
  const out=[];
  for(const [yaw,pitch] of [[0,-0.1],[1.5,0.2],[3,-0.6],[4.5,0.0],[2.2,0.9],[5.5,-1.2],[0.7,0.45]]){
    player.yaw=yaw; player.pitch=pitch;
    const {f,r,u}=camVectors(); const ex=player.x, ey=player.y+1.6, ez=player.z, aspect=RW/RH;
    const W={len:0,t0:-1,top:false}; let h1=0,h2=0,n=0;
    for(let py=0;py<RH;py++){ const sy=1-(py+0.5)/RH*2; for(let px=0;px<RW;px++){ const sx=(px+0.5)/RW*2-1;
      let dx=f[0]+r[0]*sx*aspect*TAN+u[0]*sy*TAN, dy=f[1]+r[1]*sx*aspect*TAN+u[1]*sy*TAN, dz=f[2]+r[2]*sx*aspect*TAN+u[2]*sy*TAN; const l=Math.hypot(dx,dy,dz);
      const h=cast(ex,ey,ez,dx/l,dy/l,dz/l,VIEW_DIST,W,HIT_A);
      const v = h ? (h.x*31+h.y*17+h.z*13+h.b*7+h.face+Math.round(h.t*1e6)) : -1;
      h1=(h1*33+v)%1000000007; h2=(h2*33+Math.round(W.len*1e6)+Math.round(W.t0*1e6)+(W.top?1:0))%1000000007; if(h) n++;
      // shadow-style ray without W
      const s=cast(ex,ey+20,ez,0.3,0.5,0.81,20,undefined,HIT_S); h1=(h1+(s?s.b:0))%1000000007;
    } }
    out.push([h1,h2,n]);
  }
  return out; }"""
res=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for f in ['before_perf.html','blockcraft_prototype.html']:
        ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file:///home/claude/'+f); pg.wait_for_timeout(1000)
        pg.fill('#newName','eq'); pg.fill('#newSeed','777'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
        res.append(pg.evaluate(JS)); print(f,res[-1],errs); ctx.close()
    b.close()
print('IDENTICAL' if res[0]==res[1] else 'DIFFERENT')
