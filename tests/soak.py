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
    openMap(); renderMapSide(); mapZoom=2; drawMap(); mapZoom=1; drawMap(); closeMap(); openCraft(3); closeCraft(); openCraft(2); closeCraft(); toggleMenu(); toggleMenu(); return o.length; }"""),
 ('hold everything', """()=>{ let n=0; for(let id=1;id<NB;id++){ if(!NAMES[id]) continue; iconCanvas(id); heldModel(id); n++; } for(const id of [STONE, IRON_PICK, MEAT_STEW, CROSSBOW, NOTICE0, TSIGN0, 412, 316]){ inv[id]=2; HOTBAR[sel]=id; updateHotbar(); drawHand(); } return n; }"""),
 ('five days pass', """()=>{ const d0=dayNo; for(let i=0;i<5;i++){ advanceHours(24); } for(let i=0;i<60;i++){ provinceTick(); horseTick(); blessTick(); travellerTick(); hunterTick(); delveTick(); } return [dayNo-d0, dateStr(dayNo), quests.length]; }"""),
 ('buy and ride a horse', """()=>{ gold=5000; horse=null; buyHorse({ job:'farmer', village:[window.__V[0],window.__V[1]], name:'T' }); const m=horseMob(); if(!m) return 'no horse'; mountHorse(m); return riding(); }"""),
 ('ride about', None),
 ('get down, wagon to the next place', """()=>{ if(riding()) toggleSneak(); for(let a=-3;a<=3;a++) for(let c=-3;c<=3;c++){ const v=villageAt(window.__V[0]+a, window.__V[1]+c); if(v&&v.houses) visitedV.add((window.__V[0]+a)+','+(window.__V[1]+c)); } const P=knownPlaces().filter(p=>Math.hypot(p.x-player.x,p.z-player.z)>60); if(!P.length) return 'nowhere known'; wagonTo(P[0].key, false); return [P[0].name, Math.round(player.x), Math.round(player.z)]; }"""),
 ('crime and the law', """()=>{ const v=nearbyVillages().sort((p,q)=>Math.hypot(p[2].cx-player.x,p[2].cz-player.z)-Math.hypot(q[2].cx-player.x,q[2].cz-player.z))[0]; if(!v) return 'no village'; const vv=[v[0],v[1]]; player.x=v[2].cx+0.5; player.z=v[2].cz+0.5; player.y=v[2].g+1; lastPCX=null; updateChunks(); gold=5000;
    return new Promise(done=>setTimeout(()=>{ crime(vv,'theft'); crime(vv,'assault'); crime(vv,'murder'); const g=mobs.find(m=>m.kind==='npc' && m.job==='guard');
      let r='no guard near '+JSON.stringify([!!g, craftOpen, paused, g && g.angry, mobs.filter(m=>m.kind==='npc').length]); if(g){ openArrest(g); if(talkNpc){ talkAction('finepay'); r='paid '+(bountyOf(vv)===0); if(talkNpc) closeTalk(); } } hunterT=1; hunterTick(); const hn=mobs.filter(m=>m.hunter).length; bounty={}; mobs.filter(m=>m.hunter).forEach(m=>{ m.dead=true; m.deadT=0; }); done([r,hn]); }, 5000)); }"""),
 ('a delve', """()=>{ let P=null; for(let a=-3;a<=3&&!P;a++) for(let b=-3;b<=3&&!P;b++) P=delvePlan(a,b); if(!P) return 'no delve'; const N=P.nodes[P.heart]; health=maxHP(); player.x=N.cx+0.5; player.z=N.cz-4.5; player.y=N.F+0.01; lastPCX=null; updateChunks();
    return new Promise(done=>setTimeout(()=>{ delveTick(); openMap(); drawMap(); renderMapSide(); closeMap(); const c=P.nodes[P.heart].chests[0]; if(c){ openChest(c[0],c[1],c[2]); closeChest(); } health=maxHP(); mobs.length=0; done(P.name); }, 4000)); }"""),
 ('the Underworld', """()=>{ let Q=null; for(let x=0;x<400&&!Q;x+=4){ const z=UNDER_Z+40, c=underCol(x,z); if(c.hf>UNDER_LAVA+3 && c.hc-c.hf>14) Q=[x,z,c.hf]; } if(!Q) return 'none'; player.x=Q[0]+0.5; player.z=Q[1]+0.5; player.y=Q[2]+1; health=maxHP(); lastPCX=null; updateChunks();
    return new Promise(done=>setTimeout(()=>{ openMap(); drawMap(); renderMapSide(); closeMap(); mobs.length=0; health=maxHP(); done(isUnder(player.z)); }, 3500)); }"""),
 ('back up, die and wake', """()=>{ const v=window.__V[2]; player.x=v.cx+0.5; player.z=v.cz+3.5; player.y=v.g+1; lastPCX=null; updateChunks(); inv[COBBLE]=5; return new Promise(done=>setTimeout(()=>{ hurt(9999, true); setTimeout(()=>{ const b=document.getElementById('respawnBtn'); if(b) b.click(); else if(typeof respawn==='function') respawn(); setTimeout(()=>done([dead, deathSacks.length, health>0]), 1500); }, 1500); }, 2500)); }"""),
 ('save', """()=>{ saveWorld(); return currentWorld; }"""),
]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for seed in SEEDS:
        pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
        pg.goto(F); pg.wait_for_timeout(1500)
        pg.fill('#newName','soak'+seed); pg.fill('#newSeed',seed); pg.click('#newBtn'); pg.wait_for_timeout(4000)
        pg.evaluate("()=>{ window.__f=0; (function t(){ window.__f++; requestAnimationFrame(t); })(); }")
        for name,js in STEPS:
            n0=len(errs)
            try:
                if js is None:      # hold forward and turn for a while, in the saddle
                    pg.evaluate("()=>{ if(!running) toggleRun(); keys.KeyW=true; }")
                    for k in range(6): pg.wait_for_timeout(1500); pg.evaluate("()=>{ player.yaw+=0.9; keys.Space=!keys.Space; }")
                    r=pg.evaluate("()=>{ keys.KeyW=false; keys.Space=false; return [riding(), Math.round(player.x), Math.round(player.z)]; }")
                else: r=pg.evaluate(js)
            except Exception as e:
                r='THREW '+str(e).split('\n')[0][:260]; bad.append(seed+': '+name)
            pg.wait_for_timeout(700)
            st=pg.evaluate("()=>[paused, craftOpen, !!talkNpc]")
            if st!=[False,False,False]: bad.append(seed+': left paused or a screen open after '+name+' '+str(st)); pg.evaluate("()=>{ if(talkNpc) closeTalk(); paused=false; craftOpen=false; }")
            if len(errs)>n0: bad.append(seed+': error during '+name)
            print(seed, '|', name, '|', json.dumps(r)[:200], '|', errs[n0:][:2])
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
