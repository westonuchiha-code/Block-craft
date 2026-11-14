from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','vl2'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000); pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.evaluate("""async ()=>{ let V=null; for(let a=-1;a<=1&&!V;a++)for(let c=-1;c<=1&&!V;c++){ const v=villageAt(a,c); if(v)V=v; }
      const vc=villageCentre(V); player.x=vc[0]; player.z=vc[1]; player.y=colInfo(Math.floor(vc[0]),Math.floor(vc[1])).h+2; tod=0.3; beastSpawnT=1e9; }""")
    pg.wait_for_timeout(9000)
    pg.evaluate("""()=>{ const n=mobs.filter(m=>m.kind==='npc'); const m=n[0]; const f=()=>{ const dx=m.x-player.x, dz=m.z-player.z; let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.03){ player.yaw=a; const v=camVectors().f; const d=(v[0]*dx+v[2]*dz)/Math.hypot(dx,dz); if(d>bd){bd=d;ba=a;} } player.yaw=ba; player.pitch=0; }; f(); }""")
    pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/vl_a.png')
    print(errs[:3]); b.close()
