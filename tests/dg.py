from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','dg'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={};
      out.bands=[0,300,500,1000,1500,2000,2500,3000].map(d=>dangerAt(d,40,0)); out.deep=dangerAt(0,10,0);
      out.bear=[0,1,3,5].map(l=>{ const m=newBeast('bear',0,40,0,l); return m.hp+'hp/'+lvlDmg(BEAST.bear.bite,l)+'dmg'; });
      out.ogre=newOgre(2000,40,0).hp+' vs '+newOgre(0,40,0).hp;
      // crossing a band boundary
      player.x=440; player.z=0; player.y=colInfo(440,0).h+2; await sleep(1500); player.x=470; player.y=colInfo(470,0).h+2; await sleep(1500);
      out.toast=document.getElementById('skillToast').textContent;
      // quest reward scaling
      for(let i=0;i<120;i++) trainSkill('weapons'); out.level=playerLevel();
      return out; }""")
    print(json.dumps(r)); print(errs[:3]); b.close()
