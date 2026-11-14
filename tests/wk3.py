from playwright.sync_api import sync_playwright
CMP="""async ()=>{
  const wait=async()=>{ const f=WK.frames||0; for(let i=0;i<400 && (WK.frames||0)<f+3;i++) await new Promise(r=>setTimeout(r,25)); };
  await wait();
  const a=new Uint8ClampedArray(img.data);
  const on=WK.on; WK.on=false; R_Y0=0; R_STEP=1; render(); WK.on=on;
  const out=[]; for(let i=0;i<a.length;i+=4) if(a[i]!==img.data[i]||a[i+1]!==img.data[i+1]||a[i+2]!==img.data[i+2]){ const px=(i/4)%RW, py=Math.floor(i/4/RW);
    out.push([px,py,[a[i],a[i+1],a[i+2]],[img.data[i],img.data[i+1],img.data[i+2]], depthBuf[py*RW+px].toFixed(2)]); }
  return out.slice(0,12);
}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page()
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','wk'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    pg.evaluate("()=>{ const t=performance.now(); performance.now=()=>t; update=function(){}; tod=0.2; }")
    pg.evaluate("""()=>{ const px=Math.floor(player.x), pz=Math.floor(player.z), y=Math.floor(player.y);
      mobs.push(newRat(px+1,y,pz-3)); mobs.push(newCat(px-1,y,pz-3)); const n=newNpc(px,y,pz-4, npcGenerate(Math.random,'guard')); mobs.push(n);
      camMode=1; player.pitch=-0.2; }""")
    for r in pg.evaluate(CMP): print(r)
    b.close()
