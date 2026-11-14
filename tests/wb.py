from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':780,'height':390}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','wb'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    r=pg.evaluate("""()=>{ const out={};
      // put a woolbloom 5 blocks in front of the player on grass
      const px=Math.floor(player.x), pz=Math.floor(player.z); const y=ratTop(px+4,pz); out.y=y;
      const m=newWb(px+4,y,pz); mobs.push(m); out.boxes=wbBoxes(m,[]).length;
      m.shedT=0.1; out.id=m.id; return out; }""")
    print(r,errs)
    pg.wait_for_timeout(300)
    for i in range(14):
        pg.wait_for_timeout(500)
        st=pg.evaluate("()=>({seeds:wbSeeds.length, shake:+mobs.filter(m=>m.kind==='wb')[0].shake.toFixed(2), left:mobs.filter(m=>m.kind==='wb')[0].seedsLeft})")
        if i in (3,5,12): print(st)
        if i==4: pg.screenshot(path='/tmp/wb1.png')
    pg.evaluate("()=>{ const m=mobs.find(m=>m.kind==='wb'); player.yaw=Math.atan2(m.x-player.x, -(m.z-player.z)); player.yaw=player.yaw; }")
    b.close()
