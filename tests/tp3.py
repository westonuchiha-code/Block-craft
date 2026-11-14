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
    pg.fill('#newName','tp'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    pg.evaluate("()=>{ tod=0.25; mobs.length=0; trySpawnOgre=function(){}; inv[STONE_SWORD]=1; inv[STONE_PICK]=1; inv[PISTOL]=1; inv[CROSSBOW]=1; inv[PLANKS]=5; HOTBAR[0]=STONE_SWORD; HOTBAR[1]=STONE_PICK; HOTBAR[2]=PISTOL; HOTBAR[3]=CROSSBOW; HOTBAR[4]=PLANKS; sel=0; camMode=2; player.pitch=0; }")
    for i,n in enumerate(['sword','pick','pistol','xbow','block']):
        pg.evaluate("i=>{ sel=i; }",i); pg.wait_for_timeout(700); pg.screenshot(path='/tmp/tp_%s.png'%n,clip={'x':110,'y':120,'width':170,'height':200})
    pg.evaluate("()=>{ camMode=1; sel=0; player.pitch=-0.25; }"); pg.wait_for_timeout(700); pg.screenshot(path='/tmp/tp_back.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("()=>{ const t=performance.now(); performance.now=()=>t; update=function(){}; const raf=requestAnimationFrame; window.requestAnimationFrame=cb=>raf(()=>cb(t)); }")
    print('held item, workers vs single:', pg.evaluate(CMP), errs)
    b.close()
