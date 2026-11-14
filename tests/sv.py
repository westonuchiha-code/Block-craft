from playwright.sync_api import sync_playwright
import json
# does a world saved by the current build keep its edits after reload?  and what region keys does it write?
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','sv'); pg.fill('#newSeed','77'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ classPick='warrior'; confirmClass(); }")
    pg.evaluate("()=>{ villageRep={'3,4':17}; dayNo=5; questId=9; quests=[{id:8,test:1}]; villagerState={a:1}; }")      # village standing, quests and the day count must survive too
    pg.evaluate("()=>{ const x=Math.floor(player.x)+2, z=Math.floor(player.z), y=colInfo(x,z).h+1; for(let k=0;k<5;k++) setB(x,y+k,z,STONE_BRICK); window.__p=[x,y,z]; saveWorld(); }")
    keys=pg.evaluate("()=>Object.keys(localStorage).filter(k=>k.includes(currentWorld)).map(k=>k.replace(currentWorld,'W'))")
    print(keys)
    pos=pg.evaluate("()=>window.__p")
    pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{ const w=listWorlds().find(w=>w.name==='sv'); localStorage.removeItem(wkey(w.id,'lock')); loadWorld(w.id); }"); pg.wait_for_timeout(2500)
    got=pg.evaluate("(p)=>NAMES[getB(p[0],p[1]+2,p[2])]", pos)
    meta=pg.evaluate("()=>[villageRep['3,4'], dayNo, questId, quests.length, villagerState.a]"); print('standing/day/quests', meta)
    print(got, errs[:2]); b.close()
    import sys
    if got!="stone brick" or meta!=[17,5,9,1,1]: sys.exit(1)
