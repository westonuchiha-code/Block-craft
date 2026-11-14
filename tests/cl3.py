from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':780,'height':390}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','cl3'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    r=pg.evaluate("""()=>{ let best=null;
      for(let x=-500;x<=500&&!best;x+=5)for(let z=-500;z<=500;z+=5){ const c=colInfo(x,z); if(c.steep&&c.top===STONE&&c.h>50&&c.h<80){ best=[x,z,c.h]; break; } }
      if(!best) return null; const [x,z,h]=best; player.x=x+.5; player.z=z+.5; player.y=h+2; player.pitch=-0.3; player.yaw=0.8; return best; }""")
    print(r,errs); pg.wait_for_timeout(6000); pg.screenshot(path='/tmp/cl3.png'); b.close()
