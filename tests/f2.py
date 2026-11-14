from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','f2'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const out={}; const sleep=t=>new Promise(r=>setTimeout(r,t));
      out.skills=SKILLS.map(k=>k.id).join(',');
      // mining: natural stone with a pick trains; placed stone does not; dirt does not
      const X=Math.floor(player.x)+3, Z=Math.floor(player.z), Y=Math.floor(player.y)+1;
      const u0=skillUses.mining; setB(X,Y,Z,STONE); placedDel(X,Y,Z); breakNow({x:X,y:Y,z:Z,b:STONE}, STONE_PICK); out.natural=skillUses.mining-u0;
      inv[STONE]=1; setB(X,Y,Z,STONE); placedAdd(X,Y,Z); const u1=skillUses.mining; breakNow({x:X,y:Y,z:Z,b:STONE}, STONE_PICK); out.placed=skillUses.mining-u1;
      setB(X,Y,Z,DIRT); const u2=skillUses.mining; breakNow({x:X,y:Y,z:Z,b:DIRT}, STONE_PICK); out.dirt=skillUses.mining-u2;
      out.hits=[hitsNeeded(STONE,STONE_PICK)]; skills.mining=100; out.hits.push(hitsNeeded(STONE,STONE_PICK)); skills.mining=5;
      setB(X,Y,Z,LOG_IDS[0]); const w0=skillUses.woodcut; breakNow({x:X,y:Y,z:Z,b:LOG_IDS[0]}, WOOD_AXE); out.wood=skillUses.woodcut-w0;
      // alchemy recipe exists
      out.brew=COOK_RECIPES.filter(r=>r.out[0]===FIRE_POTION||r.out[0]===BOLT_POTION).map(r=>r.name);
      out.pistolRecipe=RECIPES.some(r=>r.out[0]===PISTOL);
      // death sack
      inv[COBBLE]=30; inv[STONE_PICK]=1; syncWear(); player.x+=30; player.y=colInfo(Math.floor(player.x),Math.floor(player.z)).h+1; const px=player.x, pz=player.z;
      die(); out.sack=deathSacks.length; out.invEmpty=Object.keys(inv).filter(k=>inv[k]>0).length; out.sackItems=JSON.stringify(deathSacks[0]&&deathSacks[0].items);
      respawn(); await sleep(500); const far=Math.hypot(player.x-px,player.z-pz); out.respawnDist=+far.toFixed(1);
      saveWorld(); return out; }""")
    print(json.dumps(r))
    # beam screenshot from a distance
    pg.evaluate("""()=>{ const s=deathSacks[0]; player.x=s.x-25; player.z=s.z; player.y=colInfo(Math.floor(player.x),Math.floor(player.z)).h+1.6; tod=0.3;
       let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; const v=camVectors().f; if(v[0]>bd){bd=v[0];ba=a;} } player.yaw=ba; player.pitch=-0.25; }""")
    pg.wait_for_timeout(2000); pg.screenshot(path='/tmp/f2_beam.png')
    pg.evaluate("()=>{ tod=0.8; }"); pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/f2_beam_night.png')
    r2=pg.evaluate("""async ()=>{ const s=deathSacks[0]; player.x=s.x; player.z=s.z; player.y=s.y-0.9; await new Promise(r=>setTimeout(r,800)); return [deathSacks.length, inv[COBBLE], inv[STONE_PICK], JSON.stringify(wear[STONE_PICK])]; }""")
    print(r2, errs[:3]); b.close()
