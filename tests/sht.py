from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':844}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','sht'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>{ classPick='ranger'; confirmClass(); gold=137; for(let i=0;i<120;i++) trainSkill('weapons'); quests.push({id:9,kind:'fetch',item:LEATHER,n:4,days:4,reward:60,rep:6,giver:'0,0:1',giverName:'Odo',giverJob:'blacksmith',village:[0,0],gvc:[40,40],due:3,state:'active'}); villageRep['0,0']=14; vitalKey=''; updateVitals(); }")
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/sht_hud.png')
    pg.keyboard.press('KeyJ'); pg.wait_for_timeout(300)
    r=[pg.evaluate("()=>[document.getElementById('skillMenu').classList.contains('show'), craftOpen]")]
    pg.screenshot(path='/tmp/sht_skills.png')
    pg.click('[data-tab="quests"]'); pg.wait_for_timeout(200); pg.screenshot(path='/tmp/sht_quests.png')
    pg.click('[data-tab="standing"]'); pg.wait_for_timeout(200); pg.screenshot(path='/tmp/sht_standing.png')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    r.append(pg.evaluate("()=>[document.getElementById('skillMenu').classList.contains('show'), craftOpen, paused]"))
    print(r, errs[:3]); b.close()
