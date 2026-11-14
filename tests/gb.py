import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for f in ['before_rocks','blockcraft_prototype']:
        pg=b.new_context().new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(f'file:///home/claude/{f}.html'); pg.wait_for_timeout(1500)
        pg.fill('#newName','gb'); pg.fill('#newSeed','5151'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
        r=pg.evaluate("""()=>{ const t=performance.now(); let n=0; for(let cx=60;cx<76;cx++)for(let cz=60;cz<76;cz++){ getChunk(cx,cz); n++; } return [(performance.now()-t)/n, n]; }""")
        print(f,r,errs)
    b.close()
