from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','pf'); pg.fill('#newSeed','5151'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ classPick='warrior'; confirmClass(); paused=true; }")
    r=pg.evaluate("""()=>{ const out={}; let base=60;
      const gen=(tag)=>{ chunks.clear && 0; let t=performance.now(); let n=0; for(let cx=base;cx<base+8;cx++)for(let cz=base;cz<base+8;cz++){ getChunk(cx,cz); n++; } out[tag]=+((performance.now()-t)/n).toFixed(2); base+=10; };
      gen('full');
      const cb=cryptBlock; window.cryptBlock=()=>-1; gen('noCrypt'); window.cryptBlock=cb;
      const ra=roadAt, sa=signAt, nr=nearRoad; window.roadAt=()=>false; window.signAt=()=>null; window.nearRoad=()=>false; gen('noRoads'); window.roadAt=ra; window.signAt=sa; window.nearRoad=nr;
      window.cryptBlock=()=>-1; window.roadAt=()=>false; window.signAt=()=>null; window.nearRoad=()=>false; gen('neither');
      return out; }""")
    print(json.dumps(r), errs[:2]); b.close()
