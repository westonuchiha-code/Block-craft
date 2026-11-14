from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','st'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.wait_for_timeout(3000)
    pg.evaluate("()=>{ const m=mobs.find(m=>m.kind==='npc'&&m.job!=='guard'); openTalk(m); talkAction('work'); talkAction('accept'); closeCraft(); const ks=[...visitedV]; addRep(ks[0].split(',').map(Number), 12); openSheet('standing'); }")
    pg.wait_for_timeout(400); pg.screenshot(path='/tmp/stand.png', clip={'x':280,'y':40,'width':540,'height':480})
    print(pg.evaluate("()=>document.getElementById('skillList').innerText.slice(0,500)"), errs)
