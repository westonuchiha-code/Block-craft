from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','bd'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); beastSpawnT=1e9; ogreSpawnT=1e9; health=1000; player.x=-135.5; player.y=12; player.z=-235.5; await sleep(2500);
      const out={}; out.feet=NAMES[getB(-136,12,-236)]; out.head=NAMES[getB(-136,13,-236)]; out.below=NAMES[getB(-136,11,-236)]; out.pos=[player.x,player.y,player.z].map(v=>+v.toFixed(1));
      const orig=window.hurt; const calls=[]; window.hurt=function(p,pure){ calls.push([p,pure,new Error().stack.split('\\n')[2].trim().slice(0,90)]); return orig(p,pure); };
      await sleep(2000); out.calls=calls.slice(0,5); out.n=calls.length; out.mobs=mobs.map(m=>m.kind+':'+Math.round(Math.hypot(m.x-player.x,m.z-player.z))).join(','); out.air=typeof airT!=='undefined'?airT:null; return out; }""")
    print(json.dumps(r)); print(errs)
