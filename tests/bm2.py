from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m: errs.append('C:'+m.text) if m.type=='error' else None)
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    for k,name in ((6,'snow'),(7,'desert')):
        pg.evaluate("i=>{ health=20; paused=false; testPadGo({k:i}); }",k); pg.wait_for_timeout(5000)
        pg.evaluate("player.yaw=0.8; player.pitch=-0.05; health=20")
        pg.wait_for_timeout(2500)
        print(name, pg.evaluate("""()=>{ const X=Math.floor(player.x), Z=Math.floor(player.z), c={}; for(let dx=-40;dx<=40;dx++) for(let dz=-40;dz<=40;dz++){ const h=colInfo(X+dx,Z+dz).h; for(let y=h-3;y<=h+14;y++){ const b=getB(X+dx,y,Z+dz); if([ICE,SANDSTONE,CACTUS,PALM_LOG,PALM_LEAF,SNOW,SAND,LOG_IDS[3]].includes(b)) c[NAMES[b]]=(c[NAMES[b]]||0)+1; } } return [biomeAt(X,Z), Math.round(player.y), c]; }"""))
        pg.screenshot(path='/tmp/bm_%s.png'%name,clip={'x':0,'y':60,'width':390,'height':330})
    print(errs); b.close()
