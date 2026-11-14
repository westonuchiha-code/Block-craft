from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','ch'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500); pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    print(pg.evaluate("""()=>{ const v=nearestVillage(2); window.V=v; mobs.length=0; trySpawnOgre=function(){}; const o={n:v.chests.size, tiers:[...v.chests.values()].join(',')};
      const [k,tier]=[...v.chests.entries()].find(e=>e[1]==='dungeon')||[...v.chests.entries()][0]; const q=k.split(',').map(Number); window.Q=q; o.tier=tier; o.block=getB(q[0],q[1],q[2])===CHEST;
      const a=JSON.stringify(chestItems(q[0],q[1],q[2])); chests.delete(k); o.sameAgain = a===JSON.stringify(chestItems(q[0],q[1],q[2])); o.loot=a;
      inv[PLANKS]=10; craftMode='craft'; craftRecipe(RECIPES.find(r=>r.name==='Chest')); o.crafted=inv[CHEST];
      openChest(q[0],q[1],q[2]); return o; }"""), errs)
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/ch1.png')
    pg.click('#chestGrid .slot2'); pg.wait_for_timeout(100)
    print(pg.evaluate("({chest:JSON.stringify(chestOpen.items), hb:HOTBAR.slice()})"))
    pg.click('#chestInv .slot2'); pg.wait_for_timeout(100)
    print(pg.evaluate("JSON.stringify(chestOpen.items)"))
    pg.click('#chestClose')
    print(pg.evaluate("""()=>{ const o={open:craftOpen}; saveWorld(); const m=JSON.parse(localStorage.getItem(wkey(currentWorld,'world'))); o.saved=Object.keys(m.chests).length;
      const n0=itemDrops.length; breakNow({x:Q[0],y:Q[1],z:Q[2],b:CHEST},0); o.spilled=itemDrops.length-n0; o.gone=!chests.has(Q.join(',')); return o; }"""), errs)
    b.close()
