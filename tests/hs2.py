from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':780,'height':390}).new_page()
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hs2'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("""()=>{ for(let rx=-4;rx<=4;rx++)for(let rz=-4;rz<=4;rz++){const v=villageAt(rx,rz); if(!v) continue; const h=v.houses.find(h=>h.w>=7&&h.d>=5&&h.job!=='librarian'); if(!h) continue;
      const W=(h.r&1)?h.d:h.w; player.x=h.inside[0]+.5; player.z=h.inside[2]+.5; player.y=h.F+1; player.yaw=[0,Math.PI/2,Math.PI,-Math.PI/2][h.r]; player.pitch=-0.6; return; } }""")
    pg.wait_for_timeout(4000); pg.screenshot(path='/tmp/hs2.png'); b.close()
