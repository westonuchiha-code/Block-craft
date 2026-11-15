from playwright.sync_api import sync_playwright
import json, sys, os
# A world saved by the build that was handed over on 2026-11-14 (tests/fixtures) must load in the current build with nothing lost:
# old world shape, position, class, items, gold, standing, day, quests, edits; and load again after the current build saves it.
import tempfile, shutil
D=tempfile.mkdtemp(prefix='bc_compat_')
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fixtures','handoff_build_2026-11-14.html'), D+'/old.html')
shutil.copy('/home/claude/blockcraft_prototype.html', D+'/new.html')
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1920,'height':1080}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    # 1. play a little in the build he handed over
    pg.goto('file://'+D+'/old.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','oldsave'); pg.fill('#newSeed','4242'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }"); pg.wait_for_timeout(3000)
    old=pg.evaluate("""()=>{ beastSpawnT=1e9; const x=Math.floor(player.x)+2, z=Math.floor(player.z), y=colInfo(x,z).h+1; for(let k=0;k<4;k++) setB(x,y+k,z,STONE_BRICK); window.__p=[x,y,z];
      inv[IRON_PICK]=1; inv[MITH_SWORD]=1; inv[ADAM_INGOT]=3; inv[COBBLE]=40; HOTBAR[0]=IRON_PICK; HOTBAR[1]=MITH_SWORD; gold=321; villageRep={'0,0':22}; dayNo=6;
      quests.push({ id:5, kind:'fetch', item:COAL_ITEM, n:5, giver:'0,0:1', giverName:'Marek', giverJob:'miner', village:[0,0], gvc:[player.x,player.z], due:dayNo+4, days:4, reward:50, rep:8, state:'active' });
      saveWorld(); return { gen:worldGen, sea:(typeof SEA!=='undefined'?SEA:null), pos:[Math.round(player.x),Math.round(player.y),Math.round(player.z)], cls:playerClass, hp:maxHP(), ground:colInfo(Math.floor(player.x),Math.floor(player.z)).h, edit:window.__p,
               mithTier:TOOLS[MITH_SWORD].tier, keys:Object.keys(localStorage).length }; }""")
    print('OLD', json.dumps(old))
    # 2. open the same save in the current build (same folder, so the same saved data)
    pg.goto('file://'+D+'/new.html'); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{ const w=listWorlds().find(w=>w.name==='oldsave'); localStorage.removeItem(wkey(w.id,'lock')); loadWorld(w.id); }"); pg.wait_for_timeout(5000)
    new=pg.evaluate("""(p)=>{ const o={ gen:worldGen, YOFF, sea:SEA, pos:[Math.round(player.x),Math.round(player.y),Math.round(player.z)], cls:playerClass, hp:maxHP(), ground:colInfo(Math.floor(player.x),Math.floor(player.z)).h,
        edit:NAMES[getB(p[0],p[1]+2,p[2])], inv:[inv[IRON_PICK],inv[MITH_SWORD],inv[ADAM_INGOT],inv[COBBLE]], hotbar:[HOTBAR[0]===IRON_PICK,HOTBAR[1]===MITH_SWORD], gold, rep:villageRep['0,0'], dayNo, quests:quests.length,
        picker:document.getElementById('classMenu').classList.contains('show'), delves:delveNear(player.x,player.z,3000).length, mithTier:TOOLS[MITH_SWORD].tier, adamTier:TOOLS[MT(1,3)].tier,
        journal:journal.length, guilds:Object.keys(guilds).length, bounty:Object.keys(bounty).length, standing:(player.y - (colInfo(Math.floor(player.x),Math.floor(player.z)).h+1)) };
      const f0=WK.frames||0; return new Promise(r=>setTimeout(()=>{ o.frames=(WK.frames||0)-f0; openSheet('quests'); o.sheet=document.getElementById('skillList').innerText.includes('Marek'); openSheet('standing'); o.standingTab=document.getElementById('skillList').innerText.includes('GUILDS'); saveWorld(); r(o); },2000)); }""", old['edit'])
    print('NEW', json.dumps(new))
    # 3. and it loads again after the current build has saved it
    pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{ const w=listWorlds().find(w=>w.name==='oldsave'); localStorage.removeItem(wkey(w.id,'lock')); loadWorld(w.id); }"); pg.wait_for_timeout(3500)
    again=pg.evaluate("(p)=>({gen:worldGen, YOFF, edit:NAMES[getB(p[0],p[1]+2,p[2])], gold, quests:quests.length, cls:playerClass})", old['edit'])
    print('AGAIN', json.dumps(again)); print('errors', errs)
    ok=(new['gen']==old['gen'] and new['YOFF']==0 and new['sea']==16 and new['pos']==old['pos'] and new['cls']=='warrior' and new['hp']==old['hp'] and new['ground']==old['ground'] and new['edit']=='stone brick'
        and new['inv']==[1,1,3,40] and new['hotbar']==[True,True] and new['gold']==321 and new['rep']==22 and new['dayNo']==6 and new['quests']==1 and not new['picker'] and new['delves']==0 and new['frames']>0 and new['sheet'] and new['standingTab']
        and again['gen']==old['gen'] and again['edit']=='stone brick' and again['gold']==321 and again['quests']==1 and not errs)
    print('OLD SAVE COMPATIBLE' if ok else 'COMPATIBILITY PROBLEM'); b.close(); sys.exit(0 if ok else 1)
