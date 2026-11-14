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
    pg.fill('#newName','wk'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("[Math.round(player.x),Math.round(player.z), !!nearestVillage(2)]"))
    pg.evaluate("()=>{ const t=performance.now(); performance.now=()=>t; update=function(){}; tod=0.75; const raf=requestAnimationFrame; window.requestAnimationFrame=cb=>raf(()=>cb(t)); }")
    print('village night', pg.evaluate(CMP))
    print('lantern edit', pg.evaluate("""()=>{ const x=Math.floor(player.x/16)*16, z=Math.floor(player.z), y=Math.floor(player.y); setB(x,y+1,z-2,LANTERN0+1); setB(x-1,y+1,z-3,GLOW);
       const o=[getLightAt(x-3,y+1,z-2), getLightAt(x+3,y+1,z-2)]; window.__o=o; return 1; }""") and pg.evaluate(CMP), pg.evaluate("__o"))
    print('remove', pg.evaluate("""()=>{ const x=Math.floor(player.x/16)*16, z=Math.floor(player.z), y=Math.floor(player.y); setB(x,y+1,z-2,AIR); setB(x-1,y+1,z-3,AIR); window.__o=[getLightAt(x-3,y+1,z-2), getLightAt(x+3,y+1,z-2)]; return 1; }""") and pg.evaluate(CMP), pg.evaluate("__o"))
    pg.screenshot(path='/tmp/wk7.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(errs); b.close()
