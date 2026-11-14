from playwright.sync_api import sync_playwright
CMP="""async ()=>{
  const wait=async()=>{ const f=WK.frames||0; for(let i=0;i<400 && (WK.frames||0)<f+3;i++) await new Promise(r=>setTimeout(r,25)); };
  await wait();
  const a=new Uint8ClampedArray(img.data), da=new Float32Array(depthBuf);
  const on=WK.on; WK.on=false; R_Y0=0; R_STEP=1; render(); WK.on=on;
  let diff=0, dd=0; for(let i=0;i<a.length;i++) if(a[i]!==img.data[i]) diff++; for(let i=0;i<da.length;i++) if(da[i]!==depthBuf[i]) dd++;
  return [diff, dd, WK.on, WK.err||null];
}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','wk'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    # freeze the clock and the world
    pg.evaluate("()=>{ const t=performance.now(); performance.now=()=>t; update=function(){}; tod=0.2; const raf=requestAnimationFrame; window.requestAnimationFrame=cb=>raf(()=>cb(t)); }")
    print('plain', pg.evaluate(CMP))
    print('mobs+3rd', pg.evaluate("""async ()=>{ const px=Math.floor(player.x), pz=Math.floor(player.z), y=Math.floor(player.y);
      mobs.push(newRat(px+1,y,pz-3)); mobs.push(newCat(px-1,y,pz-3)); const n=newNpc(px,y,pz-4, npcGenerate(Math.random,'guard')); mobs.push(n);
      camMode=1; player.pitch=-0.2; return 1; }""") and pg.evaluate(CMP))
    print('edits', pg.evaluate("""()=>{ const px=Math.floor(player.x), pz=Math.floor(player.z), y=Math.floor(player.y); camMode=0;
      for(let i=-2;i<=2;i++){ setB(px+i,y+1,pz-3,FRAME_X); setB(px+i,y,pz-3,stairId(8,0,0)); } setB(px,y+2,pz-2,LANTERN0+1); setB(px+1,y,pz-2,doorId(0,0,0,0)); setB(px-1,y,pz-2,WIN0); setB(px+2,y,pz-2,WATER); return 1; }""") and pg.evaluate(CMP))
    print('teleport', pg.evaluate("()=>{ player.x+=200; player.z-=130; lastPCX=null; updateChunks(); let y=119; while(y>0&&PASS[getB(Math.floor(player.x),y,Math.floor(player.z))]) y--; player.y=y+1; player.yaw=2; return 1; }") and pg.evaluate(CMP))
    print('night', pg.evaluate("()=>{ tod=0.7; player.pitch=0.4; return 1; }") and pg.evaluate(CMP))
    print(errs); b.close()
