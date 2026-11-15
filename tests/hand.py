from playwright.sync_api import sync_playwright
import json, sys
# Every named thing can sit on the hotbar and in the hand: its icon draws, its held model builds, and the frame loop survives holding it.
# (A gold vine on the hotbar used to stop the whole game: its icon had no texture to borrow.)
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hand'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const o={icon:[],model:[],n:0};
      for(let id=1;id<NB;id++){ if(!NAMES[id]) continue; o.n++;
        try{ iconCanvas(id); }catch(e){ o.icon.push(NAMES[id]); }
        try{ heldModel(id); }catch(e){ o.model.push(NAMES[id]); } }
      const k=n=>heldKind(NAMES.indexOf(n));
      o.kinds=[k('maple door'),k('window'),k('iron bars'),k('gold vine'),k('maple planks stairs'),k('stone'),k('iron ingot'),k('wood pickaxe')];
      return o; }""")
    ids=pg.evaluate("()=>['gold vine','maple door','window','iron bars','fire','lantern','bed'].map(n=>NAMES.indexOf(n)).filter(i=>i>0)")
    for i in ids:
        pg.evaluate("(id)=>{ inv[id]=3; HOTBAR[sel]=id; updateHotbar(); }", i); pg.wait_for_timeout(250)
    print(json.dumps(r)); print(errs)
    if r['icon']: bad.append('icons throw')
    if r['model']: bad.append('held models throw')
    if r['kinds']!=['item','item','item','item','block','block','item','tool']: bad.append('held kinds')
    b.close()
print('HAND TEST FAILED', bad) if bad else print('hand ok')
sys.exit(1 if (bad or errs) else 0)
