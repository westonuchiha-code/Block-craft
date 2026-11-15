from playwright.sync_api import sync_playwright
import json, sys
# The notice board in each village plaza (worlds from worldGen 7): it stands on the flagstones, opens a panel that names the place, its
# province and ruler and the date, gives a rumour once a day, and posts the ruler's bounty, which is reported to the village guard.
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/blockcraft_prototype.html'
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(1500)
    pg.fill('#newName','board'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const o={n:0,ok:0};
      for(let rx=-4;rx<=4;rx++) for(let rz=-4;rz<=4;rz++){ const v=villageAt(rx,rz); if(!v||!v.houses) continue; o.n++; if(!v.board) continue; let found=0;
        for(const arr of v.cells.values()) for(let i=1;i<arr.length;i+=2) if(arr[i]===NOTICE0) found++; if(found===1) o.ok++; }
      const v=villageAt(0,0), B=v.board; window.__B=B; player.x=B[0]+0.5; player.z=B[2]+2.5; player.y=B[1]; player.yaw=0; player.pitch=-0.1; tod=0.3; return o; }""")
    pg.wait_for_timeout(3500)
    t=pg.evaluate("""()=>{ const o={}, B=window.__B; mobs.length=0;
      o.block=[getB(B[0],B[1],B[2])===NOTICE0, !PASS[getB(B[0],B[1]-1,B[2])] && getB(B[0],B[1]-1,B[2])!==AIR, getB(B[0],B[1]+2,B[2])===AIR];
      openBoard(B[0],B[2]); const html=()=>document.getElementById('talkBody').innerText; o.open=document.getElementById('talkMenu').classList.contains('show');
      o.title=document.getElementById('talkName').textContent; o.head=html().slice(0,200);
      const s0=cryptSeen.size; talkAction('bread'); o.read1=[cryptSeen.size-s0, html().includes('forbids all trade')]; talkAction('bread'); o.read2=html().includes('Nothing new');
      talkAction('bwork'); o.offer=html().includes('BY ORDER OF') && html().includes('TAKE THE NOTICE'); const q0=quests.length; talkAction('accept');
      const q=quests[quests.length-1]; o.took=[quests.length-q0, q && q.kind, q && q.board, q && q.giver, q && q.giverName, q && q.reward>100, html().includes('Report to')];
      talkAction('bwork'); o.again=html().includes('already taken'); talkAction('bye'); o.closed=!document.getElementById('talkMenu').classList.contains('show') && !craftOpen;
      const G=boardGuard(0,0); o.guard=[G.home===q.giver, G.name===q.giverName];
      cryptCleared(q.crypt); o.done=q.state;
      openBoard(B[0]+40,B[2]); o.far=document.getElementById('talkMenu').classList.contains('show');
      // honours: the first bounty makes you a Friend of the province, the third a Knight (fines halved), and it is saved
      const P=provinceInfo(provinceOfVillage([0,0])), g0=gold, j0=journal.length; bounty={}; crime([0,0],'assault'); const f0=fineOf([0,0]);
      finishQuest(q,true); o.hon1=[provDeeds[P.key], honourOf(P.key), honourTitle(P)==='Friend of '+P.name, gold-g0===q.reward, journal.slice(j0).some(e=>e.t.includes('names you Friend of'))];
      provinceDeed([0,0]); provinceDeed([0,0]); o.hon3=[honourOf(P.key), fineOf([0,0])*2===f0, renderQuests().includes('Knight of '+P.name)];
      openBoard(B[0],B[2]); o.known=html().includes('You are known here as Knight of'); talkAction('bye'); bounty={};
      saveWorld(); o.saved=JSON.parse(localStorage.getItem(wkey(currentWorld,'world'))).provDeeds[P.key]===3;
      return o; }""")
    print(json.dumps(r)); print(json.dumps(t)); print(errs)
    if not (r['n']>=10 and r['ok']==r['n']): bad.append('a board in every village')
    if not (t['block']==[True,True,True] and t['open'] and 'Notice board' in t['title'] and 'IRONHOLD' in t['head'] and ' rules.' in t['head'] and 'Greening' in t['head']): bad.append('the board opens')
    if not (t['read1']==[1,True] and t['read2']): bad.append('notices')
    if not (t['offer'] and t['took'][0]==1 and t['took'][1]=='crypt' and t['took'][2]==1 and t['took'][5] and t['took'][6] and t['again'] and t['closed'] and t['guard']==[True,True] and t['done']=='done' and t['far'] is False): bad.append('the bounty')
    if not (t['hon1']==[1,1,True,True,True] and t['hon3']==[2,True,True] and t['known'] and t['saved']): bad.append('honours')
    pg.screenshot(path='/tmp/board.png')
    b.close()
print('BOARD TEST FAILED', bad) if bad else print('board ok')
sys.exit(1 if (bad or errs) else 0)
