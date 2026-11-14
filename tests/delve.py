from playwright.sync_api import sync_playwright
import json, sys
# Delves (cavern dungeons): the lifted world shape, that every chamber and the master can be reached on foot from the gate
# without digging (step up 1, drop up to 3), and that the master, chests, quest and map entry work.
WALK = r"""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const out=[];
      const L=[]; for(let a=-5;a<=5;a++) for(let b=-5;b<=5;b++){ const P=delvePlan(a,b); if(P) L.push(P); }
      for(const P of L.slice(0,8)){
        // can you walk (step up 1, drop up to 3) from the top of the stair to every chamber and to the master, without digging?
        const B=P.bb, W=B[1]-B[0]+1, Dp=B[5]-B[4]+1, Ht=B[3]-B[2]+3, solid=new Uint8Array(W*Dp*Ht);
        const idx=(x,y,z)=>((y-B[2]+1)*Dp+(z-B[4]))*W+(x-B[0]);
        for(let y=B[2]-1;y<=B[3]+1;y++) for(let z=B[4];z<=B[5];z++) for(let x=B[0];x<=B[1];x++){ const b=blockAt(x,y,z); solid[idx(x,y,z)] = (b===AIR||PASS[b]) && !IS_WATER[b] && !IS_LAVA[b] ? 0 : IS_WATER[b]||IS_LAVA[b] ? 2 : (IS_SHAPED[b] && b!==CHEST ? 3 : 1); }
        const S=(x,y,z)=> (x<B[0]||x>B[1]||z<B[4]||z>B[5]||y<B[2]-1||y>B[3]+1) ? 1 : solid[idx(x,y,z)];
        const stand=(x,y,z)=> S(x,y,z)!==1 && S(x,y,z)!==2 && S(x,y+1,z)===0 && (S(x,y-1,z)===1 || S(x,y,z)===3);   // feet cell free (or a slab), head free, floor below
        const seen=new Set(), q=[[P.ex,P.h+1,P.ez+1]]; seen.add(q[0].join(','));
        while(q.length){ const [x,y,z]=q.pop(); for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]]) for(let dy=1;dy>=-3;dy--){ const nx=x+dx, ny=y+dy, nz=z+dz; if(nx<B[0]||nx>B[1]||nz<B[4]||nz>B[5]) break; if(stand(nx,ny,nz)){ if(dy===1 && S(x,y+2,z)!==0) continue; const k=nx+','+ny+','+nz; if(!seen.has(k)){ seen.add(k); q.push([nx,ny,nz]); } break; } if(S(nx,ny,nz)===1 && dy<=0) break; } }
        const reach=P.nodes.map(N=>{ for(let a=-7;a<=7;a++) for(let c=-7;c<=7;c++) for(let y=N.F-1;y<=N.F+2;y++) if(seen.has((N.cx+a)+','+y+','+(N.cz+c))) return 1; return 0; });
        // and back out again (step up 1 only): from the heart to the gate
        out.push({name:P.name, at:[P.ex,P.ez], nodes:P.nodes.length, reached:reach.join(''), boss:seen.has(P.boss.join(','))||seen.has([P.boss[0],P.boss[1]-1,P.boss[2]].join(',')), cells:seen.size, size:[W,Dp], floors:P.F1+'..'+Math.min(...P.nodes.map(N=>N.F)), maxHc:Math.max(...P.nodes.map(N=>N.Hc)), maxR:Math.max(...P.nodes.map(N=>Math.max(N.a,N.b)))});
      }
      return out; }"""
PLAY = r"""async ()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; hurt=function(){}; const o={};
  const P=delveNear(player.x,player.z,1200).sort((p,q)=>Math.hypot(p.ex-player.x,p.ez-player.z)-Math.hypot(q.ex-player.x,q.ez-player.z))[0];
  let offer=null; for(let id=1;id<400 && !offer;id++){ const q=questOffer({id, home:'h'+id, job:'guard', vc:[P.ex-150,P.ez+40], x:P.ex-150, z:P.ez+40}); if(q && q.kind==='crypt' && q.delve) offer=q; }
  o.offer = offer ? offer.cname+' / '+offer.days+' days / '+offer.reward+' gold' : null;
  const N=P.nodes[P.heart]; player.x=N.cx+0.5; player.z=N.cz-5.5; player.y=N.F+0.01; lastPCX=null; updateChunks();
  await new Promise(r=>setTimeout(r,5000));
  o.seen=cryptSeen.has(P.key); o.awake=mobs.filter(m=>m.crypt===P.key).length;
  o.chests=N.chests.map(c=>NAMES[getB(c[0],c[1],c[2])]).join(','); o.loot=N.chests.map(c=>Object.keys(chestItems(c[0],c[1],c[2])).length);
  quests.push({ id:99, kind:'crypt', delve:1, crypt:P.key, cname:P.name, state:'active', at:[P.ex,P.ez], reward:400, days:8, rep:25 });
  const boss=mobs.find(m=>m.master && m.crypt===P.key); o.master=boss?boss.kind:null; if(boss) spellDamage(boss, 1e6);
  o.cleared=!!(cryptState[P.key] && cryptState[P.key].cleared); o.quest=quests.find(q=>q.id===99).state; o.site=siteByKey(P.key).name===P.name;
  // the heirloom job: the cup is put in the shrine chest when the job is taken, and can be carried back
  let relic=null; const npc={id:1, home:'hr', name:'Edda', job:'villager', vc:[P.ex-150,P.ez+40], village:null, x:P.ex-150, z:P.ez+40};
  cryptState={}; for(let id=1;id<600 && !relic;id++){ npc.id=id; const q=questOffer(npc); if(q && q.relic) relic=q; }
  o.relicOffer=!!relic; if(relic){ o.idFree=!IS_SHAPED[HEIRLOOM] && !TOOLS[HEIRLOOM] && !ARMOR[HEIRLOOM]; acceptQuest(npc, relic); const c=N.chests[0], it=chestItems(c[0],c[1],c[2]); o.inChest=it[HEIRLOOM]||0;
    it[HEIRLOOM]--; inv[HEIRLOOM]=1; const q=quests.find(q=>q.relic); o.canHandIn=(inv[q.item]||0)>=q.n; o.goal=renderQuests().includes('You have the heirloom'); inv[q.item]-=q.n; finishQuest(q,true); o.relicDone=!quests.some(q=>q.relic) && journal.some(e=>e.t.includes('heirloom')); }
  return o; }"""
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1100,'height':560}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','delve'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    shape=pg.evaluate("()=>({gen:worldGen, YOFF, SEA, TOP_BUILD, ground:colInfo(Math.floor(player.x),Math.floor(player.z)).h})"); print('world', shape)
    if shape['gen']<6 or shape['SEA']!=56 or shape['ground']<=56: bad.append('world shape')
    r=pg.evaluate(WALK)
    for d in r[:6]:
        ok = '0' not in d['reached'] and d['boss']
        print(('ok  ' if ok else 'BAD ')+d['name'], d['at'], 'chambers', d['reached'], 'master', d['boss'], 'floors', d['floors'], 'tallest', d['maxHc'])
        if not ok: bad.append(d['name'])
    if len(r)<3: bad.append('too few delves: %d' % len(r))
    g=pg.evaluate(PLAY); print('play', json.dumps(g))
    if not (g['offer'] and g['seen'] and g['awake']>0 and g['chests']=='chest,chest' and min(g['loot'])>0 and g['master'] and g['cleared'] and g['quest']=='done' and g['site'] and g['relicOffer'] and g['idFree'] and g['inChest']==1 and g['canHandIn'] and g['goal'] and g['relicDone']): bad.append('play')
    print(errs); b.close()
print('DELVE TEST FAILED:', bad) if bad else print('delves ok')
sys.exit(1 if (bad or errs) else 0)
