from playwright.sync_api import sync_playwright
import json, sys
# A new world opens with a letter: one piece of work already in the list (find the tavern keeper), which costs no work slot,
# never runs out, and ends with a meal, a little gold and a pointer to the notice board. It is saved, and old worlds get none.
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/blockcraft_prototype.html'
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(1500)
    pg.fill('#newName','intro'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; travT=1e9; const o={}, v=villageAt(0,0), q=quests[0];
      o.start=[quests.length, q && q.kind, q && q.giver==='0,0:'+v.tavern, q && q.giverName===residentOf(0,0,v.tavern).name, questCount(), questTitle(q)];
      o.journal=journal.length>=1 && journal[0].t.includes('a letter in my pocket') && journal[0].t.includes(tavernName(0,0));
      o.sheet=renderQuests().includes('The letter') && renderQuests().includes('two hanging lamps') && !renderQuests().includes('99999');
      for(let d=0;d<5;d++) questDawn(); o.kept=quests.some(x=>x.kind==='intro');                       // it never runs out
      // it does not use up a work slot
      const fake=i=>({ id:50+i, home:'9,9:'+i, name:'N'+i, job:'farmer', village:[0,0], vc:[v.cx,v.cz] });
      for(let i=0;i<3;i++) acceptQuest(fake(i), { kind:'fetch', item:COBBLE, n:1, days:9, reward:5, rep:0, text:'' }); o.slots=[quests.length, questCount(), acceptQuest(fake(7), { kind:'fetch', item:COBBLE, n:1, days:9, reward:5, rep:0, text:'' }).includes('as much work')];
      quests=quests.filter(x=>x.kind==='intro');
      // the keeper
      const h=v.houses[v.tavern], ch=residentOf(0,0,v.tavern), m=newNpc(h.inside[0],h.inside[1],h.inside[2],ch); m.home='0,0:'+v.tavern; m.house=h; m.village=[0,0]; m.vc=[v.cx,v.cz]; mobs.push(m);
      gold=0; const stew=inv[MEAT_STEW]||0; openTalk(m); const html=()=>document.getElementById('talkBody').innerText;
      o.button=html().includes('SHOW THE LETTER'); talkAction('turnin'); o.done=[quests.length, gold, (inv[MEAT_STEW]||0)-stew, html().includes('board in the square')];
      o.work=html().includes('ASK FOR WORK'); talkAction('work'); o.canWork=!html().includes('already have work from me'); closeTalk();
      saveWorld(); o.saved=JSON.parse(localStorage.getItem(wkey(currentWorld,'world'))).quests.length;
      return o; }""")
    print(json.dumps(r)); print(errs)
    if not (r['start']==[1,'intro',True,True,0,'the letter'] and r['journal'] and r['sheet'] and r['kept']): bad.append('the letter at the start')
    if not (r['slots']==[4,3,True]): bad.append('work slots')
    if not (r['button'] and r['done']==[0,25,1,True] and r['work'] and r['canWork'] and r['saved']==0): bad.append('the keeper')
    b.close()
print('INTRO TEST FAILED', bad) if bad else print('intro ok')
sys.exit(1 if (bad or errs) else 0)
