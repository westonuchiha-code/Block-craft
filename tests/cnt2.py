from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','cnt'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    print(pg.evaluate("""()=>{ tod=0.2; player.pitch=-0.1; paused=true;
      const o={}; const C={};
      for(const n of ['getB','getTopP','getLightAt','biomeCol','cast','waterHas','plantHit','texColor','getChunk','shapedHit','isLeafHole','skyPixel','cloudHit']){
        const f=window[n]; C[n]=0; window[n]=function(){ C[n]++; return f.apply(this,arguments); }; }
      for(let i=0;i<5;i++) render();
      for(const k in C) C[k]=Math.round(C[k]/5);
      return C; }"""), errs)
    b.close()
