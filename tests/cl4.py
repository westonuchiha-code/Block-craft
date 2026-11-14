from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':780,'height':390}).new_page()
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','cl4'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    r=pg.evaluate("""()=>{ let best=null,mx=0,cnt=0,st=0; for(let x=-600;x<=600;x+=6)for(let z=-600;z<=600;z+=6){ const c=colInfo(x,z); cnt++; if(c.h>mx) mx=c.h; if(c.steep){ st++; if(!best||c.h>best[2]) best=[x,z,c.h]; } } return {mx,cnt,st,best,TREELINE,SNOW_LINE}; }""")
    print(r); b.close()
