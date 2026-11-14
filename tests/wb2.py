from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':780,'height':390}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','wb2'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    r=pg.evaluate("""()=>{
      // find open grass: stand there
      let X=null; for(let x=-60;x<60&&!X;x+=2)for(let z=-60;z<60;z+=2){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+2&&colInfo(x+8,z).top===GRASS&&colInfo(x+8,z).h===c.h&&colInfo(x+4,z+3).h===c.h){ X=[x,z,c.h]; break; } }
      const [x,z,h]=X; player.x=x-1.5; player.z=z+.5; player.y=h+1.2;
      for(let i=1;i<=8;i++) for(let j=-4;j<=4;j++){ for(let k=h+1;k<=h+6;k++) setB(x+i,k,z+j,AIR); setB(x+i,h,z+j,GRASS); }
      // plant stages in a row at distance 3
      for(let k=0;k<4;k++) setB(x+2,h+1,z-3+k*2, WBP0+k);
      const m=newWb(x+5,h+1,z+1); m.yaw=Math.PI*0.85; mobs.push(m); m.shedT=999; m.age=0; m.shake=0;
      let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.05){ player.yaw=a; const f=camVectors().f; const d=f[0]; if(d>bd){bd=d;ba=a;} } player.yaw=ba; player.pitch=0.1;
      globalThis.__m=m; tod=0.27; return X; }""")
    print(r,errs); pg.wait_for_timeout(2500); print(pg.evaluate("()=>mobs.filter(m=>m.kind==='wb').map(m=>[m.x.toFixed(1),m.y,m.z.toFixed(1),m.dead,m.state])"), pg.evaluate('()=>[player.x,player.y,player.z]'))
    pg.screenshot(path='/tmp/wb2a.png')
    pg.evaluate("()=>{ __m.shake=3; __m.shedT=999; }"); pg.wait_for_timeout(900); pg.screenshot(path='/tmp/wb2b.png')
    print(pg.evaluate("()=>({seeds:wbSeeds.length})"),errs); b.close()
