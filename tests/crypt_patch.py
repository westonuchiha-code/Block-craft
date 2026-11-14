p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# ---------- crypt layout (terrain) ----------
mod = r'''
// ---------- crypts: barrows of the old dead, out in the wild (worlds made from now on) ----------
// A small mossy stone hut stands on the surface; inside, slab steps lead ten blocks down to a corridor with burial rooms either
// side and a great hall at the end, where the Crypt Lord waits. Skeletons, zombies and ghosts walk the halls; the chests hold
// the best loot outside the underworld. Kill the Crypt Lord and the crypt falls quiet for good.
const CRS = 160, CRYPT_D = 10;
const CRYPT_NAMES = ['Aldric','Morwen','Hrothgar','Ysolde','Beren','Calder','Edda','Gorm','Isolt','Varric','Wulfstan','Maelis'];
const cryptCache = new Map();
function cryptPlan(rx,rz){
  const key = rx+','+rz; let P = cryptCache.get(key); if(P!==undefined) return P;
  P = null;
  if(worldGen>=4 && !isUnder(rz*CRS) && !isTestZ(rz*CRS) && h3(rx,51,rz,SEED+800) < 0.55){
    for(let t=0;t<5 && !P;t++){
      const ex = rx*CRS + 30 + Math.floor(h3(rx,52+t,rz,SEED+801)*(CRS-60)), ez = rz*CRS + 30 + Math.floor(h3(rx,57+t,rz,SEED+802)*(CRS-90));
      const ci = colInfo(ex,ez), h = ci.h;
      if(ci.open || h<=SEA+3 || h-CRYPT_D<5 || !(ci.top===GRASS || ci.top===SNOW || ci.top===SAND || ci.top===STONE)) continue;
      let flat = true; for(let a=-3;a<=3 && flat;a+=3) for(let b=-3;b<=3;b+=3) if(Math.abs(colInfo(ex+a,ez+b).h-h)>1){ flat = false; break; }
      if(!flat || villageNoTree(ex,ez) || nearVillage(ex,ez) || nearRoad(ex,ez)) continue;
      const F = h - CRYPT_D;                       // the crypt floor (the top of the floor blocks)
      const air = [];                              // interior boxes: [x0,x1,y0,y1,z0,z1] (inclusive)
      air.push([ex-2,ex+2,h+1,h+4,ez-2,ez+2]);      // the hut
      air.push([ex,ex,h+1,h+2,ez-3,ez-3]);          // its doorway
      const zs = ez+2, zc = zs + CRYPT_D*2;         // the stair starts inside the hut and ends at zc
      const L = 34, rooms = [], chestsP = [], spawns = [];
      air.push([ex-1,ex+1,F+1,F+3,zc,zc+L]);         // the corridor
      for(let k=0;k<3;k++){ const zr = zc+6+k*11, side = (k%2 ? 1 : -1), cx = ex + side*6;
        rooms.push([cx-3,cx+3,F+1,F+4,zr-3,zr+3]); air.push(rooms[k]); air.push([Math.min(ex+side*2,ex+side*2),Math.max(ex+side*2,ex+side*2),F+1,F+2,zr,zr]);
        chestsP.push([cx+side*3, F+1, zr]); spawns.push([cx,F+1,zr-1],[cx,F+1,zr+1]); }
      const hz = zc+L+1, hall = [ex-5,ex+5,F+1,F+5,hz,hz+8]; air.push(hall);
      chestsP.push([ex-5,F+1,hz+8],[ex+5,F+1,hz+8]); spawns.push([ex-1,F+1,zc+4],[ex+1,F+1,zc+20],[ex-3,F+1,hz+3]);
      P = { key, ex, ez, h, F, zs, zc, air, chestSet:new Set(chestsP.map(c=>c.join(','))), spawns, boss:[ex,F+1,hz+5], name:'Barrow of '+CRYPT_NAMES[Math.floor(h3(rx,61,rz,SEED+803)*CRYPT_NAMES.length)],
            bb:[ex-8, ex+8, F-1, h+6, ez-5, hz+10] };
    }
  }
  cryptCache.set(key,P); return P;
}
function cryptBlock(x,y,z){
  if(worldGen<4) return -1;
  const P = cryptPlan(Math.floor(x/CRS), Math.floor(z/CRS)); if(!P) return -1;
  const B = P.bb; if(x<B[0]||x>B[1]||y<B[2]||y>B[3]||z<B[4]||z>B[5]) return -1;
  // the stair: slab half-steps down the middle three columns, a block every two cells
  if(z>=P.zs && z<P.zc && Math.abs(x-P.ex)<=2){
    const i = z-P.zs, s2 = 2*P.h - i;              // twice the walking surface height
    const top = s2>>1, half = s2&1;                 // surface at top (+0.5 if half)
    if(Math.abs(x-P.ex)<=1){
      if(y<top) return y>=top-2 ? STONE_BRICK : -1;
      if(y===top) return half ? slabId(6,0) : (y<=P.h ? AIR : AIR);
      if(y<=top+3) return y<=P.h+4 || z<=P.ez+2 ? AIR : -1;
      if(y===top+4) return STONE_BRICK;
      return -1;
    }
    if(y>=top-2 && y<=top+4) return MOSSY_BRICK;      // the stair walls
    return -1;
  }
  for(const A of P.air) if(x>=A[0]&&x<=A[1]&&y>=A[2]&&y<=A[3]&&z>=A[4]&&z<=A[5]){
    if(P.chestSet.has(x+','+y+','+z)) return CHEST;
    if(y===A[2] && (x===A[0]||x===A[1]) && h3(x,y,z,SEED+810)<0.18 && y<P.h) return BONE;            // bones heaped along the walls
    return AIR;
  }
  for(const A of P.air) if(x>=A[0]-1&&x<=A[1]+1&&y>=A[2]-1&&y<=A[3]+1&&z>=A[4]-1&&z<=A[5]+1){
    if(y===A[3]+1 && (x+z)%6===0 && y<P.h) return GLOW;                                              // a few lights in the ceilings
    if(y>P.h && y===A[3]+1) return slabId(6,0);                                                       // the hut's roof
    return h3(x,y,z,SEED+811)<0.35 ? MOSSY_BRICK : y===A[2]-1 ? COBBLE : STONE_BRICK;
  }
  return -1;
}
function cryptNear(x,z,r){
  const out = [], R = Math.ceil(r/CRS)+1, rx = Math.floor(x/CRS), rz = Math.floor(z/CRS);
  for(let a=-R;a<=R;a++) for(let b=-R;b<=R;b++){ const P = cryptPlan(rx+a,rz+b); if(P && Math.hypot(P.ex-x,P.ez-z)<=r) out.push(P); }
  return out.sort((p,q)=>Math.hypot(p.ex-x,p.ez-z)-Math.hypot(q.ex-x,q.ez-z));
}
'''
rep("// dungeon hall for region (rx,rz): returns a block type, or -1 if this block isn't part of a hall", mod+"// dungeon hall for region (rx,rz): returns a block type, or -1 if this block isn't part of a hall")
rep("  const hb = hallBlock(x,y,z);\n", "  const hb = hallBlock(x,y,z);\n  if(hb===-1){ const cb = cryptBlock(x,y,z); if(cb!==-1) return cb; }\n")
# trees and the like stay off crypt huts: treat as village-like no-tree zone
rep("function villageNoTree(x,z){\n  if(worldGen<2) return false;", "function villageNoTree(x,z){\n  if(worldGen<2) return false;\n  if(worldGen>=4){ const P = cryptCache.get(Math.floor(x/CRS)+','+Math.floor(z/CRS)); if(P && Math.abs(x-P.ex)<=7 && Math.abs(z-P.ez)<=7) return true; }")
# crypt chests
s = s.replace("tier = isUnder(z) ? 'under' : v && v.chests.get(key);", "tier = isUnder(z) ? 'under' : (v && v.chests.get(key)) || (worldGen>=4 && (()=>{ const P = cryptPlan(Math.floor(x/CRS), Math.floor(z/CRS)); return P && P.chestSet.has(key) ? 'crypt' : null; })());",1)
assert "'crypt' : null" in s
rep("  under:   [[GOLD,20,120,.8],", "  crypt:   [[GOLD,25,90,.9],[IRON_INGOT,1,4,.5],[ADAM_INGOT,1,2,.14],[MITH_INGOT,1,1,.04],[FIRE_POTION,1,2,.4],[BOLT_POTION,1,2,.4],[CANDLE,1,3,.5],[BONE,2,5,.6],[AR(2,0),1,1,.12],[AR(2,3),1,1,.12],[AR(1,1),1,1,.1],[IRON_SWORD,1,1,.15],[CROSSBOW,1,1,.1]],\n  under:   [[GOLD,20,120,.8],")
# ---------- the undead ----------
rep("  scorpion: { hp:20, bite:3, cd:1.3,", """  skeleton: { hp:16, bite:3, cd:1.1, walk:0.035, run:0.09, aggro:14, memory:20, reach:1.6, tall:1.9, br:1.6, rect:1.9, max:3, group:[1,2], weight:1.2, night:true, undead:true,
              where:(b,y)=>true, drops:[[BONE,1,3]] },
  zombie:   { hp:22, bite:4, cd:1.3, walk:0.025, run:0.06, aggro:12, memory:25, reach:1.6, tall:1.9, br:1.6, rect:1.9, max:3, group:[1,3], weight:1.2, night:true, undead:true,
              where:(b,y)=>b<=4, drops:[[BONE,0,1]], gold:[2,9] },
  ghost:    { hp:12, bite:3, cd:1.0, walk:0.03, run:0.08, aggro:12, memory:20, reach:1.6, tall:1.9, br:1.6, rect:1.9, max:0, group:[1,1], weight:0, undead:true,
              where:()=>false, drops:[[GLOWMOSS,1,2]] },
  cryptlord:{ hp:70, bite:6, cd:1.25, walk:0.03, run:0.075, aggro:16, memory:60, reach:2.1, tall:2.5, br:2.3, rect:2.4, max:0, group:[1,1], weight:0, undead:true,
              where:()=>false, drops:[[EMBER,1,2],[BONE,3,5]], gold:[80,150] },
  scorpion: { hp:20, bite:3, cd:1.3,""")
rep("    for(const [id,lo,hi] of K.drops) for(let n=roll(lo,hi)+(isClass('ranger')?1:0); n>0; n--) spawnDrop(x,y,z,id);",
    """    for(const [id,lo,hi] of K.drops) for(let n=roll(lo,hi)+(isClass('ranger') && !K.undead ? 1 : 0); n>0; n--) spawnDrop(x,y,z,id);
    if(K.gold) spawnGold(x,y,z,roll(K.gold[0],K.gold[1]));
    if(m.kind==='cryptlord'){ spawnDrop(x,y,z, Math.random()<0.25 ? MITH_INGOT : ADAM_INGOT); spawnDrop(x,y,z, ADAM_INGOT); cryptCleared(m.crypt); }""")
rep("  if(K.night && !ratNight && !isTestZ(m.z)){ m.dayT += dt;", "  if(K.night && !ratNight && !isTestZ(m.z) && !m.crypt){ m.dayT += dt;")
rep("const p = ratPath(cx,cy,cz,(x,y,z)=>Math.hypot(x+0.5-player.x,z+0.5-player.z)<1.2 && Math.abs(y-player.y)<2, beastAllowed, 500);",
    "const p = ratPath(cx,cy,cz,(x,y,z)=>Math.hypot(x+0.5-player.x,z+0.5-player.z)<1.2 && Math.abs(y-player.y)<2, K.undead ? null : beastAllowed, 500);")
rep("const p = ratPath(cx,cy,cz,(x,y,z)=>Math.hypot(x+0.5-tx,z+0.5-tz)<1.6 && Math.abs(y-cy)<=3, beastAllowed, 300);",
    "const p = ratPath(cx,cy,cz,(x,y,z)=>Math.hypot(x+0.5-tx,z+0.5-tz)<1.6 && Math.abs(y-cy)<=3, K.undead ? null : beastAllowed, 300);")
# models
rep("  if(hurtF) for(const b of out) b.col = [Math.min(255,b.col[0]+70), b.col[1]*0.6, b.col[2]*0.6];", r"""  else if(BEAST[m.kind].undead){
    // humanoids: legs, body, arms, head. Skeletons are all bone; zombies shamble with their arms out; ghosts float, legless and glowing
    const k = m.kind, S = k==='cryptlord' ? 1.3 : 1, gh = k==='ghost', sk = k==='skeleton' || k==='cryptlord';
    const bob = gh ? Math.sin(m.age*2)*0.08 + 0.25 : run*Math.abs(Math.sin(ph))*0.03;
    const A2 = (cx,cy,cz,w,h,l,col,pt,col2,glow)=>add(cx*S,cy*S+bob,cz*S,w*S,h*S,l*S,col,pt,col2,glow);
    const BONEC = [228,224,208], BD = [196,190,170], ZS = [108,146,98], ZD = [84,118,78], GC = [196,226,255];
    const lg = i=>Math.sin(ph*1.6+(i?Math.PI:0))*0.18*run;
    if(!gh){
      for(const i of [0,1]){ const x = i ? 0.12 : -0.12, sw = lg(i);
        if(sk) A2(x,0,sw*0.5, 0.1,0.78,0.1, BONEC,5,BD);
        else { A2(x,0,sw*0.5, 0.22,0.78,0.24, [62,52,84],5,[50,42,70]); A2(x,0,sw*0.5+0.02, 0.24,0.08,0.28, [52,40,30]); } }
    }
    if(sk){
      A2(0,0.78,0, 0.1,0.72,0.1, BONEC);                                                   // the spine
      for(const y of [0.98,1.12,1.26,1.4]) A2(0,y,0, 0.44,0.06,0.24, BONEC,5,BD);           // ribs
      A2(0,0.76,0, 0.38,0.1,0.2, BD);                                                        // the hips
      if(k==='cryptlord'){ A2(0,0.8,0, 0.52,0.72,0.3, [78,38,108],5,[60,28,86]); A2(0,1.5,-0.02, 0.6,0.06,0.34, [96,50,130]); }   // a rotting purple robe
    } else if(gh){
      A2(0,0.1,0, 0.42,0.5,0.26, GC,5,[170,206,246],true); A2(0,0.6,0, 0.48,0.9,0.28, GC,5,[170,206,246],true);   // a body that fades out below
    } else { A2(0,0.78,0, 0.48,0.74,0.26, [74,96,128],5,[60,80,108]); A2(-0.12,0.9,0.135, 0.12,0.2,0.01, ZS); }   // torn shirt, skin showing
    // arms: zombies and ghosts reach forward; skeletons swing theirs and lash out on the attack
    for(const i of [0,1]){
      const x = i ? 0.31 : -0.31, fwd = (k==='zombie' || gh), sw = fwd ? 0 : -lg(i)*0.8, atk = A*(i ? 1 : 0.3);
      const col = sk ? BONEC : gh ? GC : ZS, w = sk ? 0.09 : 0.16;
      if(fwd) A2(x,1.36-atk*0.2,0.3+atk*0.15, w,w,0.62, col,5,sk?BD:gh?[170,206,246]:ZD,gh);
      else A2(x,0.84+atk*0.3,sw+atk*0.3, w,0.66,w, col,5,BD);
    }
    if(sk && k==='skeleton') A2(0.31,0.86+A*0.3,0.18+A*0.35, 0.05,0.06,0.62, [120,104,92]);     // a rusted blade
    if(k==='cryptlord'){ A2(0.36,0.4,0.25+A*0.4, 0.07,1.4,0.07, [60,50,46]); A2(0.36,1.8,0.25+A*0.4, 0.28,0.28,0.06, [140,40,180],0,0,true); }  // a staff with a glowing head
    // the head
    const hc = sk ? BONEC : gh ? GC : ZS;
    A2(0,1.5,0, 0.44,0.44,0.42, hc,5,sk?BD:gh?[170,206,246]:ZD,gh);
    const eye = k==='cryptlord' ? [255,60,40] : gh ? [30,40,70] : sk ? [24,20,18] : [180,30,24];
    for(const ex of [-0.1,0.1]) A2(ex,1.66,0.211, 0.1,0.08,0.01, eye,0,0,k==='cryptlord' || k==='zombie');
    if(sk) A2(0,1.55,0.211, 0.2,0.04,0.01, [40,34,30]);                                        // teeth
    if(k==='cryptlord'){ A2(0,1.94,0, 0.48,0.1,0.46, [214,170,50]); for(const [cx,cz] of [[-0.2,-0.19],[0.2,-0.19],[-0.2,0.19],[0.2,0.19],[0,0.19],[0,-0.19]]) A2(cx,2.04,cz, 0.08,0.12,0.08, [236,196,64]); }   // an old crown
  }
  if(hurtF) for(const b of out) b.col = [Math.min(255,b.col[0]+70), b.col[1]*0.6, b.col[2]*0.6];""")
# ---------- crypt life: populate, boss, cleared ----------
rep("let beastSpawnT = 8;", r"""let beastSpawnT = 8;
let cryptState = {}, cryptSeen = new Set(), cryptPop = new Set();
function cryptCleared(key){
  if(!key || (cryptState[key] && cryptState[key].cleared)) return;
  cryptState[key] = { cleared:1 };
  for(const q of quests) if(q.kind==='crypt' && q.crypt===key && q.state==='active') q.state = 'done';
  const P = cryptCache.get(key);
  skillToast((P ? P.name.toUpperCase() : 'THE CRYPT')+'<br><small>falls silent</small>', true); scheduleSave();
}
function cryptTick(){
  if(worldGen<4 || testWorld) return;
  for(const P of cryptNear(player.x, player.z, 120)){
    const d = Math.hypot(P.ex-player.x, P.ez-player.z);
    if(d<40 && !cryptSeen.has(P.key)){ cryptSeen.add(P.key); skillToast(P.name.toUpperCase()+'<br><small>discovered</small>', true); scheduleSave(); }
    if(d>100){ cryptPop.delete(P.key); continue; }
    if(cryptPop.has(P.key) || d>60 || player.y > P.h-2) continue;          // the dead stir when you go down into their halls
    if(!ratCanStand(P.boss[0],P.boss[1],P.boss[2])) continue;               // not loaded yet
    cryptPop.add(P.key);
    const cleared = cryptState[P.key] && cryptState[P.key].cleared;
    const kinds = ['skeleton','zombie','ghost','skeleton','zombie'];
    P.spawns.forEach((sp,i)=>{ if(cleared && i>1) return; const m = newBeast(kinds[(i+P.ex)%kinds.length], sp[0], sp[1], sp[2]); m.crypt = P.key; mobs.push(m); });
    if(!cleared){ const L = newBeast('cryptlord', P.boss[0], P.boss[1], P.boss[2]); L.crypt = P.key; mobs.push(L); }
  }
}""")
rep("  exploreT -= dt; if(exploreT<=0){ exploreT = 1; exploreTick(); }", "  exploreT -= dt; if(exploreT<=0){ exploreT = 1; exploreTick(); cryptTick(); }")
# crypt mobs: don't despawn while you're inside... generic far>70 rule ok. Save/load
rep("gold, armor, trained:trainedDay,", "gold, armor, crypts:cryptState, cryptSeen:[...cryptSeen], trained:trainedDay,")
rep("  trainedDay = meta.trained || {}; homesteads", "  cryptState = meta.crypts || {}; cryptSeen = new Set(meta.cryptSeen || []); cryptPop.clear(); cryptCache.clear();\n  trainedDay = meta.trained || {}; homesteads")
# ---------- crypt quests ----------
rep("  const kinds = m.job==='guard' ? ['hunt','hunt','deliver','order','build'] : ['hunt','deliver','fetch','order','order','build'];",
    "  const kinds = m.job==='guard' ? ['hunt','crypt','crypt','deliver','order','build'] : ['hunt','deliver','fetch','order','order','build','crypt'];")
rep("  if(kind==='order'){", """  if(kind==='crypt'){
    const C = cryptNear(vc[0], vc[1], 420).find(P=>!(cryptState[P.key] && cryptState[P.key].cleared));
    if(C){ const d = Math.hypot(C.ex-vc[0], C.ez-vc[1]), reward = 160 + Math.round(d/4), days = 5;
      return { kind:'crypt', crypt:C.key, cname:C.name, at:[C.ex,C.ez], days, reward, rep:15,
               text:`The dead are walking out of the ${C.name}, about ${Math.round(d/10)*10} paces ${dirWord(vc[0],vc[1],C.ex,C.ez)} of here. Something commands them: a Crypt Lord, the old stories say. Go down and destroy it within ${days} days. ${reward} gold, and every family here in your debt.` }; }
    kind = 'hunt';
  }
  if(kind==='order'){""")
rep("    else if(q && q.kind==='build' && q.state==='done'){", "    else if(q && q.kind==='crypt' && q.state==='done'){ finishQuest(q, true); talkLine = `The Crypt Lord is gone? Then the dead will rest. ${q.reward} gold, with our thanks.`; }\n    else if(q && q.kind==='build' && q.state==='done'){")
rep("back = quests.find(q=>q.giver===m.home && (q.kind==='hunt' || q.kind==='build' ? q.state==='done' :", "back = quests.find(q=>q.giver===m.home && (q.kind==='hunt' || q.kind==='build' || q.kind==='crypt' ? q.state==='done' :")
rep("${back.kind==='build' ? 'REPORT THE WORK' : back.kind==='hunt' ? 'REPORT THE KILL' :", "${back.kind==='build' ? 'REPORT THE WORK' : back.kind==='hunt' || back.kind==='crypt' ? 'REPORT THE KILL' :")
rep("    else if(q.kind==='build'){ const J", "    else if(q.kind==='crypt') goal = q.state==='done' ? `The Crypt Lord is destroyed. Return to ${q.giverName} (${gv}).` : `Destroy the Crypt Lord in the ${q.cname}, ${far(q.at[0],q.at[1])}.`;\n    else if(q.kind==='build'){ const J")
rep("<b>${q.kind==='hunt'?'Hunt':", "<b>${q.kind==='crypt'?'Crypt':q.kind==='hunt'?'Hunt':")
rep("mine.kind==='build' ? 'How is the building coming along?' :", "mine.kind==='build' ? 'How is the building coming along?' : mine.kind==='crypt' ? 'Is the crypt quiet yet?' :")
# map markers
rep("  for(const q of quests){ const t = q.kind==='hunt' && q.state==='active' ? q.at : q.kind==='deliver' ? q.tvc : null;",
    "  for(const k of cryptSeen){ const P = cryptCache.get(k); if(P) mark(P.ex, P.ez, cryptState[k] && cryptState[k].cleared ? '#8a8a9a' : '#b07ae0', P.name); }\n  for(const q of quests){ const t = (q.kind==='hunt' || q.kind==='crypt') && q.state==='active' ? q.at : q.kind==='deliver' ? q.tvc : null;")
rep("if(t) mark(t[0], t[1], '#e05040', q.kind==='hunt' ? BEAST_NAME[q.beast] : q.toName); }", "if(t) mark(t[0], t[1], '#e05040', q.kind==='hunt' ? BEAST_NAME[q.beast] : q.kind==='crypt' ? q.cname : q.toName); }")
rep("const nm = { bear:'a grizzly bear', tiger:'a sabertooth', spider:'giant spiders', scorpion:'a giant scorpion' };", "const nm = { bear:'a grizzly bear', tiger:'a sabertooth', spider:'giant spiders', scorpion:'a giant scorpion', skeleton:'walking skeletons', zombie:'the walking dead', ghost:'a ghost', cryptlord:'a Crypt Lord' };")
rep("const BEAST_NAME = {", "const BEAST_NAME_X = 0;\nconst BEAST_NAME = { skeleton:'skeleton', zombie:'zombie', ghost:'ghost', cryptlord:'Crypt Lord', ")
# den hunts never pick undead (they're night creatures already excluded by !night); test hall room
rep("[1,-1,{name:'BEASTS: SPIDER + SCORPION', h:8, floor:SAND, wall:SANDSTONE, mobs:['spider+scorpion',2]}]",
    "[1,-1,{name:'BEASTS: SPIDER + SCORPION', h:8, floor:SAND, wall:SANDSTONE, mobs:['spider+scorpion+skeleton+zombie+ghost+cryptlord',6]}]")
open(p,'w').write(s); print('ok')
