from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','fl'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    pg.evaluate("""()=>{ player.pitch=-0.25; const px=Math.floor(player.x), pz=Math.floor(player.z), yy=Math.floor(player.y);
      for(let i=0;i<11;i++){ const x=px+(i%4)*1-1, z=pz-2-Math.floor(i/4)*1; let y=yy+3; while(y>0 && getB(x,y,z)===AIR) y--; if(getB(x,y,z)!==AIR && IS_PLANT[getB(x,y+1,z)]!==1) setB(x,y+1,z,FLOWER0+i); } }""")
    pg.wait_for_timeout(800); pg.screenshot(path='/tmp/fl_world.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(errs); b.close()
