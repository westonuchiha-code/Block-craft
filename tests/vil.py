from playwright.sync_api import sync_playwright
import sys
seed=sys.argv[1] if len(sys.argv)>1 else '12345'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','vil'); pg.fill('#newSeed',seed); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    r=pg.evaluate("""()=>{ const o={gen:worldGen}; let t=performance.now(); const v=villageAt(0,0); o.ms=performance.now()-t;
      let cnt=0; for(let rx=-3;rx<=3;rx++) for(let rz=-3;rz<=3;rz++) if(villageAt(rx,rz)) cnt++; o.of49=cnt;
      if(!v) return o; o.c=[v.cx,v.cz,v.g]; o.houses=v.houses.map(h=>h.job); o.rects=v.rects.length; let n=0; for(const a of v.cells.values()) n+=a.length/2; o.blocks=n;
      player.x=v.cx+0.5; player.z=v.cz+9.5; lastPCX=null; updateChunks(); player.y=v.g+1; player.yaw=0; player.pitch=0.05; tod=0.2; window.V=v; return o; }""")
    print(r, errs)
    if 'c' in r:
        pg.wait_for_timeout(2500); pg.screenshot(path='/tmp/vil1.png',clip={'x':0,'y':60,'width':390,'height':330})
        for i,(yaw) in enumerate([1.57,3.14,4.71]):
            pg.evaluate("y=>{ player.yaw=y; player.x=V.cx+0.5-Math.sin(y)*9; player.z=V.cz+0.5+Math.cos(y)*9; }",yaw); pg.wait_for_timeout(1200); pg.screenshot(path='/tmp/vil%d.png'%(i+2),clip={'x':0,'y':60,'width':390,'height':330})
        # overhead view
        pg.evaluate("()=>{ player.x=V.cx+0.5; player.z=V.cz+30.5; player.y=V.g+26; player.yaw=0; player.pitch=-0.75; update=function(){}; }"); pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/vil5.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(errs); b.close()
