from playwright.sync_api import sync_playwright
import sys
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','bm'); pg.fill('#newSeed',sys.argv[1] if len(sys.argv)>1 else '12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const c=[0,0,0,0,0]; for(let i=0;i<6000;i++){ const x=(i%77-38)*80, z=(Math.floor(i/77)-38)*80; c[biomeAt(x,z)]++; } return [worldGen, c.map(v=>(v/60).toFixed(1)+'%').join(' ')]; }"""))
    print(errs); b.close()
