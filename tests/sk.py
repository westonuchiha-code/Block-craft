from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','sk'); pg.fill('#newSeed','777'); pg.click('#newBtn'); pg.wait_for_timeout(2500); pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const out={};
      out.start=[playerLevel(), maxHP(), health, JSON.stringify(skills)];
      out.fist0=playerAttackDamage();
      // punch a bear many times with fists
      const m=newBeast('bear',Math.floor(player.x)+1,Math.floor(player.y),Math.floor(player.z)); m.hp=1e6; mobs.push(m);
      for(let i=0;i<200;i++){ m.iframe=0; mobHit(m, playerAttackDamage()); trainSkill('unarmed'); }
      out.afterPunch=[skills.unarmed, playerLevel(), maxHP(), health, +playerAttackDamage().toFixed(2)];
      for(let i=0;i<400;i++) trainSkill('weapons'); for(let i=0;i<120;i++) trainSkill('magic');
      out.after=[JSON.stringify(skills), skillGained, playerLevel(), maxHP(), health];
      mobs.length=0;
      // athletics through real sprinting
      const a0=skills.athletics; running=true; for(let i=0;i<2000;i++) skillMoveTick(0.1,false); out.ath=[a0,skills.athletics];
      // stealth multiplier
      sneaking=true; out.stealth=+stealthMul().toFixed(2); sneaking=false;
      saveWorld(); return out; }""")
    print(json.dumps(r))
    pg.evaluate("()=>{ health=maxHP()-5; vitalKey=''; updateVitals(); }"); pg.wait_for_timeout(500); pg.screenshot(path='/tmp/sk_hud.png')
    pg.evaluate("()=>openSkills()"); pg.wait_for_timeout(400); pg.screenshot(path='/tmp/sk_menu.png')
    pg.evaluate("()=>closeSkills()")
    # persistence
    r2=pg.evaluate("""async ()=>{ scheduleSave(); await new Promise(r=>setTimeout(r,2500)); return JSON.stringify(skills); }""")
    pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{ const w=listWorlds().find(w=>w.name==='sk'); localStorage.removeItem(wkey(w.id,'lock')); loadWorld(w.id); }"); pg.wait_for_timeout(2500)
    r3=pg.evaluate("()=>[JSON.stringify(skills), playerLevel(), maxHP()]")
    print(r2==r3[0], r3)
    print(errs); b.close()
