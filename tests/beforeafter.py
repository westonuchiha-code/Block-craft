from playwright.sync_api import sync_playwright
from PIL import Image
import base64, io
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1920,'height':1080}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','ba'); pg.fill('#newSeed','12345'); pg.click('#newBtn', no_wait_after=True); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; ogreSpawnT=1e9; }")
    pg.evaluate("""()=>{ const v=nearestVillage(2); player.x=v.cx+0.5; player.z=v.cz+9.5; player.y=colInfo(v.cx,v.cz+9).h+1; player.yaw=-0.25; player.pitch=-0.06; tod=0.3; inv[IRON_PICK]=1; HOTBAR[0]=IRON_PICK; sel=0; updateHotbar(); }""")
    pg.wait_for_timeout(3000)
    pg.evaluate("""()=>{ const v=nearestVillage(2); const n=mobs.filter(m=>m.kind==='npc').slice(0,2); n.forEach((m,i)=>{ m.x=v.cx-1.5+i*2.2; m.z=v.cz+5.5; m.y=colInfo(Math.floor(m.x),Math.floor(m.z)).h+1; m.yaw=Math.PI; m.path=null; m.idleT=99; m.state='idle'; }); const keep=new Set(n); for(let i=mobs.length-1;i>=0;i--) if(!keep.has(mobs[i])) mobs.splice(i,1); paused=true; }""")
    pg.wait_for_timeout(500); print('state', pg.evaluate("()=>({paused, gpu:GPU.on, wk:WK.on, ok:GPU.ok})"), flush=True)
    # old renderer: one CPU frame, shown at the screen's size
    pg.evaluate("()=>{ GPU.on=false; WK.on=false; R_Y0=0; R_STEP=1; render(); }"); pg.wait_for_timeout(800)
    print('cpu rendered', flush=True); pg.screenshot(path='/tmp/ba_cpu.png', timeout=60000); print('cpu shot', flush=True)
    pg.evaluate("()=>{ gpuSet(true); GPU.frames=0; gpuRender(); renderOverlay(); }"); pg.wait_for_timeout(20000)
    pg.screenshot(path='/tmp/ba_gpu.png', timeout=280000)
    print(pg.evaluate("()=>({pic:GPU.size, overlay:[canvas.width,canvas.height]})"), errs)
a=Image.open('/tmp/ba_cpu.png'); g=Image.open('/tmp/ba_gpu.png')
box=(560,300,1360,760)
S=Image.new('RGB',(800*2+20,460),(0,0,0)); S.paste(a.crop(box),(0,0)); S.paste(g.crop(box),(820,0)); S.save('/home/claude/renderer_before_after_1080p.png')
g.save('/home/claude/gpu_fullhd_village.png')
