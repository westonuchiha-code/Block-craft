from playwright.sync_api import sync_playwright
import json, os, time, traceback
OUT = '/home/claude/screenshots'
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
log = []          # (stage, note)
errs = []
n = [0]

PRE = r"""
window.T = {
  sleep: t=>new Promise(r=>setTimeout(r,t)),
  face(tx,ty,tz){ const dx=tx-player.x, dz=tz-player.z, dy=ty-(player.y+1.6); player.yaw=Math.atan2(dx,-dz); player.pitch=Math.atan2(dy,Math.hypot(dx,dz)); },
  freeze(){ beastSpawnT=1e9; ogreSpawnT=1e9; try{wbSpawnT=1e9;catSpawnT=1e9;ratSpawnT=1e9;}catch(e){} },
  flat(r){ r=r||9; for(let x=-400;x<400;x+=5) for(let z=-400;z<400;z+=5){ const c=colInfo(x,z); if(c.top!==GRASS||c.open||c.h<=SEA+2||nearVillage(x,z)) continue; let ok=true;
      for(let a=-r;a<=r&&ok;a+=3) for(let b=-r;b<=r;b+=3){ const q=colInfo(x+a,z+b); if(Math.abs(q.h-c.h)>1||q.top!==GRASS){ ok=false; break; } } if(ok) return [x,z,c.h]; } return null; },
  clear(x0,z0,h,r){ for(let i=-r;i<=r;i++) for(let j=-r;j<=r;j++){ for(let k=h+1;k<=h+10;k++) setB(x0+i,k,z0+j,AIR); setB(x0+i,h,z0+j,GRASS); } },
  closeAll(){ try{closeSkills();}catch(e){} try{closeCraft();}catch(e){} try{closeSpellmaker();}catch(e){} try{closeMap();}catch(e){} try{closeQuests();}catch(e){}
    for(const el of document.querySelectorAll('.show')) if(el.id && /Menu$|^death$/.test(el.id) && el.id!=='death') el.classList.remove('show'); craftOpen=false; paused=false; },
  fps(ms){ return new Promise(res=>{ let f=0; const t0=performance.now(); const step=()=>{ f++; if(performance.now()-t0<ms) requestAnimationFrame(step); else res(Math.round(f*1000/(performance.now()-t0))); }; requestAnimationFrame(step); }); },
};
"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': 1100, 'height': 560})
    pg = ctx.new_page()
    pg.on('pageerror', lambda e: errs.append(('pageerror', str(e)[:300])))
    pg.on('console', lambda m: errs.append(('console', m.text[:300])) if m.type == 'error' else None)

    def shot(name, clip=None):
        n[0] += 1
        fn = '%02d_%s.png' % (n[0], name)
        pg.screenshot(path=os.path.join(OUT, fn), clip=clip) if clip else pg.screenshot(path=os.path.join(OUT, fn))
        return fn

    def stage(name, js=None, wait=1200, arg=None, snap=True):
        e0 = len(errs)
        try:
            r = pg.evaluate(js, arg) if js and arg is not None else (pg.evaluate(js) if js else None)
            pg.wait_for_timeout(wait)
            fn = shot(name) if snap else None
            if r not in (None, {}, []): log.append((name, r))
            new = errs[e0:]
            if new: log.append((name, 'ERRORS: ' + json.dumps(new)))
            return r
        except Exception as ex:
            log.append((name, 'STAGE FAILED: ' + str(ex)[:400]))
            return None

    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    shot('title_menu')
    pg.fill('#newName', 'Tour'); pg.fill('#newSeed', '12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    shot('class_picker')
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.evaluate(PRE)
    pg.evaluate("()=>{ T.freeze(); tod=0.3; health=1000; rainMode='off'; rainOn=false; }")
    pg.wait_for_timeout(2500)
    stage('spawn_village_plaza', "()=>{ player.pitch=-0.05; return {pos:[player.x|0,player.y|0,player.z|0], village: nearestVillage(2) && villageName(nearestVillage(2))}; }", 1500)

    # village from above
    stage('village_from_above', """()=>{ const v=nearestVillage(2); player.x=v.cx-28; player.z=v.cz-28; player.y=colInfo(v.cx,v.cz).h+24; flying=true; player.vy=0; T.face(v.cx,colInfo(v.cx,v.cz).h,v.cz); }""", 3000)
    stage('village_street_level', """()=>{ const v=nearestVillage(2); player.x=v.cx+0.5; player.z=v.cz+12.5; player.y=colInfo(v.cx,v.cz+12).h+1; flying=false; T.face(v.cx,player.y+1,v.cz);
        return {npcs: mobs.filter(m=>m.kind==='npc').map(m=>m.job).join(',')}; }""", 3000)

    # villager up close + talk + trade + quest offer
    stage('villager_close', """()=>{ const m=mobs.find(m=>m.kind==='npc'&&m.job!=='guard'); if(!m) return 'no villager'; m.path=null; m.state='idle'; m.idleT=99;
        player.x=m.x+2.2; player.z=m.z+2.2; player.y=m.y; T.face(m.x,m.y+1.2,m.z); window.__npc=m; return m.job+' '+(m.name||''); }""", 1200)
    stage('talk_menu', "()=>{ openTalk(window.__npc); }", 500)
    stage('shop_trade', "()=>{ talkAction('trade'); }", 500)
    stage('quest_offer', "()=>{ talkAction('back'); talkAction('work'); return talkLine.slice(0,120); }", 500)
    stage('quest_accepted', "()=>{ try{ talkAction('accept'); }catch(e){ return 'accept: '+e; } return quests.length; }", 500)
    pg.evaluate("()=>T.closeAll()")
    stage('guard_close', """()=>{ const m=mobs.find(m=>m.kind==='npc'&&m.job==='guard'); if(!m) return 'no guard'; m.path=null; m.idleT=99; let best=null; for(let a=0;a<6.283;a+=0.4){ const x=Math.floor(m.x+Math.cos(a)*2.5), z=Math.floor(m.z+Math.sin(a)*2.5), y=Math.floor(m.y); if(PASS[getB(x,y,z)]&&PASS[getB(x,y+1,z)]&&!PASS[getB(x,y-1,z)]){ best=[x,y,z]; break; } } if(best){ player.x=best[0]+0.5; player.y=best[1]; player.z=best[2]+0.5; } T.face(m.x,m.y+1.2,m.z); return !!best; }""", 1200)

    # character sheet
    for tab in ['skills', 'gear', 'magic', 'quests', 'standing']:
        stage('sheet_' + tab, "(t)=>{ T.closeAll(); openSheet(t); }", 400, arg=tab)
    pg.evaluate("()=>T.closeAll()")

    # road & signpost & map
    stage('road', """()=>{ const e=roadEdgesNear(0,0)[0]; if(!e) return 'no road'; const s=e.signs[0]; player.x=s.x+0.5; player.z=s.z+6.5; player.y=colInfo(s.x,s.z+6).h+3; T.face(s.x,colInfo(s.x,s.z).h+1,s.z-12); return e.signs.length+' signs'; }""", 2500)
    stage('signpost', """()=>{ const s=roadEdgesNear(0,0)[0].signs[1]||roadEdgesNear(0,0)[0].signs[0]; let best=null; for(let a=0;a<6.283;a+=0.3){ const x=Math.floor(s.x+Math.cos(a)*3.5), z=Math.floor(s.z+Math.sin(a)*3.5), y=colInfo(x,z).h+1; if(ratCanStand(x,y,z)&&PASS[getB(x,y+1,z)]){ best=[x,y,z]; break; } }
        if(!best) return 'no stand'; player.x=best[0]+0.5; player.y=best[1]; player.z=best[2]+0.5; T.face(s.x+0.5,colInfo(s.x,s.z).h+1.6,s.z+0.5); return {sign:[s.x,s.z], block:NAMES[getB(s.x,colInfo(s.x,s.z).h+1,s.z)], stand:best}; }""", 2500)
    stage('world_map', "()=>{ openMap(); return {explored: explored.size}; }", 600)
    pg.evaluate("()=>T.closeAll()")

    # biomes
    for k, name in ((0, 'biome_a'), (1, 'biome_b'), (2, 'biome_c'), (6, 'biome_snow'), (7, 'biome_desert')):
        stage(name, "(k)=>{ mobs.length=0; testPadGo({k}); }", 4500, arg=k, snap=False)
        stage(name, "()=>{ player.yaw=0.8; player.pitch=-0.08; health=1000; return biomeAt(player.x,player.z); }", 2000)

    # beasts lineup on a cleared field
    P = pg.evaluate("()=>{ const X=T.flat(9); if(!X) return null; const [x,z,h]=X; player.x=x+0.5; player.z=z-12; player.y=h+1; return X; }")
    pg.wait_for_timeout(2000)
    if P:
        pg.evaluate("(P)=>{ const [x,z,h]=P; T.clear(x,z,h,12); window.__P=P; }", P)
        for kind in ['bear', 'tiger', 'spider', 'scorpion']:
            stage('beast_' + kind, """(k)=>{ const [x,z,h]=__P; mobs.length=0; BEAST[k]._ag=BEAST[k].aggro; BEAST[k].aggro=0; const m=newBeast(k,x+5,h+1,z); m.yaw=-Math.PI/2-0.6; m.idleT=999; m.angry=0; mobs.push(m);
                player.x=x+0.5; player.z=z+0.5; player.y=h+2.2; T.face(m.x,h+1.2,m.z); return 'lvl '+m.lvl+' hp '+m.hp; }""", 1200, arg=kind)
            pg.evaluate("(k)=>{ BEAST[k].aggro=BEAST[k]._ag; }", kind)
        stage('beasts_herd', """()=>{ const [x,z,h]=__P; mobs.length=0; const ks=['bear','tiger','spider','scorpion']; ks.forEach((k,i)=>{ BEAST[k]._ag=BEAST[k].aggro; BEAST[k].aggro=0; const m=newBeast(k,x+6,h+1,z-5+i*3.3); m.idleT=999; m.angry=0; m.yaw=-Math.PI/2; mobs.push(m); });
            for(const kk of ['ogre']) {} player.x=x-4.5; player.z=z+0.5; player.y=h+2.5; T.face(x+6,h+1,z); }""", 1500)
        stage('fight_tiger_action', """async ()=>{ const [x,z,h]=__P; for(const k of ['bear','tiger','spider','scorpion']) BEAST[k].aggro=BEAST[k]._ag; mobs.length=0; health=1000; inv[IRON_SWORD]=1; HOTBAR[0]=IRON_SWORD; sel=0; updateHotbar();
            const m=newBeast('tiger',x+7,h+1,z); mobs.push(m); m.angry=30; player.x=x+0.5; player.z=z+0.5; player.y=h+1; T.face(m.x,h+1,m.z); await T.sleep(1600); T.face(m.x,m.y+0.8,m.z); return {dist:+Math.hypot(m.x-player.x,m.z-player.z).toFixed(1), hurt:1000-health}; }""", 100)
        stage('ogre', """()=>{ const [x,z,h]=__P; mobs.length=0; const o=newOgre(x+7,h+1,z); o.hostile=false; o.idleT=999; mobs.push(o); player.x=x-2.5; player.z=z+0.5; player.y=h+2; T.face(o.x,h+2.5,o.z); }""", 1500)
        stage('woolbloom', """()=>{ const [x,z,h]=__P; mobs.length=0; for(let i=0;i<3;i++){ const w=newWb(x+5+i*1.4,h+1,z-2+i*2); mobs.push(w); } player.x=x-0.5; player.z=z+0.5; player.y=h+2; T.face(x+6,h+1.2,z); }""", 1500)
        stage('cat_and_rats', """()=>{ const [x,z,h]=__P; mobs.length=0; mobs.push(newCat(x+4,h+1,z-1)); for(let i=0;i<3;i++) mobs.push(newRat(x+5+i,h+1,z+1+i*0.7)); player.x=x+0.5; player.z=z+0.5; player.y=h+1.8; T.face(x+5,h+0.5,z+0.5); }""", 1500)

        # fire in action
        stage('fire_lit', """async ()=>{ const [x0,z0,h]=__P; mobs.length=0; T.clear(x0,z0,h,12); for(let i=-2;i<=2;i++) for(let j=-2;j<=2;j++) for(let k=1;k<=4;k++){ if(Math.abs(i)===2||Math.abs(j)===2||k===4) setB(x0+i,h+k,z0+j,PLANKS); }
            for(let k=1;k<=5;k++) setB(x0+5,h+k,z0,LOG_IDS[0]); for(let a=-2;a<=2;a++) for(let c=-2;c<=2;c++) for(let k=5;k<=7;k++) if(getB(x0+5+a,h+k,z0+c)===AIR && Math.abs(a)+Math.abs(c)+(k-5)<4) setB(x0+5+a,h+k,z0+c,LEAF_IDS?LEAF_IDS[0]:LEAVES);
            inv[TINDERBOX]=1; HOTBAR[0]=TINDERBOX; sel=0; updateHotbar(); player.x=x0-3.5; player.z=z0+0.5; player.y=h+1; player.yaw=Math.PI/2; player.pitch=0; placeBlock(); const lit=fires.size;
            const fk=[...fires.keys()]; const ser=[]; const F0=fk[0].split(',').map(Number); const nb=WDIRS.map(([a,b,c])=>NAMES[getB(F0[0]+a,F0[1]+b,F0[2]+c)]); const fobj=JSON.stringify(fires.get(fk[0])); window.__F0=F0; player.x=x0-9.5; player.z=z0-7.5; player.y=h+2.5; T.face(x0+1,h+3,z0); for(let i=0;i<5;i++){ await T.sleep(1000); ser.push(fires.size+(rainOn?'R':'')); } return {lit, fk, ser, nb, fobj, fuel: fireFuelNear(...F0), rainMode, x0,z0,h, here:[player.x|0,player.z|0], blockAtFire: fk[0]&&NAMES[getB(...fk[0].split(',').map(Number))]}; }""", 100)
        stage('fire_spreading', "async ()=>{ await T.sleep(6000); return fires.size; }", 100)
        stage('fire_aftermath', "async ()=>{ await T.sleep(14000); return fires.size; }", 100)

        pass
    b.close()
print(json.dumps(log[-4:],default=str)); print(errs)
raise SystemExit
