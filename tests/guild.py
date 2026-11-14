from playwright.sync_api import sync_playwright
# Guilds: joining, pay and price perks, standing and ranks from guild work, the journal entries, save and reload.
import json, sys
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1920,'height':1080}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','guild'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(5000)
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const o={};
      const guard={id:5, home:'g5', name:'Beren', job:'guard', vc:[Math.floor(player.x),Math.floor(player.z)], village:null, x:player.x, z:player.z};
      const cleric=Object.assign({},guard,{home:'c1',name:'Edda',job:'cleric'}), scholar=Object.assign({},guard,{home:'s1',name:'Varric',job:'librarian'});
      o.before={rank:guildRank('fighters'), train:trainCost('weapons','guard'), cap:trainCap('guard'), mp:mpMax(), spell:smCost().gold, cut:guildCut('temple',15,90)};
      const pay=(m)=>{ let q=null; for(let id=1;id<300 && !q;id++){ m.id=id; const c=questOffer(m); if(c && c.kind==='hunt') q=c; } const base=q.reward; acceptQuest(m,q); const got=q.reward; return [base,got,q]; };
      const p0=pay(guard); o.payOutsider=p0[1]/p0[0]; finishQuest(p0[2],true); o.repOutsider=guilds.fighters||null;
      guildJoin('fighters'); guildJoin('mages'); guildJoin('temple');
      o.joined={rank:guildRank('fighters'), train:trainCost('weapons','guard'), cap:trainCap('guard'), mp:mpMax(), spell:smCost().gold, cut:guildCut('temple',15,90)};
      const p1=pay(guard); o.payMember=+(p1[1]/p1[0]).toFixed(2); finishQuest(p1[2],true); o.repAfterHunt=guilds.fighters.rep;
      for(let i=0;i<4;i++){ const q=pay(guard); finishQuest(q[2],true); }
      o.later={rep:guilds.fighters.rep, rank:guildRank('fighters'), name:GUILDS.fighters.ranks[guildRank('fighters')], train:trainCost('weapons','guard'), cap:trainCap('guard')};
      const q=pay(guard); finishQuest(q[2],false); o.afterFail=guilds.fighters.rep;
      guilds.temple.rep=200; o.templeTop={rank:guildRank('temple'), cut:guildCut('temple',15,90)};
      o.journal=journal.filter(e=>/Guild|Temple/.test(e.t)).map(e=>e.t);
      saveWorld(); openSheet('standing'); return o; }""")
    print(json.dumps(r,indent=1))
    pg.wait_for_timeout(300)
    pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{ const w=listWorlds().find(w=>w.name==='guild'); localStorage.removeItem(wkey(w.id,'lock')); loadWorld(w.id); }"); pg.wait_for_timeout(2500)
    after=pg.evaluate("()=>[guildRank('fighters'), guildRank('mages'), guildRank('temple')]"); print('after reload ranks', after, errs)
    b_,j,l=r['before'],r['joined'],r['later']
    ok = (b_['rank']==-1 and r['payOutsider']==1 and r['repOutsider'] is None and j['rank']==0 and j['train']<b_['train'] and j['cap']==58 and j['mp']==b_['mp']+2 and j['spell']<b_['spell']
          and r['payMember']==1.08 and r['repAfterHunt']==12 and l['rank']==2 and l['cap']==74 and l['train']<j['train'] and r['afterFail']==l['rep']-6 and r['templeTop']['rank']==5 and abs(r['templeTop']['cut']-0.1)<1e-9
          and len(r['journal'])>=5 and after==[2,0,5])
    if not ok: bad.append('guild numbers')
    b.close()
print('GUILD TEST FAILED', bad) if bad else print('guilds ok')
sys.exit(1 if (bad or errs) else 0)
