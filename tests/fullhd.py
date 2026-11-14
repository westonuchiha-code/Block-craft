from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1920,'height':1080}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hd'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; ogreSpawnT=1e9; }")
    pg.evaluate("""()=>{ mobs.length=0; let L=null; for(let x=-400;x<400&&!L;x+=6) for(let z=-400;z<400;z+=6){ const c=colInfo(x,z); if(c.h<SEA-4 && getB(x,SEA,z)!==AIR){ L=[x,z]; break; } }
       let X=null; for(let x=-200;x<200&&!X;x+=7) for(let z=-200;z<200;z+=7){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+3&&!nearVillage(x,z)){ X=[x,z]; break; } }
       player.x=X[0]+0.5; player.z=X[1]+0.5; player.y=colInfo(X[0],X[1]).h+1; player.yaw=0.7; player.pitch=-0.12; tod=0.3; inv[IRON_PICK]=1; HOTBAR[0]=IRON_PICK; sel=0; updateHotbar(); }""")
    pg.wait_for_timeout(3000)
    pg.evaluate("()=>{ mobs.length=0; }"); pg.wait_for_timeout(500)
    pg.screenshot(path='/tmp/cpu_1080.png')
    print('cpu', pg.evaluate("()=>({RW,RH})"))
    pg.evaluate("()=>{ gpuSet(true); }"); pg.wait_for_timeout(6000)
    pg.evaluate("()=>{ mobs.length=0; }"); pg.wait_for_timeout(2500)
    pg.screenshot(path='/tmp/gpu_1080.png')
    print('gpu', pg.evaluate("()=>({on:GPU.on, size:[GPU.cv.width,GPU.cv.height], err:GPU.err, frames:GPU.frames})"), errs)
    pg.evaluate("()=>gpuSet(false)")
