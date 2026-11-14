from playwright.sync_api import sync_playwright
import sys
seed=sys.argv[1] if len(sys.argv)>1 else '12345'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','vil'); pg.fill('#newSeed',seed); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    r=pg.evaluate("""()=>{ let v=null; for(let rx=0;rx<4&&!v;rx++) for(let rz=0;rz<4&&!v;rz++) v=villageAt(rx,rz); window.V=v; update=function(){}; tod=0.22; mobs.length=0;
      return v&&{c:[v.cx,v.cz,v.g], houses:v.houses.map(h=>h.job)}; }""")
    print(r, errs)
    n=len(r['houses'])
    for i in range(min(n,4)):
        pg.evaluate("""i=>{ const h=V.houses[i]; const dx=h.out[0]-h.door[0], dz=h.out[2]-h.door[2];
          player.x=h.out[0]+0.5+dx*6; player.z=h.out[2]+0.5+dz*6; lastPCX=null; updateChunks(); let y=110; while(y>0&&PASS[getB(Math.floor(player.x),y,Math.floor(player.z))]) y--; player.y=y+1;
          player.yaw=Math.atan2(-dx,dz); player.pitch=0.12; }""", i)
        pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/h%d.png'%i,clip={'x':0,'y':60,'width':390,'height':330})
    # inside house 0
    pg.evaluate("""()=>{ const h=V.houses[0]; const dx=h.out[0]-h.door[0], dz=h.out[2]-h.door[2]; player.x=h.inside[0]+0.5; player.z=h.inside[2]+0.5; player.y=h.inside[1]; player.yaw=Math.atan2(-dx,dz); player.pitch=-0.1; tod=0.75; }""")
    pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/hin.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("()=>{ tod=0.22; player.x=V.cx+0.5; player.z=V.cz+34.5; player.y=V.g+30; player.yaw=0; player.pitch=-0.75; }"); pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/vtop.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(errs); b.close()
