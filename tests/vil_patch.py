p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
i=s.index("const NPC_MAX = 3, NPC_WALK = 0.04, NPC_HP = 20;"); j=s.index("// ---------- rats: the first animal ----------")
s=s[:i]+r'''// ---------- villagers: everyone in a village lives in one of its houses and is tied to their bed ----------
// When you come near a village its people are there: by day they go about the village (guards patrol it), at night they go home.
// Anyone who dies comes back in their own bed at the next sunrise, so a quest giver or shopkeeper is never lost for good; if their bed
// has been broken they leave the village instead. Everyone fights hostile creatures inside the village; guards hunt them down.
// Hit a villager and the guards come after you.
const NPC_WALK = 0.04, NPC_RUN = 0.085, NPC_HP = 20, GUARD_HP = 34;
const NPCS_IN_WORLD = true;
let npcSpawnT = 1, villagerState = {};                       // per-resident record: { dead:1 } until sunrise, { gone:1 } once their bed is gone
let npcPathing = false;                                      // while true, closed doors count as walkable (villagers open them)
function npcAllowed(x,y,z){ return true; }
function npcHostile(o){ return !o.dead && (BEAST[o.kind] || o.kind==='rat' || IS_BRUTE(o.kind)); }
// the villages whose regions are around the player
function nearbyVillages(){
  const out = [], rx = Math.floor(player.x/VREG), rz = Math.floor(player.z/VREG);
  for(let a=-1;a<=1;a++) for(let b=-1;b<=1;b++){ const v = villageAt(rx+a, rz+b); if(v && v.houses) out.push([rx+a, rz+b, v]); }
  return out;
}
function newNpc(x,y,z,ch){
  ch = ch || npcGenerate();
  const guard = ch.job==='guard';
  return { id:mobId++, kind:'npc', x:x+0.5, y, z:z+0.5, yaw:Math.random()*6.28, hp:guard?GUARD_HP:NPC_HP, ch, name:ch.name, job:ch.job, model:bodyModel(ch),
           pose:{c:1,s:0,hd:0,hp:0,ra:0,la:0,rl:0,ll:0}, res:{t:0,nx:0,ny:0,nz:0,col:null,lx:0,ly:0,lz:0,glow:false},
           state:'idle', idleT:Math.random()*3, path:null, pi:0, replanT:0, angry:0, atkCd:0, hurtT:0, iframe:0, dead:false, deadT:0, fleeT:0,
           phase:Math.random()*6, age:Math.random()*10, moving:false, kx:0, kz:0, stuckT:0, limb:0, hx:Math.floor(x), hz:Math.floor(z), swing:0, foeT:0 };
}
function trySpawnNpcs(){
  if(isUnder(player.z) || isTestZ(player.z)) return;
  for(const [rx,rz,v] of nearbyVillages()){
    v.houses.forEach((h,i)=>{
      const key = rx+','+rz+':'+i, st = villagerState[key];
      if(st && (st.dead || st.gone)) return;
      if(Math.hypot(h.out[0]+0.5-player.x, h.out[2]+0.5-player.z) > 56) return;
      if(mobs.some(m=>m.home===key)) return;
      const at = ratNight && h.job!=='guard' ? h.inside : h.out;
      if(!npcCanStand(at[0],at[1],at[2])) return;                                   // not loaded yet
      // the resident is always the same person: their looks come from the village seed and the house number
      const rnd = vRng(Math.floor(h3(rx*31+i, 77, rz*17+i, SEED+520)*4294967295));
      const job = h.job==='villager' && i===0 ? 'guard' : h.job;                    // every village has at least one guard
      const m = newNpc(at[0],at[1],at[2], npcGenerate(rnd, v.houses.some(q=>q.job==='guard') ? h.job : job));
      m.home = key; m.house = h; m.village = [rx,rz]; m.vc = villageCentre(v);
      mobs.push(m);
    });
  }
}
function villageCentre(v){ let x=0,z=0; for(const h of v.houses){ x+=h.out[0]; z+=h.out[2]; } return [x/v.houses.length, z/v.houses.length]; }
function npcCanStand(x,y,z){ npcPathing = true; const r = ratCanStand(x,y,z); npcPathing = false; return r; }
function npcPath(m, goal, n){ npcPathing = true; const p = ratPath(Math.floor(m.x),Math.round(m.y),Math.floor(m.z), goal, null, n||400); npcPathing = false; return p; }
// sunrise: the dead come back in their beds, if they still have one
function villagerDawn(){
  for(const k in villagerState){
    const st = villagerState[k]; if(!st.dead) continue;
    const [r, i] = k.split(':'), [rx,rz] = r.split(',').map(Number), v = villageAt(rx,rz), h = v && v.houses[+i];
    if(!h){ delete villagerState[k]; continue; }
    const c = chunks.get(chunkKey(Math.floor(h.bed[0]/CS), Math.floor(h.bed[2]/CS)));
    if(c && !IS_BED[getB(h.bed[0],h.bed[1],h.bed[2])]) villagerState[k] = { gone:1 };      // no bed to wake up in: they have left
    else delete villagerState[k];
  }
  scheduleSave();
}
function npcHit(m, dmg){                                         // you hit a villager: they get hurt, and the guards turn on you
  if(m.dead || m.iframe>0) return;
  m.hp -= dmg; m.hurtT = 0.3; m.iframe = 0.3;
  const dx=m.x-player.x, dz=m.z-player.z, d=Math.hypot(dx,dz)||1; m.kx = dx/d*0.18; m.kz = dz/d*0.18;
  if(m.job==='guard') m.angry = 30; else { m.fleeT = 5; m.path = null; m.replanT = 0; }
  for(const o of mobs) if(o.kind==='npc' && o.job==='guard' && !o.dead && Math.hypot(o.x-m.x,o.z-m.z)<32) o.angry = 30;
  if(m.hp<=0){ m.dead = true; m.deadT = 0; m.path = null; }
}
// open a closed door the villager is about to walk through, and shut it again once they're past
function npcDoors(m){
  if(m.door){ const [x,y,z] = m.door, b = getB(x,y,z);
    if(Math.hypot(x+0.5-m.x, z+0.5-m.z)>1.6){ if(IS_DOOR[b] && SH_OPEN[b] && !(Math.floor(player.x)===x && Math.floor(player.z)===z)) npcToggleDoor(x,y,z); m.door = null; } }
  if(!m.path || m.pi>=m.path.length) return;
  for(let k=m.pi; k<Math.min(m.pi+2, m.path.length); k++){
    const [x,y,z] = m.path[k], b = getB(x,y,z);
    if(IS_DOOR[b] && !SH_OPEN[b] && Math.hypot(x+0.5-m.x, z+0.5-m.z)<1.8){ npcToggleDoor(x,y,z); m.door = [x,y,z]; break; }
  }
}
function npcToggleDoor(x,y,z){ const sw = swingT; toggleDoor(x,y,z); swingT = sw; }
function npcWalk(m, speed){ npcDoors(m); return ratWalk(m, speed); }
function npcFindFoe(m){
  const range = m.job==='guard' ? 20 : 8, vc = m.vc; let best = null, bd = range;
  for(const o of mobs){
    if(!npcHostile(o)) continue;
    const d = Math.hypot(o.x-m.x, o.z-m.z);
    if(d<bd && Math.abs(o.y-m.y)<5 && (!vc || Math.hypot(o.x-vc[0], o.z-vc[1])<48)){ bd = d; best = o; }     // only inside the village
  }
  return best;
}
function npcChase(m, tx, ty, tz, dt){
  m.replanT -= dt;
  if(m.replanT<=0 || !m.path || m.pi>=m.path.length){
    m.replanT = 0.5+Math.random()*0.2;
    const p = npcPath(m, (x,y,z)=>Math.hypot(x+0.5-tx,z+0.5-tz)<1.3 && Math.abs(y-ty)<2, 500);
    if(p) ratSetPath(m,p); else m.path = null;
  }
  if(m.path && npcWalk(m, NPC_RUN)) return true;
  const dx=tx-m.x, dz=tz-m.z, d=Math.hypot(dx,dz)||1, st=Math.min(d, NPC_RUN*frameScale), nx=m.x+dx/d*st, nz=m.z+dz/d*st;
  if(npcCanStand(Math.floor(nx),Math.round(m.y),Math.floor(nz))){ m.x=nx; m.z=nz; m.moving=true; m.phase+=st*5; m.yaw=Math.atan2(dx,-dz); return true; }
  return false;
}
function npcGoTo(m, at, dt, speed){
  if(Math.hypot(at[0]+0.5-m.x, at[2]+0.5-m.z)<0.9 && Math.abs(at[1]-m.y)<1.2) return false;
  m.replanT -= dt;
  if(!m.path || m.pi>=m.path.length){
    if(m.replanT>0) return false;
    m.replanT = 2;
    const p = npcPath(m, (x,y,z)=>x===at[0] && z===at[2] && Math.abs(y-at[1])<=1, 1500);
    if(p) ratSetPath(m,p); else return false;
  }
  return npcWalk(m, speed);
}
function updateNpc(m, dt){
  let walking = false;
  m.swing = Math.max(0, m.swing - dt*3);
  const guard = m.job==='guard', dmg = guard ? 4 : 2;
  m.foeT -= dt; if(m.foeT<=0){ m.foeT = 0.5; m.foe = m.fleeT>0 ? null : npcFindFoe(m); }
  if(m.foe && (m.foe.dead || !mobs.includes(m.foe))) m.foe = null;
  if(dead) m.angry = 0;
  if(m.angry>0){                                                                       // a guard after you
    m.angry -= dt;
    const dxp=player.x-m.x, dzp=player.z-m.z;
    if(Math.hypot(dxp,dzp)<1.5 && Math.abs(player.y-m.y)<1.6){ m.moving=false; m.yaw=Math.atan2(dxp,-dzp); if(m.atkCd<=0){ hurt(3); m.atkCd = 1.1; m.swing = 1; } }
    else walking = npcChase(m, player.x, player.y, player.z, dt);
  } else if(m.foe){                                                                    // a hostile creature in the village
    const o = m.foe, dxp=o.x-m.x, dzp=o.z-m.z;
    if(Math.hypot(dxp,dzp)<1.6 && Math.abs(o.y-m.y)<1.6){
      m.moving=false; m.yaw=Math.atan2(dxp,-dzp);
      if(m.atkCd<=0){ mobDamage(o, dmg, m); if(BEAST[o.kind] && !o.dead) o.npcFoe = m; m.atkCd = 1.0; m.swing = 1; }
    } else walking = npcChase(m, o.x, o.y, o.z, dt);
  } else if(m.fleeT>0){                                                                // hurt: back away from you
    m.fleeT -= dt; m.replanT -= dt;
    if(m.replanT<=0 || !m.path || m.pi>=m.path.length){
      m.replanT = 0.7;
      const p = npcPath(m, (x,y,z)=>Math.hypot(x+0.5-player.x,z+0.5-player.z)>12, 300);
      if(p) ratSetPath(m,p); else m.path=null;
    }
    walking = npcWalk(m, NPC_RUN);
  } else if(m.house && ratNight && !guard){                                            // night: home to bed
    walking = npcGoTo(m, m.house.inside, dt, NPC_WALK*1.4);
    if(!walking){ m.state = 'home'; if(Math.random()<dt*0.2) m.yaw += (Math.random()-0.5)*2; }
  } else if(m.state==='idle' || m.state==='home'){
    m.moving=false; m.idleT -= dt;
    if(m.idleT<=0){
      let tx, tz;
      if(guard && m.vc && Math.random()<0.7){ const h = m.house && Math.random()<0.3 ? m.house : null, vv = villageAt(m.village[0], m.village[1]);
        const q = h || vv.houses[Math.floor(Math.random()*vv.houses.length)]; tx = q.out[0]+0.5+(Math.random()-0.5)*6; tz = q.out[2]+0.5+(Math.random()-0.5)*6; }   // guards walk the rounds
      else if(m.house && Math.random()<0.25){ tx = m.house.inside[0]+0.5; tz = m.house.inside[2]+0.5; }     // pop home for a bit
      else { const a=Math.random()*6.283, d=2+Math.random()*7, b = m.house ? m.house.out : [m.hx,0,m.hz]; tx=b[0]+0.5+Math.cos(a)*d; tz=b[2]+0.5+Math.sin(a)*d; }
      const cy = Math.round(m.y);
      const p = npcPath(m, (x,y,z)=>Math.hypot(x+0.5-tx,z+0.5-tz)<1.6 && Math.abs(y-cy)<=4, 700);
      if(p){ ratSetPath(m,p); m.state='wander'; } else { m.state='idle'; m.idleT = 1+Math.random()*3; }
    }
  } else {
    walking = npcWalk(m, NPC_WALK);
    if(!walking){ m.state='idle'; m.idleT = 2+Math.random()*6; }
  }
  if(!walking) m.moving=false;
  if(m.door && !walking) npcDoors(m);
  // pose: limbs swing while walking, the right arm strikes when fighting, and the head turns to watch you when you are close
  const P = m.pose;
  m.limb += ((m.moving?1:0) - m.limb)*Math.min(1,0.25*frameScale);
  P.c = Math.cos(m.yaw); P.s = Math.sin(m.yaw);
  const sw = Math.sin(m.phase*1.15) * 0.95 * m.limb;
  P.ra = m.swing>0 ? -2.2*Math.sin(m.swing*Math.PI) : sw; P.la = -sw; P.rl = -sw; P.ll = sw;
  const dxp=player.x-m.x, dzp=player.z-m.z, dp=Math.hypot(dxp,dzp);
  let hd=0, hp=0;
  if(dp<9 && Math.abs(player.y-m.y)<5 && !m.foe){
    const want = Math.atan2(dxp,-dzp); let rel = want - m.yaw; rel = Math.atan2(Math.sin(rel), Math.cos(rel));
    hd = Math.max(-1.1, Math.min(1.1, rel)); hp = Math.max(-0.5, Math.min(0.5, Math.atan2((player.y+1.6)-(m.y+1.6), dp)));
  }
  P.hd += (hd-P.hd)*Math.min(1,0.15*frameScale); P.hp += (hp-P.hp)*Math.min(1,0.15*frameScale);
}
'''+s[j:]
# doors walkable for villagers
rep("function ratCanStand(x,y,z){\n  const b = ratGet(x,y,z);\n  if(!PASS[b] || IS_WATER[b] || IS_LAVA[b]) return false;",
    "function ratCanStand(x,y,z){\n  const b = ratGet(x,y,z);\n  if((!PASS[b] && !(npcPathing && IS_DOOR[b])) || IS_WATER[b] || IS_LAVA[b]) return false;")
# deaths recorded; respawn at dawn
rep("    if(m.dead){ m.deadT += dt; if(m.deadT>0.5){ mobs.splice(i,1); } continue; }",
    "    if(m.dead){ if(m.home && !m.noted){ m.noted = true; villagerState[m.home] = { dead:1 }; scheduleSave(); } m.deadT += dt; if(m.deadT>0.5){ mobs.splice(i,1); } continue; }")
rep("    if(wrapped) rainDawn(false);\n  }", "    if(wrapped) rainDawn(false);\n  }\n  if(wrapped) villagerDawn();")
rep("  if(NPCS_IN_WORLD){ npcSpawnT -= dt; if(npcSpawnT<=0){ npcSpawnT = 12; trySpawnNpcs(); } }", "  if(NPCS_IN_WORLD){ npcSpawnT -= dt; if(npcSpawnT<=0){ npcSpawnT = 3; trySpawnNpcs(); } }")
# beasts fight back against villagers who hit them
rep("  if(m.angry>0){\n    m.angry -= dist > K.aggro*2.5+8 ? dt*3 : dt*0.2;",
    """  if(m.npcFoe && (m.npcFoe.dead || !mobs.includes(m.npcFoe))) m.npcFoe = null;
  if(m.npcFoe && m.angry<=0){                                                          // a villager is fighting it: it fights back
    const o = m.npcFoe, dx = o.x-m.x, dz = o.z-m.z;
    if(Math.hypot(dx,dz)<K.reach && Math.abs(o.y-m.y)<1.6){ m.moving=false; m.yaw=Math.atan2(dx,-dz); if(m.atkCd<=0){ mobDamage(o, K.bite, m); m.atkCd = K.cd; m.atkA = 1; } return; }
    m.replanT -= dt;
    if(m.replanT<=0 || !m.path || m.pi>=m.path.length){ m.replanT = 0.5; const p = ratPath(cx,cy,cz,(x,y,z)=>Math.hypot(x+0.5-o.x,z+0.5-o.z)<1.2 && Math.abs(y-o.y)<2, null, 400); if(p) ratSetPath(m,p); else m.path = null; }
    if(m.path && ratWalk(m, K.run)) return;
  }
  if(m.angry>0){
    m.angry -= dist > K.aggro*2.5+8 ? dt*3 : dt*0.2;""")
# save / load
rep("tod, health, food, saturation, skills:{ v:skills, u:skillUses, g:skillGained },", "tod, health, food, saturation, skills:{ v:skills, u:skillUses, g:skillGained }, gold, villagers:villagerState,")
rep("  resetSkills(); if(meta.skills){", "  gold = meta.gold || 0; villagerState = meta.villagers || {};\n  resetSkills(); if(meta.skills){")

# ---------- gold ----------
rep("const LEATHER = 1081, RAW_MEAT = 1082, STEAK = 1083, SILK = 1084, CHITIN = 1085, MEAT_STEW = 1086;",
    "const LEATHER = 1081, RAW_MEAT = 1082, STEAK = 1083, SILK = 1084, CHITIN = 1085, MEAT_STEW = 1086, GOLD = 1087;\nlet gold = 0;                                               // gold pieces: kept in a purse, not in the inventory (like Daggerfall)")
rep("[MEAT_STEW,'meat stew',[132,74,42]]]", "[MEAT_STEW,'meat stew',[132,74,42]],[GOLD,'gold pieces',[236,196,64]]]")
rep("SHORT[LEATHER]='leather';", "SHORT[GOLD]='gold'; SHORT[LEATHER]='leather';")
rep("    case LEATHER: paintIcon(g,(P,E)=>{", """    case GOLD: paintIcon(g,(P,E)=>{ for(const [cx,cy] of [[5,11],[11,11],[8,8],[6,6],[10,5]]){ E(cx,cy,3.2,2.2,null,(x,y,dx,dy)=>dy<-0.2 ? [255,232,130] : dy>0.5 ? [176,128,30] : [236,196,64]); P(cx-1,cy-1,[255,248,200]); } }); return true;
    case LEATHER: paintIcon(g,(P,E)=>{""")
rep("        inv[e.id] = Math.min(99, (inv[e.id]||0)+1);\n        autoFillHotbar(e.id);",
    "        if(e.id===GOLD){ gold += e.n||1; skillToast('+'+(e.n||1)+' gold'); scheduleSave(); itemDrops.splice(i,1); continue; }\n        inv[e.id] = Math.min(99, (inv[e.id]||0)+1);\n        autoFillHotbar(e.id);")
rep("id=>{ inv[id] = Math.min(999, (inv[id]||0) + items[id]); delete items[id];", "id=>{ if(id===GOLD){ gold += items[id]; skillToast('+'+items[id]+' gold'); } else inv[id] = Math.min(999, (inv[id]||0) + items[id]); delete items[id];")
rep("  house:   [", "  house:   [[GOLD,2,15,.6],")
rep("  dungeon: [", "  dungeon: [[GOLD,15,80,.85],")
rep("  under:   [", "  under:   [[GOLD,20,120,.8],")
rep("    else if(m.kind==='mino'){ drop(EMBER", "    if(m.kind==='mino' || m.kind==='ogre') spawnGold(dx,dy,dz, m.kind==='ogre' ? 60+Math.floor(Math.random()*90) : 30+Math.floor(Math.random()*50));\n    if(m.kind==='mino'){ drop(EMBER")
rep("function spawnDrop(x,y,z,id){", "function spawnGold(x,y,z,n){ spawnDrop(x,y,z,GOLD); itemDrops[itemDrops.length-1].n = n; }\nfunction spawnDrop(x,y,z,id){")
rep("  let h = `<div class=\"skLvl\">LEVEL ${L}<span>${maxHP()/2} hearts</span></div>", "  let h = `<div class=\"skLvl\">LEVEL ${L}<span>${maxHP()/2} hearts &nbsp;<b style=\"color:#ecc440\">${gold} gold</b></span></div>")
open(p,'w').write(s); print('ok')
