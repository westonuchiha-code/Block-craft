import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m: errs.append('C:'+m.text) if m.type=='error' else None)
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    print(pg.evaluate("[testWorld, player.x, player.y, player.z-TEST_Z, getB(2,TEST_FY+1,TEST_Z), getB(2,TEST_FY,TEST_Z), testPlan().cats.map(c=>c[0]+':'+c[1].length).join(' ')]"))
    print(errs)
    pg.evaluate("()=>{ for(let k=0;k<4;k++){ player.yaw=k; const f=camVectors().f; window['f'+k]=f; } }")
    print(pg.evaluate("[0,1,2,3].map(k=>{player.yaw=k; const f=camVectors().f; return [k,f[0].toFixed(2),f[2].toFixed(2)]})"))
    pg.screenshot(path='/tmp/tr0.png',clip={'x':0,'y':60,'width':390,'height':330}); b.close()
