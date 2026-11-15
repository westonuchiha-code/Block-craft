from playwright.sync_api import sync_playwright
import json,sys
# Many seeds: plan every village, crypt and delve over a wide area. Nothing may throw; every village has a guard and a notice board,
# nearly every one a tavern (with its spare bed and the keeper's place behind the bar), and every new world starts with the letter.
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    bad=[]
    for seed in (sys.argv[1:] or ['1','2','3','42','99999','hello']):
        pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(800)
        pg.fill('#newName','sd'+seed); pg.fill('#newSeed',seed); pg.click('#newBtn'); pg.wait_for_timeout(3500)
        try:
            r=pg.evaluate("""()=>{ const o={v:0,tav:0,guard:0,board:0,guest:0,keepOk:0,crypt:0,delve:0,letter:quests.some(q=>q.kind==='intro')};
              for(let rx=-7;rx<=7;rx++) for(let rz=-7;rz<=7;rz++){ const V=villageAt(rx,rz); if(!V||!V.houses) continue; o.v++; if(V.tavern!==undefined){ o.tav++; const h=V.houses[V.tavern]; if(h.guest) o.guest++; if(h.keep) o.keepOk++; }
                if(V.houses.some(h=>h.job==='guard')) o.guard++; if(V.board) o.board++; for(let i=0;i<V.houses.length;i++) residentOf(rx,rz,i); boardGuard(rx,rz); provinceInfo(provinceOfVillage([rx,rz])); }
              for(let rx=-6;rx<=6;rx++) for(let rz=-6;rz<=6;rz++) if(cryptPlan(rx,rz)) o.crypt++;
              for(let rx=-4;rx<=4;rx++) for(let rz=-4;rz<=4;rz++) if(delvePlan(rx,rz)) o.delve++;
              return o; }""")
        except Exception as e: r='THREW '+str(e)[:300]
        print(seed, json.dumps(r), errs[:2]); pg.close()
        if errs or not isinstance(r,dict) or not (r['v']>=20 and r['guard']==r['v'] and r['board']==r['v'] and r['tav']>=0.93*r['v'] and r['guest']==r['tav'] and r['keepOk']==r['tav'] and r['crypt']>=10 and r['delve']>=3 and r['letter']): bad.append(seed)
    b.close()
print('SEEDS TEST FAILED', bad) if bad else print('seeds ok')
sys.exit(1 if bad else 0)
