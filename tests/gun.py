from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','gun'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000); pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }"); pg.wait_for_timeout(500)
    print(pg.evaluate("""()=>{ const o={}; tod=0.25; updateMobs=function(){}; mobs.length=0;
      const px=Math.floor(player.x), pz=Math.floor(player.z)+14, gy=Math.floor(player.y)-1; window.T={px,pz,gy};
      for(let dx=-8;dx<=8;dx++) for(let dz=-30;dz<=2;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+9;y++) setB(px+dx,y,pz+dz,AIR); }
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=0;
      inv[CROSSBOW]=1; HOTBAR[0]=CROSSBOW; HOTBAR[1]=CROSSBOW; sel=0;
      const m=newCat(px,gy+1,pz-24); m.hp=30; mobs.push(m); window.m=m;
      // aim exactly at the cat's body center
      const ty=m.y+0.3, dy=ty-(player.y+1.6), dz=24; player.pitch=Math.atan2(dy,dz);
      o.rec=RECIPES.filter(r=>r.out[0]===CROSSBOW).length; o.pistolGone=!NAMES[PISTOL] && !GUN[PISTOL] && !PRICE[PISTOL]; return o; }"""), errs)
    pg.wait_for_timeout(500); pg.screenshot(path='/tmp/gun0.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("punch()"); pg.wait_for_timeout(30); pg.screenshot(path='/tmp/gun1.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.wait_for_timeout(700); print('crossbow at 24 blocks', pg.evaluate("[m.hp, gunCool.toFixed(2)]"))
    pg.wait_for_timeout(700)
    pg.evaluate("()=>{ sel=1; }"); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/gun2.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("punch()"); pg.wait_for_timeout(150); pg.screenshot(path='/tmp/gun3.png',clip={'x':0,'y':60,'width':390,'height':330}); pg.wait_for_timeout(700)
    print('crossbow', pg.evaluate("[m.hp, fx.length]"))
    # aim
    pg.evaluate("()=>{ placeHeld=true; sel=0; }"); pg.wait_for_timeout(600); pg.screenshot(path='/tmp/gun4.png',clip={'x':0,'y':60,'width':390,'height':330})
    print('aim', pg.evaluate("[aimK, TAN, aimSens, WK.on, WK.err||null]"))
    pg.evaluate("()=>{ sel=1; }"); pg.wait_for_timeout(400); pg.screenshot(path='/tmp/gun5.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("()=>{ placeHeld=false; player.pitch=-0.3; punch(); }"); pg.wait_for_timeout(900); pg.screenshot(path='/tmp/gun6.png',clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("[TAN, fx.map(e=>e.kind)]"), errs)
    b.close()
