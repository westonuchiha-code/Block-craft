from playwright.sync_api import sync_playwright
CMP="""async ()=>{
  const wait=async()=>{ const f=WK.frames||0; for(let i=0;i<400 && (WK.frames||0)<f+3;i++) await new Promise(r=>setTimeout(r,25)); };
  await wait();
  const a=new Uint8ClampedArray(img.data);
  const on=WK.on; WK.on=false; R_Y0=0; R_STEP=1; render(); WK.on=on;
  let diff=0; for(let i=0;i<a.length;i++) if(a[i]!==img.data[i]) diff++;
  return [diff, WK.on, WK.err||null];
}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','og'); pg.fill('#newSeed','777'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    print(pg.evaluate("""()=>{ let n=0, tries=0; const R=Math.random; const spots=[];
      for(let k=0;k<40;k++){ player.x=(R()-0.5)*1200; player.z=(R()-0.5)*1200; lastPCX=null; updateChunks(); 
        for(let i=0;i<9;i++){ tries++; mobs.length=0; trySpawnOgre(); if(mobs.length){ n++; break; } } }
      return [n,'of 40 places got one within 9 spawn ticks (3 minutes)']; }"""))
    pg.evaluate("()=>{ const t=performance.now(); performance.now=()=>t; update=function(){}; tod=0.3; const raf=requestAnimationFrame; window.requestAnimationFrame=cb=>raf(()=>cb(t)); const v=nearestVillage(2); player.x=v.cx+0.5; player.z=v.cz+5.5; player.y=v.g+1; lastPCX=null; updateChunks(); player.yaw=0; player.pitch=0.1; mobs.length=0; const m=newOgre(v.cx,v.g+1,v.cz-9); m.yaw=2.6; m.pose.ra=-1.4; m.pose.c=Math.cos(2.6); m.pose.s=Math.sin(2.6); mobs.push(m); }")
    print('ogre in village, workers vs single', pg.evaluate(CMP), errs)
    pg.screenshot(path='/tmp/og4.png',clip={'x':0,'y':60,'width':390,'height':330})
    b.close()
