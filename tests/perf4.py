from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','pf'); pg.fill('#newSeed','5151'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ classPick='warrior'; confirmClass(); }")
    print(pg.evaluate("""()=>{ const out={}; let t=performance.now(); for(let i=0;i<5;i++) saveWorld(); out.base=+((performance.now()-t)/5).toFixed(1);
      for(let i=0;i<30000;i++) placedAdd(i%300, 20+(i/300|0)%40, i/12000|0); for(let i=0;i<8000;i++) explored.add((i%90)+','+(i/90|0));
      t=performance.now(); for(let i=0;i<5;i++) saveWorld(); out.big=+((performance.now()-t)/5).toFixed(1); out.metaKB=Math.round(localStorage.getItem(wkey(currentWorld,'world')).length/1024); const p1=JSON.stringify(packPlaced()); placedMap=unpackPlaced(JSON.parse(p1)); out.roundtrip=JSON.stringify(packPlaced())===p1 && placedDel(5,20,0); return out; }"""))
    print(errs); b.close()
