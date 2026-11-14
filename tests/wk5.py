from playwright.sync_api import sync_playwright
CMP="""async ()=>{
  const t=performance.now(); performance.now=()=>t; update=function(){}; const raf=requestAnimationFrame; window.requestAnimationFrame=cb=>raf(()=>cb(t));
  const wait=async()=>{ const f=WK.frames||0; for(let i=0;i<400 && (WK.frames||0)<f+3;i++) await new Promise(r=>setTimeout(r,25)); };
  await wait();
  const a=new Uint8ClampedArray(img.data);
  const on=WK.on; WK.on=false; R_Y0=0; R_STEP=1; render(); WK.on=on;
  let diff=0; for(let i=0;i<a.length;i++) if(a[i]!==img.data[i]) diff++;
  return [diff, WK.on, WK.err||null, SEED];
}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','a'); pg.fill('#newSeed','111'); pg.click('#newBtn'); pg.wait_for_timeout(2500); pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.evaluate("()=>{ setB(Math.floor(player.x),Math.floor(player.y)+3,Math.floor(player.z)-2,GLOW); saveWorld(); openMenu(); }"); pg.wait_for_timeout(500)
    pg.fill('#newName','b'); pg.fill('#newSeed','222'); pg.click('#newBtn'); pg.wait_for_timeout(2500); pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.keyboard.down('w'); pg.wait_for_timeout(3000); pg.keyboard.up('w')
    print('world b', pg.evaluate(CMP), errs)
    b.close()
