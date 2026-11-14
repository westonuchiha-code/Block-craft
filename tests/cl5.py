from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':780,'height':390}).new_page()
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','cl5'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    r=pg.evaluate("""()=>{ // find a steep stone column, stand on grass beside it at a safe height, face it
      for(let x=-300;x<=300;x+=3)for(let z=-300;z<=300;z+=3){ const c=colInfo(x,z); if(!(c.steep&&c.top===STONE&&c.h>38)) continue;
        for(const [dx,dz] of [[8,0],[-8,0],[0,8],[0,-8]]){ const c2=colInfo(x+dx,z+dz); if(c2.top===GRASS&&!c2.open&&c2.h<c.h-6&&c2.h>SEA+2){ player.x=x+dx+.5; player.z=z+dz+.5; player.y=c2.h+14;
          let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.05){ player.yaw=a; const f=camVectors().f; const d=-f[0]*dx-f[2]*dz; if(d>bd){bd=d;ba=a;} } player.yaw=ba; player.pitch=0.25; return [x,z,c.h,c2.h]; } } }
      return null; }""")
    print(r); pg.wait_for_timeout(1500); pg.evaluate('()=>{player.vy=0;player.pitch=0.25}'); pg.wait_for_timeout(300); pg.evaluate('()=>{player.y=player.y;}'); pg.screenshot(path='/tmp/cl5.png'); b.close()
