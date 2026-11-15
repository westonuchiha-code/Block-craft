from playwright.sync_api import sync_playwright
import json, sys
# What people say first: their trade's lines, and often something about the moment (the hour, a holiday, your horse, your wounds, your name here).
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/blockcraft_prototype.html'
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(1500)
    pg.fill('#newName','greet'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; travT=1e9; const o={}; const say=(m,n)=>{ const S=new Set(); for(let i=0;i<(n||300);i++) S.add(greetLine(m)); return [...S]; };
      const mk=job=>({ job, name:'T', village:[0,0], vc:[0,0], home:'0,0:1' });
      ratNight=false; rainOn=false; dayNo=0; health=maxHP(); blessDay=-1; provDeeds={}; villageRep={}; horse=null;
      o.plain={}; for(const j of Object.keys(GREET)){ const L=say(mk(j)); o.plain[j]=L.length; if(L.some(x=>typeof x!=='string' || !x.length || x.includes('undefined'))) o.badLine=j; }
      const has=(L,re)=>L.some(x=>re.test(x));
      ratNight=true; o.night=has(say(mk('farmer')), /abroad late|rats come up/); ratNight=false;
      rainOn=true; o.rain=has(say(mk('farmer')), /Foul weather|out of the wet/); rainOn=false;
      dayNo=3; o.holiday=has(say(mk('baker')), /Merchants' Fair/); dayNo=0;
      health=2; o.hurt=[has(say(mk('farmer')), /temple could see to that/), has(say(mk('cleric')), /Let me see to that/)]; health=maxHP();
      const P=provinceOfVillage([0,0]); provDeeds[P.key]=3; o.knight=has(say(mk('guard')), /We know your name here, Knight|An honour to have you/); provDeeds={};
      villageRep['0,0']=60; o.liked=has(say(mk('miner')), /Always good to see you|Back again/); villageRep['0,0']=-20; o.disliked=has(say(mk('miner')), /It is you|Say your piece/); villageRep={};
      horse={x:0,y:0,z:0,yaw:0,mounted:true}; o.horse=has(say(mk('fisher')), /fine horse|ride well/); horse=null;
      o.hermit=say({ job:'hermit', hermit:true, name:'H' }).every(x=>GREET.hermit.includes(x));
      { const v=villageAt(0,0), names=v.houses.map((h,i)=>residentOf(0,0,i).name); let n=0, named=0, self=0; for(let id=0;id<200;id++){ const m={ id, job:'farmer', name:names[1], village:[0,0], vc:[v.cx,v.cz], home:'0,0:1', x:v.cx, z:v.cz, rumourDay:dayNo }; const t=talkNews(m), nl=neighbourLine(m,0,0);
          if(nl){ if(names.some(x=>nl.includes(x))) named++; if(nl.includes('{n}')||nl.includes('undefined')) self++; } if(Object.values(NEIGHBOUR).some(L=>L.some(x=>t.includes(x.split('{n}')[1])))) n++; }
        o.gossip=[n>20 && n<160, named>150, self===0]; }
      return o; }""")
    print(json.dumps(r)); print(errs)
    if r.get('badLine') or min(r['plain'].values())<4: bad.append('every trade has lines')
    if r['gossip']!=[True,True,True]: bad.append('talk of the neighbours')
    if not (r['night'] and r['rain'] and r['holiday'] and r['hurt']==[True,True] and r['knight'] and r['liked'] and r['disliked'] and r['horse'] and r['hermit']): bad.append('the moment')
    b.close()
print('GREETING TEST FAILED', bad) if bad else print('greetings ok')
sys.exit(1 if (bad or errs) else 0)
