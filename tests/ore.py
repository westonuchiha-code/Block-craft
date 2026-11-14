from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','ore'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""()=>{ const out={}; const cnt={}; let deep=0; const byY={iron:[],adam:[],mith:[]};
      for(let x=-200;x<200;x+=3) for(let z=-200;z<200;z+=3){ const h=colInfo(x,z).h; for(let y=1;y<h-6;y++){ const b=blockAt(x,y,z); if(b!==AIR&&b!==WATER&&b!==LAVA) deep++; if(b===IRON_ORE||b===ADAM_ORE||b===MITH_ORE||b===COAL){ cnt[NAMES[b]]=(cnt[NAMES[b]]||0)+1; } } }
      for(const k in cnt) out[k]='1 in '+Math.round(deep/cnt[k]);
      out.deepSolid=deep;
      out.hits={}; for(const [n,o] of [['iron',IRON_ORE],['adam',ADAM_ORE],['mith',MITH_ORE],['stone',STONE],['dirt',DIRT]]) out.hits[n]=[0,STONE_PICK,IRON_PICK,ADAM_PICK,MITH_PICK,MITH_SHOVEL].map(t=>hitsNeeded(o,t)+(canHarvest(o,t)?'':'x'));
      out.smelt=SMELT_RECIPES.slice(0,3).map(r=>r.name);
      // shaped craft: 3 iron ingots + 2 sticks in pickaxe shape
      const cells=[IRON_INGOT,IRON_INGOT,IRON_INGOT,0,STICK,0,0,STICK,0]; const m=matchGrid(cells,3); out.craftPick=m?NAMES[(m.out||m)[0]]:null;
      const c2=[MITH_INGOT,0,0,MITH_INGOT,0,0,STICK,0,0]; const m2=matchGrid(c2,3); out.craftSword=m2?NAMES[(m2.out||m2)[0]]:null;
      out.prices=[PRICE[IRON_PICK],PRICE[ADAM_SWORD],PRICE[MITH_PICK]];
      out.dmg={}; for(const t of [STONE_SWORD,IRON_SWORD,ADAM_SWORD,MITH_SWORD]){ inv[t]=1; HOTBAR[0]=t; sel=0; out.dmg[NAMES[t]]=+playerAttackDamage().toFixed(2); }
      return out; }""")
    print(json.dumps(r, indent=0))
    # icons: open catalog chest? draw icons into a canvas sheet
    pg.evaluate("""()=>{ const ids=[IRON_ORE,ADAM_ORE,MITH_ORE,IRON_INGOT,ADAM_INGOT,MITH_INGOT,...Array.from({length:15},(_,i)=>METAL_TOOL0+i),STONE_PICK,WOOD_PICK];
      const c=document.createElement('canvas'); c.width=ids.length*36; c.height=40; c.id='sheet'; c.style.cssText='position:fixed;left:0;top:0;z-index:999;background:#555;image-rendering:pixelated';
      const g=c.getContext('2d'); g.imageSmoothingEnabled=false; ids.forEach((id,i)=>g.drawImage(iconCanvas(id),i*36+2,2,32,32)); document.body.appendChild(c); }""")
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/ore_icons.png', clip={'x':0,'y':0,'width':850,'height':40})
    # held mithril pick and an ore wall view
    pg.evaluate("""()=>{ document.getElementById('sheet').remove(); inv[MITH_PICK]=1; HOTBAR[0]=MITH_PICK; sel=0; [IRON_INGOT,ADAM_INGOT,MITH_INGOT,LEATHER,GOLD,STEAK,SILK,MEAT_STEW].forEach((id,i)=>{ inv[id]=3; HOTBAR[i+1]=id; }); syncWear(); updateHotbar();
      const X=Math.floor(player.x), Y=Math.floor(player.y), Z=Math.floor(player.z)+3; const ores=[IRON_ORE,ADAM_ORE,MITH_ORE,COAL,STONE];
      for(let i=-2;i<=2;i++) for(let j=0;j<3;j++) setB(X+i,Y+j,Z,ores[(i+2)]); let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; const v=camVectors().f; if(v[2]>bd){bd=v[2];ba=a;} } player.yaw=ba; player.pitch=0; }""")
    pg.wait_for_timeout(1200); pg.screenshot(path='/tmp/ore_wall.png')
    print(errs[:3]); b.close()
