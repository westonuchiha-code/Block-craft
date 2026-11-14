from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for vp,name in [({'width':1100,'height':560},'wide'),({'width':390,'height':844},'phone')]:
        pg=b.new_context(viewport=vp).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
        pg.fill('#newName','cl'+name); pg.fill('#newSeed','5'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
        shown=pg.evaluate("()=>document.getElementById('classMenu').classList.contains('show')")
        pg.click('.clCard[data-id="monk"]'); pg.wait_for_timeout(200); pg.screenshot(path=f'/tmp/cl_{name}.png')
        pg.click('#classGo'); pg.wait_for_timeout(300)
        r=pg.evaluate("""()=>({cls:playerClass, skills:JSON.stringify(skills), fist:+playerAttackDamage().toFixed(2), uses:[skillUsesFor('unarmed'),skillUsesFor('magic')], open:craftOpen,
            hp:maxHP()})""")
        pg.evaluate("()=>saveWorld()")
        pg.evaluate("()=>{ const w=listWorlds().find(w=>w.name==='cl"+name+"'); localStorage.removeItem(wkey(w.id,'lock')); loadWorld(w.id); }"); pg.wait_for_timeout(1200)
        r2=pg.evaluate("()=>[playerClass, document.getElementById('classMenu').classList.contains('show')]")
        r3=pg.evaluate("""()=>{ const o={}; for(const c of CLASSES){ playerClass=c.id; o[c.id]=[maxHP(), +playerAttackDamage().toFixed(2), skillUsesFor('magic')]; } playerClass='monk'; return o; }""")
        print(name, shown, json.dumps(r), r2, json.dumps(r3), errs[:2])
    b.close()
