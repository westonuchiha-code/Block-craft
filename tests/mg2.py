from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','mg'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    print(pg.evaluate("""()=>{ tod=0.25; updateMobs=function(){}; mobs.length=0; const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y);
      inv[BOLT_POTION]=1; inv[STONE_SWORD]=1; HOTBAR[0]=BOLT_POTION; HOTBAR[1]=STONE_SWORD; sel=0; placeBlock(); sel=1;
      const m=newCat(px,gy,pz-2); m.hp=30; mobs.push(m); window.m=m; castSpell(); const o={sw:swordSpell, ch:spellCharges, hp0:m.hp}; player.pitch=-0.5; punch(); o.hp1=m.hp; o.ch1=spellCharges; 
      // cooking: potion via grid match
      const r=COOK_RECIPES.find(r=>r.name==='fire potion (pepper)'); o.match = cookMatch ? 1 : 0; return o; }"""))
    pg.wait_for_timeout(900); pg.screenshot(path='/tmp/mg6.png')
    print(pg.evaluate("()=>{ for(let i=0;i<6;i++){ m.iframe=0; punch(); } return [spellCharges, spell, swordSpell, m.hp]; }"))
    pg.evaluate("()=>{ saveWorld(); }")
    print(errs); b.close()
