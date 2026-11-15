from playwright.sync_api import sync_playwright
import json, sys
# A temple's blessing: paid to a cleric, it closes your wounds slowly until the sunrise after next, then fades; saved with the world.
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/blockcraft_prototype.html'
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(1500)
    pg.fill('#newName','bless'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const o={}; dayNo=5;
      const c={ id:1, job:'cleric', name:'T', village:[0,0], vc:[0,0], home:'0,0:9', x:player.x, y:player.y, z:player.z, pose:{} };
      talkNpc=c; talkView='talk'; talkOffer=null; talkLine=''; renderTalk(); const html=()=>document.getElementById('talkBody').innerText;
      o.button=html().includes('ASK A BLESSING (25g)'); gold=10; talkAction('bless'); o.poor=[blessed(), gold];
      gold=100; const j0=journal.length; talkAction('bless'); o.paid=[blessed(), gold, blessDay, journal.slice(j0).some(e=>e.t.startsWith('Received a blessing'))];
      o.noButton=!html().includes('ASK A BLESSING'); talkAction('bless'); o.twice=gold; talkNpc=null;
      health=10; for(let i=0;i<25;i++) blessTick(); o.heal=health; health=maxHP(); for(let i=0;i<25;i++) blessTick(); o.full=health===maxHP();
      questDawn(); o.day2=[dayNo, blessed()]; questDawn(); o.day3=[dayNo, blessed(), !!document.body.innerText.match(/the blessing fades/)];
      health=10; for(let i=0;i<25;i++) blessTick(); o.after=health;
      blessDay=dayNo+1; saveWorld(); o.saved=JSON.parse(localStorage.getItem(wkey(currentWorld,'world'))).bless===dayNo+1;
      dayNo=41-DAY0; o.mending=blessCost();                      // the Day of Mending: free
      return o; }""")
    print(json.dumps(r)); print(errs)
    if not (r['button'] and r['poor']==[False,10] and r['paid']==[True,75,6,True] and r['noButton'] and r['twice']==75): bad.append('asking')
    if not (r['heal']==12 and r['full'] and r['day2']==[6,True] and r['day3']==[7,False,True] and r['after']==10): bad.append('the blessing itself')
    if not (r['saved'] and r['mending']==0): bad.append('saved, and free on the holy day')
    b.close()
print('BLESSING TEST FAILED', bad) if bad else print('blessing ok')
sys.exit(1 if (bad or errs) else 0)
