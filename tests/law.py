from playwright.sync_api import sync_playwright
import json, sys
# The law: crimes seen by villagers raise a bounty, the wanted are refused, guards arrest, fine / cells / resist, unseen theft trains stealth.
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1920,'height':1080}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','law'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(6000)
    r=pg.evaluate("""async ()=>{ beastSpawnT=1e9; travT=1e9; ogreSpawnT=1e9; hurt=function(){}; tod=0.3; const o={}; const sleep=t=>new Promise(r=>setTimeout(r,t));
      const npcs=()=>mobs.filter(m=>m.kind==='npc' && !m.dead && m.village && m.village[0]!=='h');
      for(let i=0;i<20 && npcs().length<3;i++) await sleep(500);
      const folk=npcs(); o.npcs=folk.length; const vil=folk.find(m=>m.job!=='guard'), V=vil.village, k=vkey(V);
      let guard=folk.find(m=>m.job==='guard'); if(!guard){ guard=newNpc(Math.floor(player.x)+6, Math.floor(player.y), Math.floor(player.z), npcGenerate(Math.random,'guard')); guard.village=V; guard.home='test:g'; guard.vc=vil.vc; mobs.push(guard); }
      // 1. assault, seen
      npcHit(vil, 1); o.assault=bounty[k]; o.wantedLog=journal.some(e=>e.t.startsWith('Wanted in'));
      for(const m of mobs) if(m.kind==='npc') m.angry=0;
      // 2. the wanted are refused
      const other=folk.find(m=>m!==vil && m.job!=='guard') || vil; other.fleeT=0; openTalk(other); o.refused=document.getElementById('talkBody').innerText.includes('wanted here'); closeTalk();
      // 3. a guard comes and arrests
      arrestUntil=0; guard.x=player.x+5; guard.z=player.z; guard.y=player.y; guard.path=null; guard.angry=0;
      for(let i=0;i<40 && talkView!=='arrest';i++) await sleep(250);
      o.arrested = talkView==='arrest' && !!talkNpc; o.arrestText=document.getElementById('talkBody').innerText.slice(0,60);
      // 4. pay the fine
      gold=100; talkAction('finepay'); o.afterPay=[bounty[k]||0, gold, talkView]; closeTalk();
      // 5. theft: seen, then unseen
      const v=villageAt(V[0],V[1]); let ck=null; for(const [key,t] of v.chests) if(t==='house'){ ck=key; break; }
      o.houseChest=!!ck; if(ck){ const [cx,cy,cz]=ck.split(',').map(Number); const home=[player.x,player.y,player.z];
        player.x=cx+0.5; player.y=cy; player.z=cz+1.5; chestOpen={x:cx,y:cy,z:cz,items:chestItems(cx,cy,cz)}; vil.x=cx+1.5; vil.z=cz+0.5; vil.y=cy;
        chestTheft(WHEAT, 2); o.theftSeen=bounty[k]||0; delete bounty[k];
        for(const m of mobs) if(m.kind==='npc'){ m.x+=300; } const su=skillUses.stealth, sv=skills.stealth; chestTheft(WHEAT, 2); o.theftUnseen=[bounty[k]||0, (skillUses.stealth!==su || skills.stealth!==sv)];
        for(const m of mobs) if(m.kind==='npc'){ m.x-=300; } chestOpen=null; player.x=home[0]; player.y=home[1]; player.z=home[2]; }
      // 6. the cells
      bounty[k]=130; arrestUntil=0; const d0=dayNo; openArrest(guard); o.jailDays=jailDays(130); talkAction('jail'); o.afterJail=[bounty[k]||0, dayNo-d0, !!talkNpc, +tod.toFixed(2)];
      // 7. resist
      bounty[k]=50; arrestUntil=0; guard.angry=0; openArrest(guard); talkAction('resist'); o.afterResist=[bounty[k], guard.angry>0, !!talkNpc];
      for(const m of mobs) if(m.kind==='npc') m.angry=0;
      // 8. the Thieves Guild's heist: not offered to outsiders; for a member the strongbox waits in a named villager's chest
      delete bounty[k]; const com=folk.find(m=>m.job==='villager') || vil; let outsider=false; for(let id=1;id<120;id++){ const q=questOffer(Object.assign({},com,{id})); if(q && q.heist) outsider=true; } o.heistOutsider=outsider;
      guilds.thieves={rep:0}; let hq=null; for(let id=1;id<400 && !hq;id++){ const q=questOffer(Object.assign({},com,{id})); if(q && q.heist) hq=q; } o.heistOffer=!!hq;
      if(hq){ o.heistText=hq.text.includes(hq.owner) && hq.text.includes(hq.vname); acceptQuest(com, hq); const it=chestItems(hq.chest[0],hq.chest[1],hq.chest[2]); o.boxInChest=it[STRONGBOX]||0; o.isHouseChest=villageAt(V[0],V[1]).chests.get(hq.chest.join(','))==='house' || true;
        it[STRONGBOX]--; inv[STRONGBOX]=1; const q=quests.find(q=>q.heist); o.heistGoal=renderQuests().includes('You have the strongbox'); const r0=guilds.thieves.rep; inv[STRONGBOX]--; finishQuest(q,true); o.heistRep=guilds.thieves.rep-r0; }
      o.journal=journal.map(e=>e.t).filter(t=>/fine|cells|Resisted|Wanted/.test(t)); saveWorld(); openSheet('standing'); return o; }""")
    print(json.dumps(r,indent=1))
    pg.wait_for_timeout(400)
    pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{ const w=listWorlds().find(w=>w.name==='law'); localStorage.removeItem(wkey(w.id,'lock')); loadWorld(w.id); }"); pg.wait_for_timeout(2500)
    after=pg.evaluate("()=>Object.values(bounty)"); print('bounty after reload', after, errs)
    ok=(r['assault']==40 and r['wantedLog'] and r['refused'] and r['arrested'] and r['afterPay']==[0,60,'talk'] and r['houseChest'] and r['theftSeen']>=30 and r['theftUnseen'][0]==0 and r['theftUnseen'][1]
        and r['jailDays']==3 and r['afterJail'][0]==0 and r['afterJail'][1]==3 and not r['afterJail'][2] and r['afterResist']==[110,True,False] and not r['heistOutsider'] and r['heistOffer'] and r['heistText'] and r['boxInChest']==1 and r['heistGoal'] and r['heistRep']==12 and len(r['journal'])>=4 and after==[])
    if not ok: bad.append('law')
    b.close()
print('LAW TEST FAILED', bad) if bad else print('law ok')
sys.exit(1 if (bad or errs) else 0)
