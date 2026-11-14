from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    n=pg.evaluate("testPlan().pads.length")
    for i in range(3,n):
        pg.evaluate("""i=>{ health=20; mobs.length=0; const d=testPlan().pads[i]; player.x=d.x; player.z=d.z; player.y=TEST_FY+1; lastPCX=null; updateChunks(); }""",i)
        pg.wait_for_timeout(2200)
        print(pg.evaluate("i=>[testPlan().pads[i].name, isTestZ(player.z), Math.round(player.x), Math.round(player.y), Math.round(player.z), getB(Math.floor(player.x),Math.floor(player.y)-1,Math.floor(player.z))]",i))
        pg.screenshot(path='/tmp/pad%d.png'%i,clip={'x':0,'y':60,'width':390,'height':330})
        pg.evaluate("health=20; testGoHall()"); pg.wait_for_timeout(600)
    # gate
    pg.evaluate("""()=>{ const o=testPlan().rooms[9]; player.x=o.x0+9+1.0; player.z=TEST_Z+o.side*(4+10)-0.5*o.side; player.y=TEST_FY+1; lastPCX=null; updateChunks(); }""")
    pg.wait_for_timeout(2600)
    print('gate', pg.evaluate("[isUnder(player.z), isTestZ(player.z), Math.round(player.z)]"))
    pg.evaluate("health=20; testGoHall()"); pg.wait_for_timeout(500)
    # chest
    print(pg.evaluate("""()=>{ const c=testPlan().chestDefs[3]; openChest(c.x,c.y,c.z); const r=[document.querySelector('#chestBox .ptitle').textContent, Object.keys(chestOpen.items).length]; closeChest(); return r; }"""))
    # save/reload
    pg.evaluate("saveWorld()"); id=pg.evaluate("currentWorld")
    pg.evaluate("i=>{ openMenu(); loadWorld(i); }",id); pg.wait_for_timeout(3000)
    print('reload', pg.evaluate("[testWorld, isTestZ(player.z), getB(2,TEST_FY,TEST_Z)]"), errs); b.close()
