from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','arm'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""()=>{ const out={};
      out.craft=[matchGrid([LEATHER,LEATHER,LEATHER,LEATHER,0,LEATHER,0,0,0],3), matchGrid([IRON_INGOT,0,IRON_INGOT,IRON_INGOT,IRON_INGOT,IRON_INGOT,IRON_INGOT,IRON_INGOT,IRON_INGOT],3)].map(m=>m?NAMES[(m.out||m)[0]]:null);
      for(const id of [AR(0,0),AR(0,1),AR(0,2),AR(0,3),AR(4,1)]) inv[id]=1; inv[DYE0+3]=2;
      HOTBAR[0]=AR(0,1); sel=0; placeBlock(); out.wornByUse=armor[1]&&NAMES[armor[1].id];
      equipArmor(AR(0,0)); equipArmor(AR(0,2)); equipArmor(AR(0,3)); out.pts=armorPoints();
      health=20; hurt(10); out.hp10=health; health=20; hurt(4,true); out.fallPure=health;
      equipArmor(AR(4,1)); out.swapped=[NAMES[armor[1].id], inv[AR(0,1)]]; out.pts2=armorPoints(); health=20; hurt(10); out.hp10b=health;
      dyeArmor(0,3); out.dye=armor[0].dye;
      out.charTop=dressedChar().topCol;
      const d0=armor[1].dur; for(let i=0;i<5;i++){ health=20; hurt(2);} out.wear=d0-armor[1].dur;
      // death keeps armor in the sack
      player.x+=20; die(); out.sackArmor=deathSacks[0].armor.filter(a=>a).length; out.wornAfterDeath=armor.filter(a=>a).length; respawn();
      const s=deathSacks[0]; player.x=s.x; player.z=s.z; player.y=s.y-0.9; updateSacks(); out.restored=armor.filter(a=>a).length;
      return out; }""")
    print(json.dumps(r))
    pg.evaluate("()=>{ openSheet('gear'); }"); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/arm_gear.png')
    pg.evaluate("()=>{ closeSkills(); camMode=2; }"); pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/arm_3p.png')
    pg.evaluate("""()=>{ camMode=0; const ids=Object.keys(ARMOR).map(Number); ids.slice(0,9).forEach((id,i)=>{ inv[id]=1; HOTBAR[i]=id; }); updateHotbar(); }"""); pg.wait_for_timeout(400)
    pg.screenshot(path='/tmp/arm_hb.png', clip={'x':290,'y':465,'width':520,'height':70})
    pg.evaluate("""()=>{ const ids=Object.keys(ARMOR).map(Number); ids.slice(9,18).forEach((id,i)=>{ inv[id]=1; HOTBAR[i]=id; }); updateHotbar(); }"""); pg.wait_for_timeout(400)
    pg.screenshot(path='/tmp/arm_hb2.png', clip={'x':290,'y':465,'width':520,'height':70})
    print(errs[:3]); b.close()
