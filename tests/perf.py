from playwright.sync_api import sync_playwright
import json
files=['before_woolbloom','before_travel','before_crypts','blockcraft_prototype']
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for f in files:
        pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(f'file:///home/claude/{f}.html'); pg.wait_for_timeout(1500)
        pg.fill('#newName','pf'); pg.fill('#newSeed','5151'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
        pg.evaluate("()=>{ const cm=document.getElementById('classMenu'); if(cm&&cm.classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
        r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={};
          // chunk generation, a fresh area
          let t=performance.now(); let n=0; for(let cx=60;cx<72;cx++)for(let cz=60;cz<72;cz++){ getChunk(cx,cz); n++; } out.genMs=+((performance.now()-t)/n).toFixed(2);
          // frame cost: time update() and renderFrame() separately for 3 seconds
          let up=0, rf=0, k=0; const U=update, R=renderFrame;
          window.update=function(){ const a=performance.now(); U(); up+=performance.now()-a; };
          window.renderFrame=function(){ const a=performance.now(); R(); rf+=performance.now()-a; k++; };
          await sleep(4000);
          out.frames=k; out.updateMs=+(up/Math.max(1,k)).toFixed(2); out.renderMs=+(rf/Math.max(1,k)).toFixed(2); out.mobs=mobs.length;
          return out; }""")
        print(f, json.dumps(r), errs[:2])
    b.close()
