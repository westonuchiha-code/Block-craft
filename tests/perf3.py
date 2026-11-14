from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','pf'); pg.fill('#newSeed','5151'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ classPick='warrior'; confirmClass(); }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); await sleep(3000);
      const names=['updateMobs','updateChunks','updateItems','updateSacks','fireTick','trySpawnNpcs','questTick','exploreTick','cryptTick','lavaFireTick','updateVitals','updateHotbar','skillMoveTick','updateTreeFalls','updateWbSeeds','updateWbPlants','trySpawnBeasts','trySpawnRats','trySpawnCats','trySpawnWb','scanCatnip','trySpawnOgre','updateEating','survivalTick','portalTick','updateFx','updateGuns','renderFrame','update','computeDerived','genChunk','updateBeast','updateNpc','updateCat','updateRat','ratPath','mpTick'];
      const T={}, C={};
      for(const n of names){ const f=window[n]; if(typeof f!=='function') continue; T[n]=0; C[n]=0; window[n]=function(...a){ const t=performance.now(); try{ return f.apply(this,a); } finally{ T[n]+=performance.now()-t; C[n]++; } }; }
      const t0=performance.now(); await sleep(5000); const el=performance.now()-t0;
      const out={}; for(const n in T) if(T[n]>1) out[n]=[+(T[n]/el*1000/60).toFixed(2)+'ms/frame', C[n]];
      return out; }""")
    for k,v in sorted(r.items(), key=lambda kv:-float(kv[1][0].split('ms')[0])): print(k, v)
    print(errs[:2]); b.close()
