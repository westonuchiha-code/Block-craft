from playwright.sync_api import sync_playwright
import json, sys
# Provinces: the land is divided into named baronies and counties about 1,400 blocks across. Crossing a border is announced and
# written in the journal; the map names the province; a violent crime is owed at half value in every village of the province.
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','prov'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const o={};
      const cnt={}; for(let x=-6000;x<6000;x+=64) for(let z=-6000;z<-200;z+=64){ const P=provinceAt(x,z); cnt[P.name]=(cnt[P.name]||0)+1; }
      const big=Object.values(cnt).map(n=>Math.sqrt(n*4096)).filter(w=>w>900);
      o.provs=Object.keys(cnt).length; o.minW=Math.round(Math.min(...big)); o.maxW=Math.round(Math.max(...big)); o.stable=provinceAt(100,-300)===provinceAt(101,-301);
      const by={}; for(let rx=-8;rx<=8;rx++) for(let rz=-8;rz<=0;rz++){ const v=villageAt(rx,rz); if(!v||!v.houses) continue; const k=provinceOfVillage([rx,rz]).key; (by[k]=by[k]||[]).push([rx,rz]); }
      const ks=Object.keys(by).filter(k=>by[k].length>=2), A=by[ks[0]][0], B=by[ks[0]][1], C=by[Object.keys(by).find(k=>k!==ks[0])][0];
      crime(A,'theft'); o.theft=[bountyOf(A),bountyOf(B),bountyOf(C)];
      crime(A,'assault'); o.assault=[bountyOf(A),bountyOf(B),bountyOf(C)];
      o.word=journal.some(e=>e.t.startsWith('Word of it will reach every guard in the '));
      gold=500; arrestEnd({village:B, x:0, z:0}, 'pay'); o.paidB=[bountyOf(A),bountyOf(B),gold];              // paying where only the province wants you clears the province's claim, not the first village's
      { const P=provinceInfo(provinceAt(player.x,player.z)), rs=new Set(); for(let x=-6000;x<6000;x+=700) rs.add(provinceInfo(provinceAt(x,-900)).ruler);
        o.ruler=[/^(Baron|Baroness|Count|Countess|Margrave|Margravine|Duke|Duchess|Lord|Lady) /.test(P.ruler), P.rival!==P.name && P.rival.startsWith('the '), rs.size>=6, provinceInfo(provinceAt(player.x,player.z)).ruler===P.ruler];
        const v=villageAt(0,0); o.says=talkNews({ id:3, x:v.cx, z:v.cz, village:[0,0], vc:[v.cx,v.cz], name:'T', job:'farmer', rumourDay:dayNo }).includes(', under '+P.ruler+'.'); }
      const P0=provinceAt(player.x,player.z); let x=player.x; while(provinceAt(x,player.z).key===P0.key && x<30000) x+=32; window.__bx=x; o.j0=journal.length; o.from=P0.name; o.to=provinceAt(x,player.z).name;
      return o; }""")
    print(json.dumps(r))
    if not (20<=r['provs']<=60 and r['minW']>900 and r['maxW']<2100 and r['stable']): bad.append('province shapes')
    if not (r['ruler']==[True,True,True,True] and r['says']): bad.append('rulers')
    if not (r['theft']==[30,0,0] and r['assault']==[70,20,0] and r['word']): bad.append('word of a crime')
    if not (r['paidB'][0]==70 and r['paidB'][1]==0 and r['paidB'][2]<500): bad.append('paying in the province')
    pg.wait_for_timeout(1500)
    pg.evaluate("()=>{ fly=true; player.x=window.__bx+40; player.y=TOP_BUILD; }"); pg.wait_for_timeout(2500)
    c=pg.evaluate("()=>({ here:provHere===provinceAt(player.x,player.z).key, seen:provSeen.length, j:journal.slice(-1)[0].t, toast:!!document.body.innerText.match(/you cross the border . .* rules here/) })")
    print(json.dumps(c))
    if not (c['here'] and c['seen']==2 and c['j']=='Crossed into '+r['to']+'.' and c['toast'] and r['from']!=r['to']): bad.append('crossing a border')
    pg.evaluate("()=>{ openMap(); }"); pg.wait_for_timeout(1200)
    m=pg.evaluate("""()=>{ const cv=document.getElementById('mapCanvas'), d=cv.getContext('2d').getImageData(0,0,cv.width,24).data; let gold=0; for(let i=0;i<d.length;i+=4) if(d[i]>200 && d[i+1]>190 && d[i+2]>130 && d[i+2]<190) gold++; return gold; }""")
    print('map title pixels', m, errs)
    if m<40: bad.append('map names the province')
    b.close()
print('PROVINCE TEST FAILED', bad) if bad else print('provinces ok')
sys.exit(1 if (bad or errs) else 0)
