from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780})
    pg=ctx.new_page()
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','mb'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    print(pg.evaluate("""()=>{ paused=true; const o={};
      const pcx=Math.floor(player.x/16), pcz=Math.floor(player.z/16);
      let t=performance.now(), s=0;
      for(let r=0;r<10;r++) for(let i=0;i<369000;i++){ const c=getChunk(pcx+(i&3), pcz+((i>>2)&1)); s+=c.cx; }
      o.alt=(performance.now()-t)/10;
      t=performance.now();
      for(let r=0;r<10;r++) for(let i=0;i<369000;i++){ const c=getChunk(pcx, pcz); s+=c.cx; }
      o.same=(performance.now()-t)/10;
      t=performance.now();
      for(let r=0;r<10;r++) for(let i=0;i<369000;i++){ s+=getB(pcx*16+(i&63), 20, pcz*16+((i>>6)&15)); }
      o.getB=(performance.now()-t)/10;
      t=performance.now(); for(let i=0;i<10;i++) render(); o.render=(performance.now()-t)/10;
      return o; }"""))
    b.close()
