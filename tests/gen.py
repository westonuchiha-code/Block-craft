from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page()
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','mb'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    print(pg.evaluate("""()=>{ paused=true; const o={};
      let t=performance.now(); for(let i=0;i<20;i++) genChunk(100+i,100); o.gen=(performance.now()-t)/20;
      const c=getChunk(0,0); t=performance.now(); for(let i=0;i<50;i++) computeDerived(c); o.derived=(performance.now()-t)/50;
      t=performance.now(); for(let i=0;i<30;i++) update(); o.update=(performance.now()-t)/30;
      t=performance.now(); for(let i=0;i<30;i++) updateHotbar(); o.hotbar=(performance.now()-t)/30;
      t=performance.now(); for(let i=0;i<30;i++) updateItemName(performance.now()); o.itemName=(performance.now()-t)/30;
      t=performance.now(); for(let i=0;i<30;i++) updateMobs(); o.mobs=(performance.now()-t)/30;
      // frame pacing while walking: per-frame times
      return o; }"""))
    pg.evaluate("()=>{ paused=false; window.__ft=[]; const f0=frame; let last=performance.now(); const of=update; update=function(){ const t=performance.now(); of(); window.__ut=(window.__ut||0)+performance.now()-t; }; const orr=render; render=function(){ const t=performance.now(); orr(); __ft.push(performance.now()-t); }; }")
    pg.keyboard.down('w'); pg.wait_for_timeout(8000); pg.keyboard.up('w')
    print(pg.evaluate("()=>{ const a=__ft.slice().sort((x,y)=>x-y); return {n:a.length, med:a[a.length>>1], p95:a[Math.floor(a.length*0.95)], max:a[a.length-1], updAvg:__ut/a.length}; }"))
    b.close()
