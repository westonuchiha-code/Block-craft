from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','cnt'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    print(pg.evaluate("""()=>{ tod=0.2; player.pitch=-0.1; paused=true;
      const o={}; const g0=genChunk; let gens=0; genChunk=function(a,b){ gens++; return g0(a,b); };
      const gc0=getChunk; let calls=0, miss=0; 
      getChunk=function(cx,cz){ calls++; if(!(cx===cacheCX&&cz===cacheCZ)) miss++; return gc0(cx,cz); };
      let t=performance.now(); for(let i=0;i<10;i++) render(); o.msPerRender=(performance.now()-t)/10;
      o.calls=calls/10; o.miss=miss/10; o.gens=gens; o.chunks=chunks.size; o.LOAD_R=LOAD_R;
      return o; }"""), errs)
    b.close()
