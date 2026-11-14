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
            pg.evaluate("()=>{ if(!dead){ health=1000; } }")
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
    stage('signpost', """()=>{ const s=roadEdgesNear(0,0)[0].signs[1]||roadEdgesNear(0,0)[0].signs[0]; let best=null; for(let a=0;a<6.283;a+=0.2){ const x=Math.floor(s.x+Math.cos(a)*3.5), z=Math.floor(s.z+Math.sin(a)*3.5), y=colInfo(x,z).h+1; if(PASS[getB(x,y,z)]&&PASS[getB(x,y+1,z)]&&!PASS[getB(x,y-1,z)]&&!IS_WATER[getB(x,y-1,z)]){ best=[x,y,z]; break; } }
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
            inv[TINDERBOX]=1; HOTBAR[0]=TINDERBOX; sel=0; updateHotbar(); player.x=x0-3.5; player.z=z0+0.5; player.y=h+1; player.yaw=Math.PI/2; player.pitch=0; placeBlock(); ignite(x0-3,h+1,z0-1); ignite(x0-3,h+1,z0+1); ignite(x0+4,h+1,z0); const lit=fires.size;
            const fk=[...fires.keys()]; const ser=[]; const F0=fk[0].split(',').map(Number); const nb=WDIRS.map(([a,b,c])=>NAMES[getB(F0[0]+a,F0[1]+b,F0[2]+c)]); const fobj=JSON.stringify(fires.get(fk[0])); window.__F0=F0; player.x=x0-9.5; player.z=z0-7.5; player.y=h+2.5; T.face(x0+1,h+3,z0); for(let i=0;i<5;i++){ await T.sleep(1000); ser.push(fires.size+(rainOn?'R':'')); } return {lit, fk, ser, nb, fobj, fuel: fireFuelNear(...F0), rainMode, x0,z0,h, here:[player.x|0,player.z|0], blockAtFire: fk[0]&&NAMES[getB(...fk[0].split(',').map(Number))]}; }""", 100)
        stage('fire_spreading', "async ()=>{ await T.sleep(6000); return fires.size; }", 100)
        stage('fire_aftermath', "async ()=>{ await T.sleep(14000); return fires.size; }", 100)

        # homestead
        stage('homestead', """async ()=>{ const [x0,z0,h]=__P; mobs.length=0; T.clear(x0,z0,h,12); const house=(cx,cz)=>{ for(let i=-3;i<=3;i++) for(let j=-3;j<=3;j++){ const wall=Math.abs(i)===3||Math.abs(j)===3; setB(cx+i,h,cz+j,PLANKS); for(let k=1;k<=3;k++) if(wall) setB(cx+i,h+k,cz+j,PLANKS); setB(cx+i,h+4,cz+j,PLANKS); }
              setB(cx,h+1,cz-3,doorId(0,0,0,0,0)); setB(cx,h+2,cz-3,doorId(0,0,0,1,0)); };
            house(x0,z0); house(x0+9,z0);
            const putBed=(bx,bz)=>{ inv[BED0]=(inv[BED0]||0)+1; HOTBAR[0]=BED0; sel=0; player.x=bx+0.5; player.z=bz-1.5; player.y=h+1; player.pitch=-1.2; let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; const v=camVectors().f; if(v[2]>bd){bd=v[2];ba=a;} } player.yaw=ba; placeBlock(); };
            putBed(x0-1,z0); putBed(x0+8,z0); for(let d=0;d<4&&homesteads.length&&homesteads[0].homes.some(H=>!H.ch);d++) homesteadDawn();
            player.x=x0+4.5; player.z=z0-9; player.y=h+1.5; T.face(x0+4.5,h+2,z0); await T.sleep(5000);
            return {homesteads: homesteads.map(s=>s.name), settlers: mobs.filter(m=>m.kind==='npc'&&m.home&&m.home[0]==='h').map(m=>m.job)}; }""", 500)
        stage('homestead_standing', "()=>{ openSheet('standing'); }", 400)
        pg.evaluate("()=>T.closeAll()")

        # armor in third person
        stage('armor_mithril_3p', """()=>{ const [x,z,h]=__P; mobs.length=0; for(let k=0;k<4;k++){ const id=AR(4,k); inv[id]=1; equipArmor(id); }
            inv[MITH_SWORD]=1; HOTBAR[0]=MITH_SWORD; sel=0; syncWear(); updateHotbar(); player.x=x-6.5; player.z=z+0.5; player.y=h+1; player.yaw=Math.PI/2; player.pitch=-0.1; camMode=2; return armorPoints(); }""", 1500)
        stage('armor_iron_3p', "()=>{ for(let k=0;k<4;k++){ const id=AR(2,k); inv[id]=1; equipArmor(id); } syncWear(); return armorPoints(); }", 1200)
        stage('armor_behind_3p', "()=>{ camMode=1; }", 1200)
        stage('gear_tab', "()=>{ camMode=0; openSheet('gear'); }", 400)
        pg.evaluate("()=>T.closeAll()")

        # ores, metal tools
        stage('ore_wall', """()=>{ const [x,z,h]=__P; mobs.length=0; const X=x, Y=h+1, Z=z+3; const ores=[IRON_ORE,ADAM_ORE,MITH_ORE,COAL,STONE]; for(let i=-2;i<=2;i++) for(let j=0;j<3;j++) setB(X+i,Y+j,Z,ores[i+2]);
            inv[MITH_PICK]=1; HOTBAR[0]=MITH_PICK; sel=0; [IRON_INGOT,ADAM_INGOT,MITH_INGOT,IRON_PICK,ADAM_PICK,MITH_SWORD,LEATHER,STEAK].forEach((id,i)=>{ inv[id]=3; HOTBAR[i+1]=id; }); syncWear(); updateHotbar();
            player.x=X+0.5; player.z=z-0.5; player.y=Y; T.face(X+0.5,Y+1.5,Z+0.5); }""", 1200)
        stage('tool_icons', """()=>{ const ids=[IRON_ORE,ADAM_ORE,MITH_ORE,IRON_INGOT,ADAM_INGOT,MITH_INGOT,...Array.from({length:15},(_,i)=>METAL_TOOL0+i),...Array.from({length:20},(_,i)=>1111+i)];
            const c=document.createElement('canvas'); c.width=1100; c.height=100; c.id='sheetC'; c.style.cssText='position:fixed;left:0;top:0;z-index:999;background:#3a3a3a;image-rendering:pixelated';
            const g=c.getContext('2d'); g.imageSmoothingEnabled=false; ids.forEach((id,i)=>g.drawImage(iconCanvas(id),(i%27)*40+4,Math.floor(i/27)*46+6,36,36)); document.body.appendChild(c); }""", 300, snap=False)
        import base64
        n[0] += 1; durl = pg.evaluate("()=>{ const c=document.getElementById('sheetC'), o=document.createElement('canvas'); o.width=c.width; o.height=c.height; const g=o.getContext('2d'); g.fillStyle='#3a3a3a'; g.fillRect(0,0,o.width,o.height); g.drawImage(c,0,0); return o.toDataURL(); }")
        open(os.path.join(OUT, '%02d_ores_tools_armor_icons.png' % n[0]), 'wb').write(base64.b64decode(durl.split(',')[1]))
        pg.evaluate("()=>document.getElementById('sheetC').remove()")
        stage('inventory_crafting', "()=>{ openCraft(3); }", 500)
        pg.evaluate("()=>T.closeAll()")

        # magic
        stage('spellmaker', "()=>{ inv[EMBER]=6; inv[CANDLE]=3; inv[CHITIN]=2; gold=900; openSpellmaker(); smFx='fire'; smPow=1; smMake(); smFx='heal'; smPow=0; smMake(); smFx='ward'; smPow=0; smMake(); smFx='bolt'; smPow=2; renderSpellmaker(); return book.map(bookName); }", 500)
        pg.evaluate("()=>T.closeAll()")
        stage('firebolt_action', """async ()=>{ const [x,z,h]=__P; T.clear(x,z,h,12); mobs.length=0; mp=mpMax(); const m=newBeast('bear',x+8,h+1,z); m.hp=1e4; mobs.push(m); player.x=x+0.5; player.z=z+0.5; player.y=h+1; T.face(m.x,h+1.2,m.z);
            spell=null; spellCharges=0; bookSel=0; castCool=0; castSpell(); await T.sleep(250); return {fx: fx.length, mp}; }""", 50)
        stage('sheet_magic_book', "()=>{ openSheet('magic'); }", 400)
        pg.evaluate("()=>T.closeAll()")

        # death and the sack
        stage('death_screen', "()=>{ mobs.length=0; const [x,z,h]=__P; T.clear(x,z,h,12); player.x=x+0.5; player.z=z+0.5; player.y=h+1; inv[COBBLE]=30; inv[STONE_PICK]=1; syncWear(); window.__dp=[player.x,player.z]; die(); }", 600)
        stage('sack_beam_day', """async ()=>{ respawn(); health=1000; await T.sleep(800); const s=deathSacks[deathSacks.length-1]; player.x=s.x-11; player.z=s.z; player.y=__P[2]+1; tod=0.3; T.face(s.x,s.y+3,s.z); return deathSacks.length; }""", 2500)
        stage('sack_beam_night', "()=>{ tod=0.8; }", 2500)
        pg.evaluate("()=>{ tod=0.3; }")

    # crypt outside & inside with undead
    C = stage('crypt_entrance', """async ()=>{ mobs.length=0; const C=cryptNear(0,0,900); if(!C.length) return 'none'; const P=C[0]; window.__C=P; player.x=P.ex+0.5; player.z=P.ez-7.5; player.y=P.h+1; await T.sleep(2000);
        T.face(P.ex+0.5,P.h+2,P.ez); return P.name+' @'+P.ex+','+P.ez; }""", 1500)
    pg.keyboard.down('KeyW'); pg.wait_for_timeout(15000); pg.keyboard.up('KeyW')
    stage('crypt_inside', "()=>{ const P=__C; return {pos:[+player.x.toFixed(1),+player.y.toFixed(1),+player.z.toFixed(1)], floor:P.F, inside: player.y<=P.F+1.5}; }", 600)
    stage('crypt_undead', """()=>{ const P=__C; for(const k of ['skeleton','zombie','ghost','cryptlord']){ BEAST[k]._ag=BEAST[k].aggro; BEAST[k].aggro=0; }
        mobs.length=0; const X=Math.floor(player.x), Y=Math.floor(player.y), Z=Math.floor(player.z); const ks=['skeleton','zombie','ghost','cryptlord']; let placed=0;
        for(let d=3; d<12 && placed<4; d++) for(let s=-2; s<=2 && placed<4; s+=2){ const x=X+s, z=Z+d; if(ratCanStand(x,Y,z) && PASS[getB(x,Y+1,z)] && PASS[getB(x,Y+2,z)]){ const m=newBeast(ks[placed],x+0.5,Y,z+0.5); m.idleT=999; m.angry=0; m.yaw=Math.PI; mobs.push(m); placed++; } }
        player.yaw=0; player.pitch=-0.1; let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; const v=camVectors().f; if(v[2]>bd){bd=v[2];ba=a;} } player.yaw=ba; return placed+' undead'; }""", 1500)
    pg.evaluate("()=>{ for(const k of ['skeleton','zombie','ghost','cryptlord']) if(BEAST[k]._ag!==undefined) BEAST[k].aggro=BEAST[k]._ag; mobs.length=0; }")

    # bats and fish
    stage('bats_cave', """async ()=>{ mobs.length=0; let P=null; for(let x=-300;x<300&&!P;x+=4) for(let z=-300;z<300;z+=4){ const h=colInfo(x,z).h; for(let y=8;y<h-8;y++){ if(blockAt(x,y,z)===AIR&&blockAt(x,y+1,z)===AIR&&blockAt(x,y+2,z)===AIR&&blockAt(x,y+3,z)===AIR&&!PASS[blockAt(x,y-1,z)]){ P=[x,y,z]; break; } } if(P) break; }
        if(!P) return 'no cave'; player.x=P[0]+0.5; player.y=P[1]; player.z=P[2]+0.5; await T.sleep(1500); for(let i=0;i<4;i++){ const m=newBeast('bat',P[0]+2+i*0.8,P[1]+2,P[2]+2+i*0.5); mobs.push(m); } T.face(P[0]+3,P[1]+2,P[2]+3); return P; }""", 1200)
    stage('torch_light_cave', "()=>{ }", 200, snap=False)
    stage('slaughterfish', """async ()=>{ mobs.length=0; let L=null; for(let x=-400;x<400&&!L;x+=6) for(let z=-400;z<400;z+=6){ const c=colInfo(x,z); if(c.h<SEA-4 && getB(x,SEA,z)!==AIR){ L=[x,z,c.h]; break; } } if(!L) return 'no lake';
        player.x=L[0]+0.5; player.z=L[1]+0.5; player.y=SEA-1; await T.sleep(1500); for(let i=0;i<3;i++){ const f=newBeast('fish',L[0]+2+i,SEA-2,L[1]+3); f.angry=0; mobs.push(f); } T.face(L[0]+3,SEA-2,L[1]+3); return L; }""", 1200)

    # underworld
    stage('underworld', """async ()=>{ mobs.length=0; let P=null; for(let x=0;x<400&&!P;x+=4){ const z=UNDER_Z+40, c=underCol(x,z); if(c.hf>UNDER_LAVA+3 && c.hc-c.hf>14){ let ok=true; for(let a=-6;a<=6;a+=3) if(Math.abs(underCol(x+a,z).hf-c.hf)>1) ok=false; if(ok) P=[x,z,c.hf]; } }
        if(!P) return 'no site'; const [x,z,hf]=P; player.x=x+0.5; player.z=z+0.5; player.y=hf+1; await T.sleep(2500); mobs.length=0; window.__U=P;
        BEAST.daedra._ag=BEAST.daedra.aggro; BEAST.daedroth._ag=BEAST.daedroth.aggro; BEAST.daedra.aggro=0; BEAST.daedroth.aggro=0;
        const d=newBeast('daedra',x+6,hf+1,z-1), r=newBeast('daedroth',x+6,hf+1,z+2); d.idleT=r.idleT=999; d.angry=r.angry=0; mobs.push(d,r); T.face(x+6,hf+2,z+0.5); return P; }""", 1500)
    stage('underworld_fireball_action', """async ()=>{ BEAST.daedra.aggro=BEAST.daedra._ag; BEAST.daedroth.aggro=BEAST.daedroth._ag; const [x,z,hf]=__U; mobs.length=0; health=1000; const d=newBeast('daedra',x+8,hf+1,z); d.angry=30; mobs.push(d);
        for(let i=0;i<70;i++){ await T.sleep(200); T.face(d.x,d.y+1,d.z); if(fx.some(e=>e.enemy)) break; } await T.sleep(300); T.face(d.x,d.y+1,d.z); return {enemyFx: fx.filter(e=>e.enemy).length, hurt: 1000-health, d:[+d.x.toFixed(1),+d.z.toFixed(1),d.angry>0,d.dead,d.shotCd], st:{paused,craftOpen,dead,inMobs:mobs.includes(d),n:mobs.length, kinds:mobs.map(m=>m.kind).join(), py:player.y, dy:d.y}}; }""", 50)
    stage('underworld_map', "()=>{ mobs.length=0; openMap(); }", 600)
    pg.evaluate("()=>T.closeAll()")

    # test hall
    stage('test_hall', "()=>{ mobs.length=0; testGoHall(); }", 3000)

    # night in the village, rain
    stage('village_night', """()=>{ mobs.length=0; const v=nearestVillage(2); player.x=v.cx+0.5; player.z=v.cz+10.5; player.y=colInfo(v.cx,v.cz+10).h+3; tod=0.82; T.face(v.cx,player.y,v.cz-6); }""", 3500)
    stage('village_rain', "()=>{ tod=0.35; rainMode='on'; rainOn=true; }", 3500)
    pg.evaluate("()=>{ rainMode='off'; rainOn=false; }")

    # wagon travel
    stage('wagon_travel', """async ()=>{ const v=[...visitedV]; gold=500; openMap(); const side=document.getElementById('mapSide').textContent.slice(0,160); return {visited: v.length, side}; }""", 500)
    pg.evaluate("()=>T.closeAll()")

    # performance sample + save
    perf = pg.evaluate("""async ()=>{ const v=nearestVillage(2); player.x=v.cx+0.5; player.z=v.cz+5.5; player.y=colInfo(v.cx,v.cz+5).h+1; await T.sleep(3000); const f=await T.fps(3000);
        const t0=performance.now(); saveWorld(); const sv=performance.now()-t0; let ls=0; for(let i=0;i<localStorage.length;i++){ const k=localStorage.key(i); ls+=k.length+localStorage.getItem(k).length; }
        return {fps_headless:f, save_ms:+sv.toFixed(1), localStorage_kb: Math.round(ls/1024), mobs: mobs.length, chunks: (typeof chunks!=='undefined'&&chunks.size)||null}; }""")
    log.append(('perf', perf))

    b.close()

open('/tmp/tour_log.json','w').write(json.dumps(log, indent=1, default=str)); print(json.dumps(log, default=str)[:6000])
print('ALL ERRORS:', json.dumps(errs[:30]))
