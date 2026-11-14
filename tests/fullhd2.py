from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1920,'height':1080}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hd'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; ogreSpawnT=1e9; }")
    pg.evaluate("""()=>{ const v=nearestVillage(2); player.x=v.cx+0.5; player.z=v.cz+7.5; player.y=colInfo(v.cx,v.cz+7).h+1; player.yaw=0; player.pitch=-0.08; tod=0.3; inv[IRON_SWORD]=1; HOTBAR[0]=IRON_SWORD; sel=0; updateHotbar(); }""")
    pg.wait_for_timeout(2500)
    pg.evaluate("""()=>{ const v=nearestVillage(2); const n=mobs.filter(m=>m.kind==='npc').slice(0,3); n.forEach((m,i)=>{ m.x=v.cx-1+i*1.4; m.z=v.cz+3.5; m.y=colInfo(Math.floor(m.x),Math.floor(m.z)).h; m.path=null; m.idleT=99; }); const keep=new Set(n); for(let i=mobs.length-1;i>=0;i--) if(!keep.has(mobs[i])) mobs.splice(i,1);
       const b=newBeast('bear', v.cx+3.5, colInfo(v.cx+3,v.cz+2).h+1, v.cz+2.5); b.idleT=999; BEAST.bear._ag=BEAST.bear.aggro; BEAST.bear.aggro=0; mobs.push(b); gpuSet(true); }""")
    pg.wait_for_timeout(1000)
    pg.evaluate("()=>{ paused=true; GPU.frames=0; gpuRender(); renderOverlay(); }"); pg.wait_for_timeout(1500)
    pg.screenshot(path='/tmp/gpu_village_1080.png', timeout=120000)
    pg.evaluate("()=>{ camMode=2; player.pitch=0.25; for(let k=0;k<4;k++){ const id=AR(4,k); inv[id]=1; equipArmor(id); } gpuRender(); renderOverlay(); }"); pg.wait_for_timeout(1500)
    pg.screenshot(path='/tmp/gpu_third_1080.png', timeout=120000)
    t=pg.evaluate("()=>{ const t0=performance.now(); gpuRender(); GPU.gl.finish(); return performance.now()-t0; }"); print('one 1080p frame on the software GPU, ms:', round(t))
    print(pg.evaluate("()=>({gpu:GPU.on, pic:[GPU.cv.width,GPU.cv.height], overlay:[canvas.width,canvas.height], err:GPU.err, frames:GPU.frames})"), errs)
    pg.evaluate("()=>gpuSet(false)")
