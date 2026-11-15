from playwright.sync_api import sync_playwright
import json, sys
# Soak: a long scripted session on two seeds that touches as much of the game as a script can reach, watching for any error.
# Every villager is spoken to and every button they offer is pressed; every screen is opened; days pass; you ride, travel by wagon,
# stand in a delve and in the Underworld, commit a crime, die, and the world is saved and loaded again. Nothing may throw, and you
# must end up somewhere real (finite position, alive, the frame loop still running).
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/blockcraft_prototype.html'
SEEDS=sys.argv[2].split(',') if len(sys.argv)>2 else ['12345','777']
bad=[]
STEPS = [
 ('talk to everyone', """()=>{ const V=window.__V=(()=>{ let best=null, bd=1e18; for(let a=-4;a<=4;a++) for(let c=-4;c<=4;c++){ const v=villageAt(a,c); if(!v||!v.houses||v.tavern===undefined) continue; const d=Math.hypot(v.cx,v.cz); if(d<bd){ bd=d; best=[a,c,v]; } } return best; })(), v=V[2];
    player.x=v.cx+0.5; player.z=v.cz+0.5; player.y=v.g+1; lastPCX=null; updateChunks(); gold=5000; let n=0, pressed=0;
    return new Promise(done=>setTimeout(()=>{ const L=mobs.filter(m=>m.kind==='npc' && !m.bandit).slice(0,12);
      for(const m of L){ if(!openTalk(m)) continue; n++;
        for(let pass=0; pass<3; pass++){ const A=[...document.querySelectorAll('#talkBody [data-a]')].map(b=>b.dataset.a).filter(a=>a!=='bye' && a!=='resist' && a!=='jail');
          for(const a of A){ if(!talkNpc) break; talkAction(a); pressed++; if(!talkNpc) openTalk(m); if(talkView!=='talk' && talkNpc){ const b=document.querySelector('#talkBody [data-buy]'); if(b) talkBuy(+b.dataset.buy); const s=document.querySelector('#talkBody [data-sell]'); if(s) talkSell(+s.dataset.sell); talkAction('back'); } } }
        if(talkNpc) closeTalk(); }
      done([n,pressed,quests.length]); }, 5000)); }"""),
 ('the notice board and tavern sign', """()=>{ const v=window.__V[2]; if(!v.board) return 'none'; openBoard(v.board[0],v.board[2]); for(const a of ['bread','bread','bwork','accept','bwork','decline']) if(talkNpc) talkAction(a); if(talkNpc) closeTalk(); return [quests.length, tavernNear(v.houses[v.tavern].x, v.houses[v.tavern].z)]; }"""),
 ('every screen', """()=>{ const o=[]; for(const t of ['skills','gear','magic','quests','standing']){ try{ openSheet(t); o.push(t); }catch(e){ throw new Error('sheet '+t+': '+e.message); } } closeSkills(); craftOpen=false;
    openMap(); renderMapSide(); mapZoom=2; drawMap(); mapZoom=1; drawMap(); document.getElementById('mapRealm').click(); mapZoom=0.25; drawMap(); mapZoom=4; drawMap(); mapZoom=1; document.getElementById('mapRealm').click(); closeMap(); openCraft(3); closeCraft(); openCraft(2); closeCraft(); toggleMenu(); toggleMenu(); return o.length; }"""),
 ('hold everything', """()=>{ let n=0; for(let id=1;id<NB;id++){ if(!NAMES[id]) continue; iconCanvas(id); heldModel(id); n++; } for(const id of [STONE, IRON_PICK, MEAT_STEW, CROSSBOW, NOTICE0, TSIGN0, 412, 316]){ inv[id]=2; HOTBAR[sel]=id; updateHotbar(); drawHand(); } return n; }"""),
 ('five days pass', """()=>{ const d0=dayNo; for(let i=0;i<5;i++){ advanceHours(24); } for(let i=0;i<60;i++){ provinceTick(); horseTick(); blessTick(); travellerTick(); hunterTick(); delveTick(); } return [dayNo-d0, dateStr(dayNo), quests.length]; }"""),
 ('buy and ride a horse', """()=>{ gold=5000; horse=null; buyHorse({ job:'farmer', village:[window.__V[0],window.__V[1]], name:'T' }); const m=horseMob(); if(!m) return 'no horse'; mountHorse(m); return riding(); }"""),
 ('ride about', None),
 ('get down, wagon to the next place', """()=>{ if(riding()) toggleSneak(); for(let a=-3;a<=3;a++) for(let c=-3;c<=3;c++){ const v=villageAt(window.__V[0]+a, window.__V[1]+c); if(v&&v.houses) visitedV.add((window.__V[0]+a)+','+(window.__V[1]+c)); } const P=knownPlaces().filter(p=>Math.hypot(p.x-player.x,p.z-player.z)>60); if(!P.length) return 'nowhere known'; wagonTo(P[0].key, false); return [P[0].name, Math.round(player.x), Math.round(player.z)]; }"""),
 ('crime and the law', """()=>{ const v=nearbyVillages().sort((p,q)=>Math.hypot(p[2].cx-player.x,p[2].cz-player.z)-Math.hypot(q[2].cx-player.x,q[2].cz-player.z))[0]; if(!v) return 'no village'; const vv=[v[0],v[1]]; player.x=v[2].cx+0.5; player.z=v[2].cz+0.5; player.y=v[2].g+1; lastPCX=null; updateChunks(); gold=5000;
    return new Promise(done=>setTimeout(()=>{ crime(vv,'theft'); crime(vv,'assault'); crime(vv,'murder'); const g=mobs.find(m=>m.kind==='npc' && m.job==='guard');
      let r='no guard near '+JSON.stringify([!!g, craftOpen, paused, g && g.angry, mobs.filter(m=>m.kind==='npc').length]); if(g){ openArrest(g); if(talkNpc){ talkAction('finepay'); r='paid '+(bountyOf(vv)===0); if(talkNpc) closeTalk(); } } hunterT=1; hunterTick(); const hn=mobs.filter(m=>m.hunter).length; bounty={}; mobs.filter(m=>m.hunter).forEach(m=>{ m.dead=true; m.deadT=0; }); done([r,hn]); }, 5000)); }"""),
 ('a delve', """()=>{ let P=null; for(let a=-3;a<=3&&!P;a++) for(let b=-3;b<=3&&!P;b++) P=delvePlan(a,b); if(!P) return 'no delve'; const N=P.nodes[P.heart]; health=maxHP(); player.x=N.cx+0.5; player.z=N.cz-4.5; player.y=N.F+0.01; lastPCX=null; updateChunks();
    return new Promise(done=>setTimeout(()=>{ delveTick(); openMap(); drawMap(); renderMapSide(); closeMap(); HOTBAR[sel]=0; if(readInscription({ b:STONE_BRICK, x:P.ex+2, y:P.h+2, z:P.ez })) talkAction('bye'); if(readInscription({ b:CARVED, x:N.cx, y:N.F+1, z:N.cz+3 })) talkAction('bye'); const c=P.nodes[P.heart].chests[0]; if(c){ openChest(c[0],c[1],c[2]); closeChest(); } mobs.length=0; done(P.name); }, 4000)); }"""),
 ('the Underworld', """()=>{ let Q=null; for(let x=0;x<400&&!Q;x+=4){ const z=UNDER_Z+40, c=underCol(x,z); if(c.hf>UNDER_LAVA+3 && c.hc-c.hf>14) Q=[x,z,c.hf]; } if(!Q) return 'none'; player.x=Q[0]+0.5; player.z=Q[1]+0.5; player.y=Q[2]+1; health=maxHP(); lastPCX=null; updateChunks();
    return new Promise(done=>setTimeout(()=>{ openMap(); drawMap(); renderMapSide(); closeMap(); mobs.length=0; done(isUnder(player.z)); }, 3500)); }"""),
 ('plan the whole region', """()=>{ let v=0, t=0, c=0, d=0, pr=new Set(), cells=0;
    for(let rx=-8;rx<=8;rx++) for(let rz=-8;rz<=8;rz++){ const V=villageAt(rx,rz); if(V&&V.houses){ v++; if(V.tavern!==undefined) t++; cells+=V.cells.size; for(let i=0;i<V.houses.length;i++) residentOf(rx,rz,i); tavernName(rx,rz); villageName(rx,rz); pr.add(provinceInfo(provinceOfVillage([rx,rz])).ruler); } }
    for(let rx=-6;rx<=6;rx++) for(let rz=-6;rz<=6;rz++){ if(cryptPlan(rx,rz)) c++; }
    for(let rx=-4;rx<=4;rx++) for(let rz=-4;rz<=4;rz++){ const P=delvePlan(rx,rz); if(P){ d++; for(const N of P.nodes) delveBlock(N.cx, N.F+1, N.cz); } }
    for(let x=-1500;x<=1500;x+=50) for(let z=-1500;z<=1500;z+=50){ roadAt(x,z); signAt(x,z); colInfo(x,z); biomeAt(x,z); }
    return [v,t,c,d,pr.size,cells]; }"""),
 ('walk the wilds', """async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); beastSpawnT=0; let n=0, kinds=new Set();
    for(let i=0;i<8;i++){ const an=i*0.785+0.3, r=250+i*170, x=Math.floor(Math.cos(an)*r), z=Math.floor(Math.sin(an)*r) - 300; if(isUnder(z)) continue;
      const y=Math.max(colInfo(x,z).h, SEA)+2; player.x=x+0.5; player.z=z+0.5; player.y=y; player.yaw=i; lastPCX=null; updateChunks(); tod=i%2 ? 0.75 : 0.3;
      for(let k=0;k<40 && !chunks.get(chunkKey(Math.floor(x/CS),Math.floor(z/CS)));k++){ await sleep(250); player.x=x+0.5; player.z=z+0.5; player.y=y; }      // (hold still until the ground under you exists)
      player.y=y; await sleep(2200); n++; for(const m of mobs) kinds.add(m.kind); }
    mobs.length=0; tod=0.3; return [n,[...kinds]]; }"""),
 ('dig and build', """async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); let X=null; for(let x=-200;x<200&&!X;x+=5) for(let z=-200;z<200;z+=5){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+2&&!nearVillage(x,z)){ X=[x,z,c.h]; break; } }
    player.x=X[0]+0.5; player.z=X[1]+0.5; player.y=X[2]+1; player.pitch=-1.35; player.yaw=0.2; lastPCX=null; updateChunks();
    for(let k=0;k<40 && !(chunks.get(chunkKey(Math.floor(X[0]/CS),Math.floor(X[1]/CS))) && target());k++) await sleep(500);      // (it has just come a long way: wait for the ground to be there)
    await sleep(1500); player.x=X[0]+0.5; player.z=X[1]+0.5; player.y=X[2]+1;
    inv[IRON_SHOVEL]=1; inv[IRON_PICK]=1; inv[COBBLE]=20; HOTBAR[0]=IRON_SHOVEL; HOTBAR[1]=IRON_PICK; HOTBAR[2]=COBBLE; sel=0; updateHotbar();
    const b0=getB(X[0],X[2],X[1]); for(let i=0;i<40;i++){ if(i===20){ sel=1; updateHotbar(); } swingT=0; punch(); await sleep(120); }
    const dug=[0,1,2,3].filter(k=>getB(X[0],X[2]-k,X[1])===AIR).length;
    player.x=X[0]+3.5; player.z=X[1]+0.5; player.y=colInfo(X[0]+3,X[1]).h+1; player.pitch=-0.7; player.yaw=1.2; await sleep(700); window.__X=X;
    sel=2; updateHotbar(); const t=target(); let placed=0; if(t){ const cnt=()=>{ let n=0; for(let a=-2;a<=2;a++) for(let c=-2;c<=2;c++) for(let k=0;k<=3;k++) if(getB(t.x+a,t.y+k,t.z+c)===COBBLE) n++; return n; }, n0=cnt(); for(let i=0;i<3;i++){ placeBlock(); await sleep(350); } placed=cnt()-n0; }
    player.pitch=0; return [NAMES[b0], dug, placed]; }"""),
 ('craft everything', """()=>{ let n=0, made=0; for(const r of RECIPES){ n++; for(const id in r.ing) inv[id]=(inv[id]||0)+r.ing[id]+2; inv[PLANKS]=99; const b=inv[r.out[0]]||0; try{ craftRecipe(r); }catch(e){ throw new Error('recipe '+NAMES[r.out[0]]+': '+e.message); } if((inv[r.out[0]]||0)>b) made++; }
    updateHotbar(); return [n, made]; }"""),
 ('eat, cast, fight, shoot', """async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const o={};
    food=5; inv[STEAK]=3; HOTBAR[3]=STEAK; sel=3; updateHotbar(); placeHeld=true; for(let k=0;k<20 && food===5;k++) await sleep(500); placeHeld=false; o.food=food;
    { const keep=book, n0=0; let n=0; for(const fx in SPELL_FX) for(let pw=0;pw<3;pw++){ book=[{fx,pow:pw}]; bookSel=0; mp=999; castCool=0; if(castBook()) n++; await sleep(120); } book=keep; bookSel=0; mp=mpMax(); o.cast=n; await sleep(1200); }      // every spell at every strength
    { const X=window.__X; player.x=X[0]-3.5; player.z=X[1]+0.5; player.y=colInfo(X[0]-4,X[1]).h+1; player.yaw=-1.57; player.pitch=0; await sleep(600); }
    const bx=Math.floor(player.x+Math.sin(player.yaw)*2), bz=Math.floor(player.z-Math.cos(player.yaw)*2), by=Math.round(player.y);
    const m=newBeast('spider', bx, by, bz, 0); mobs.push(m); inv[IRON_SWORD]=1; HOTBAR[4]=IRON_SWORD; sel=4; updateHotbar();
    m.idleT=999; for(let i=0;i<60 && !m.dead;i++){ player.yaw=Math.atan2(m.x-player.x, -(m.z-player.z)); player.pitch=Math.atan2(m.y+0.4-(player.y+EYE_H), Math.hypot(m.x-player.x,m.z-player.z)); swingT=0; punch(); await sleep(250); }
    o.killed=m.dead; o.spiderHp=m.hp; inv[CROSSBOW]=1; HOTBAR[5]=CROSSBOW; sel=5; updateHotbar(); player.pitch=0.1; for(let i=0;i<3;i++){ punch(); await sleep(700); } o.shot=true;
    mobs.length=0; sel=0; updateHotbar(); return o; }"""),
 ('back up, die and wake', """()=>{ const v=window.__V[2]; player.x=v.cx+0.5; player.z=v.cz+3.5; player.y=v.g+1; lastPCX=null; updateChunks(); inv[COBBLE]=5; return new Promise(done=>setTimeout(()=>{ hurt(9999, true); setTimeout(()=>{ const b=document.getElementById('respawnBtn'); if(b) b.click(); else if(typeof respawn==='function') respawn(); setTimeout(()=>{ health=maxHP(); done([dead, deathSacks.length, health>0]); }, 1500); }, 1500); }, 2500)); }"""),
 ('save', """()=>{ saveWorld(); return currentWorld; }"""),
]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for seed in SEEDS:
        pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
        pg.goto(F); pg.wait_for_timeout(1500)
        pg.fill('#newName','soak'+seed); pg.fill('#newSeed',seed); pg.click('#newBtn'); pg.wait_for_timeout(4000)
        pg.evaluate("()=>{ window.__f=0; (function t(){ window.__f++; requestAnimationFrame(t); })(); setInterval(()=>{ if(!window.__mortal && !dead){ health=maxHP(); fallPeakY=player.y; } }, 100); }")
        for name,js in STEPS:
            n0=len(errs)
            pg.evaluate("(die)=>{ if(dead) respawn(); window.__mortal = die; health = maxHP(); }", name=='back up, die and wake')      # the tour must survive its own stops (it is dropped beside a delve's master), so it is healed all the while
            try:
                if js is None:      # hold forward and turn for a while, in the saddle
                    pg.evaluate("()=>{ if(!running) toggleRun(); keys.KeyW=true; }")
                    for k in range(6): pg.wait_for_timeout(1500); pg.evaluate("()=>{ player.yaw+=0.9; keys.Space=!keys.Space; }")
                    r=pg.evaluate("()=>{ keys.KeyW=false; keys.Space=false; return [riding(), Math.round(player.x), Math.round(player.z)]; }")
                else: r=pg.evaluate(js)
            except Exception as e:
                r='THREW '+str(e).split('\n')[0][:260]; bad.append(seed+': '+name)
            pg.wait_for_timeout(700)
            st=pg.evaluate("()=>[paused, craftOpen, !!talkNpc]"); dd=pg.evaluate("()=>[dead, Math.round(health), Math.round(player.y)]")
            if dd[0] and name!='back up, die and wake': bad.append(seed+': died during '+name); print('   DIED:', pg.evaluate("()=>[document.getElementById('deathInfo').innerText.slice(0,160), Math.round(player.x), Math.round(player.y), Math.round(player.z), bodyInWater, headUnder]"))
            if st!=[False,False,False]: bad.append(seed+': left paused or a screen open after '+name+' '+str(st)); pg.evaluate("()=>{ if(talkNpc) closeTalk(); paused=false; craftOpen=false; }")
            if len(errs)>n0: bad.append(seed+': error during '+name)
            print(seed, '|', name, '|', json.dumps(r)[:200], '|', errs[n0:][:2])
            want={ 'dig and build': lambda r: isinstance(r,list) and r[1]>=1 and r[2]>=1, 'craft everything': lambda r: r[1]>=0.9*r[0], 'eat, cast, fight, shoot': lambda r: r['food']>5 and r['killed'] and r['cast']>=15,
                   'plan the whole region': lambda r: r[0]>=30 and r[1]>=0.9*r[0] and r[3]>=3, 'crime and the law': lambda r: str(r[0]).startswith('paid true'), 'buy and ride a horse': lambda r: r is True,
                   'talk to everyone': lambda r: r[0]>=4 and r[1]>=30, 'a delve': lambda r: isinstance(r,str) and r!='no delve', 'the Underworld': lambda r: r is True }
            if name in want:
                try: ok=want[name](r)
                except Exception: ok=False
                if not ok: bad.append(seed+': '+name+' did not do its job')
        wid=pg.evaluate("()=>currentWorld")
        pg.reload(); pg.wait_for_timeout(1500)
        pg.evaluate("(w)=>{ localStorage.removeItem(wkey(w,'lock')); loadWorld(w); }", wid); pg.wait_for_timeout(3500)
        fin=pg.evaluate("()=>({ pos:[player.x,player.y,player.z].every(Number.isFinite), alive:health>0 && !dead, day:dayNo, horse:!!horse, journal:journal.length, provs:provSeen.length, gold })")
        f0=pg.evaluate("()=>{ window.__f=0; (function t(){ window.__f++; requestAnimationFrame(t); })(); return new Promise(r=>setTimeout(()=>r(window.__f), 1500)); }")
        pg.wait_for_timeout(1500)
        print(seed, '| after reload |', json.dumps(fin), 'frames', f0, errs[-2:])
        if not (fin['pos'] and fin['alive'] and fin['day']>=5 and fin['journal']>3 and f0>3): bad.append(seed+': state after reload')
        if errs: bad.append(seed+': '+str(len(errs))+' page errors')
        pg.close()
    b.close()
print('SOAK FAILED', sorted(set(bad))) if bad else print('soak ok')
sys.exit(1 if bad else 0)
