from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':780,'height':390}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','wx'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    for bio,name in [(3,'snow'),(4,'sand'),(1,'rain')]:
        r=pg.evaluate("""(bio)=>{ for(let x=-900;x<=900;x+=10)for(let z=-900;z<=900;z+=10){ if(biomeAt(x,z)===bio){ const c=colInfo(x,z); if(c.h>SEA+2&&!c.open){ player.x=x+.5; player.z=z+.5; player.y=c.h+3; player.pitch=0.05; rainDawn(true); rainLeftT=1; return [x,z,c.h]; } } } return null; }""",bio)
        pg.wait_for_timeout(5500)
        st=pg.evaluate("()=>({wxBio,rainOn,rainShow:+rainShow.toFixed(2),kind:wxBio===3?'snow':wxBio===4?'sand':'rain'})")
        print(name,r,st); pg.screenshot(path=f'/tmp/wx_{name}.png')
    pg.evaluate("()=>{ rainOn=false; rainLeftT=0; player.z=UNDER_Z+5; player.x=0; player.y=60; }"); pg.wait_for_timeout(4000)
    print('ash',pg.evaluate("()=>({ashK:+ashK.toFixed(2),under:isUnder(player.z)})")); pg.screenshot(path='/tmp/wx_ash.png')
    print(errs); b.close()
