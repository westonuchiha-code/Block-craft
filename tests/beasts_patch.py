p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:70]); s=s.replace(a,b)

# ---------- items ----------
rep("NAMES[COOK_TABLE] = 'cooking table'; COLORS[COOK_TABLE] = [104,100,98];", """NAMES[COOK_TABLE] = 'cooking table'; COLORS[COOK_TABLE] = [104,100,98];
// ---- what the wild beasts leave behind (Daggerfall's bestiary: grizzly bears, sabertooth tigers, giant spiders, giant scorpions) ----
const LEATHER = 1081, RAW_MEAT = 1082, STEAK = 1083, SILK = 1084, CHITIN = 1085, MEAT_STEW = 1086;
[[LEATHER,'leather',[150,98,56]],[RAW_MEAT,'raw meat',[196,64,58]],[STEAK,'steak',[140,82,44]],[SILK,'spider silk',[232,232,236]],[CHITIN,'scorpion chitin',[170,110,50]],[MEAT_STEW,'meat stew',[132,74,42]]]
  .forEach(([id,n,c])=>{ NAMES[id]=n; COLORS[id]=c; FLAT_ITEMS.add(id); });
FOOD_VAL[RAW_MEAT] = 2; ING_VAL[RAW_MEAT] = 6;           // raw it barely helps; a cooked steak (~250 kcal) is a full 6
FOOD_VAL[STEAK] = 6; FOOD_VAL[MEAT_STEW] = 6+4+2;           // stew = meat + potato + carrot
COOK_RECIPES.push({ name:'steak', out:[STEAK,1], ing:{[RAW_MEAT]:1}, list:[RAW_MEAT], back:null });
{ const L = [RAW_MEAT,POTATO,CARROT,WATER_BUCKET]; const ing = {}; for(const q of L) ing[q] = 1;
  COOK_RECIPES.push({ name:'meat stew', out:[MEAT_STEW,1], ing, list:L.slice().sort((a,b)=>a-b), back:[WOOD_BUCKET,1] }); }""")
rep("  { name:'Candles (placeh", "  { name:'White wool (4 spider silk)', out:[WOOL0,1], ing:{[SILK]:4} },\n  { name:'Candles (placeh")
rep("SHORT[STICK]='stick';", "SHORT[LEATHER]='leather'; SHORT[RAW_MEAT]='r.meat'; SHORT[STEAK]='steak'; SHORT[SILK]='silk'; SHORT[CHITIN]='chitin'; SHORT[MEAT_STEW]='stew'; SHORT[STICK]='stick';")
rep("  add('POTIONS + MAGIC', [FIRE_POTION, BOLT_POTION, EMBER]);", "  add('POTIONS + MAGIC', [FIRE_POTION, BOLT_POTION, EMBER]);\n  add('BEAST DROPS + MEAT', [LEATHER, RAW_MEAT, STEAK, MEAT_STEW, SILK, CHITIN]);")
# icons
rep("    case PISTOL: paintIcon(g,(P,E)=>{", """    case LEATHER: paintIcon(g,(P,E)=>{ E(8,8.5,6.6,5.6,null,(x,y,dx,dy)=>{ const r=dx*dx+dy*dy; return r>0.7 ? [118,74,40] : ((x*7+y*3)%11===0 ? [170,116,70] : (y<6 ? [166,110,64] : [150,98,56])); });
              for(const [x,y] of [[2,4],[13,4],[2,13],[13,13]]) P(x,y,[118,74,40]); for(let x=4;x<=11;x+=2){ P(x,4,[226,206,170]); P(x,13,[226,206,170]); } }); return true;
    case RAW_MEAT: case STEAK: paintIcon(g,(P,E)=>{ const raw = id===RAW_MEAT, M = raw?[196,64,58]:[140,82,44], D = raw?[150,40,40]:[96,54,28], F = raw?[244,226,214]:[210,170,110];
              E(8.5,8.5,6,4.6,null,(x,y,dx,dy)=>{ const r=dx*dx+dy*dy; if(r>0.72) return F; if(raw && ((x+y*2)%7===0)) return F; if(!raw && (x-y+16)%4===0) return D; return y<7 ? scaleC(M,1.12) : M; });
              for(const [x,y] of [[2,12],[3,12],[3,13],[2,13]]) P(x,y,[240,236,224]); }); return true;
    case SILK: paintIcon(g,(P,E)=>{ for(let k=0;k<3;k++) E(8,8,6-k*1.6,4.4-k*1.1,null,(x,y,dx,dy)=>{ const r=dx*dx+dy*dy; return r>0.55 ? ((x+y+k)%3? [238,238,242]:[196,196,206]) : null; });
              for(let x=5;x<=11;x++) P(x,8,[214,214,222]); P(13,11,[238,238,242]); P(14,12,[238,238,242]); }); return true;
    case CHITIN: paintIcon(g,(P,E)=>{ E(8,8.5,6.4,5.4,null,(x,y,dx,dy)=>{ return y%3===0 ? [110,66,30] : (dx<-0.3&&dy<-0.2 ? [210,150,76] : [170,110,50]); }); }); return true;
    case MEAT_STEW: paintIcon(g,(P,E)=>{ E(8,10.5,6.4,4.2,[150,90,60]); for(let x=2;x<14;x++) P(x,8,[176,110,74]); E(8,9.4,5.4,2.4,[132,74,42]);
              for(const [x,y,c] of [[5,9,[176,92,62]],[8,8,[230,210,150]],[10,9,[236,150,50]],[7,10,[176,92,62]],[11,8,[176,92,62]]]) P(x,y,c); P(6,4,[236,236,236]); P(7,3,[236,236,236]); P(10,5,[236,236,236]); }); return true;
    case PISTOL: paintIcon(g,(P,E)=>{""")

# ---------- the beasts ----------
beast = r'''// ---------- wild beasts, from Daggerfall's bestiary (built from blocks like everything else) ----------
// Grizzly bear: the woods; leaves you alone unless you come close or hit it. Sabertooth tiger: the Frostlands and the pine highlands; hunts you on sight.
// Giant spider: comes out of the woods at night. Giant scorpion: the Sunscorch desert. They all fight to the death (Daggerfall's beasts don't flee).
const BEAST = {
  bear:     { hp:30, bite:4, cd:1.3, walk:0.032, run:0.09, aggro:5,  memory:25, reach:1.7, tall:1.3, br:1.9, rect:2.0, max:2, group:[1,1], weight:1.0,
              where:(b,y)=>b<=2, drops:[[LEATHER,2,3],[RAW_MEAT,2,4]] },
  tiger:    { hp:22, bite:5, cd:1.0, walk:0.04,  run:0.11, aggro:14, memory:20, reach:1.55, tall:1.15, br:1.7, rect:1.8, max:2, group:[1,2], weight:1.0,
              where:(b,y)=>b===3 || (b===2 && y>=CAT_MOUNTAIN_Y), drops:[[LEATHER,1,2],[RAW_MEAT,1,3]] },
  spider:   { hp:14, bite:3, cd:0.9, walk:0.045, run:0.1,  aggro:12, memory:18, reach:1.6, tall:1.0, br:1.6, rect:1.8, max:4, group:[1,3], weight:1.4, night:true,
              where:(b,y)=>b<=2, drops:[[SILK,1,3]] },
  scorpion: { hp:20, bite:4, cd:1.1, walk:0.038, run:0.085, aggro:10, memory:18, reach:1.8, tall:1.2, br:1.8, rect:1.9, max:3, group:[1,2], weight:1.0,
              where:(b,y)=>b===4, drops:[[CHITIN,1,2]] }
};
const BEAST_TOTAL = 4;
let beastSpawnT = 8;
function nearVillage(x,z){
  const v = villageAt(Math.floor(x/VREG), Math.floor(z/VREG)); if(!v || !v.rects) return false;
  for(const R of v.rects) if(x>=R.x0-20 && x<=R.x1+20 && z>=R.z0-20 && z<=R.z1+20) return true;
  return false;
}
// out on the land: in the open, or under nothing but trees
function beastAllowed(x,y,z){
  if(isTestZ(z)) return true;
  if(y<CAT_MIN_Y) return false;
  const t = ratTop(x,z); if(t<=y+2) return true;
  if(t>y+16) return false;
  for(let yy=y+1; yy<t; yy++){ const b = ratGet(x,yy,z); if(b!==AIR && !IS_LEAF[b] && !IS_LOG[b]) return false; }
  return true;
}
function newBeast(kind,x,y,z){
  return { id:mobId++, kind, x:x+0.5, y, z:z+0.5, yaw:Math.random()*6.28, hp:BEAST[kind].hp, variant:0,
           state:'idle', idleT:Math.random()*3, path:null, pi:0, replanT:0, angry:0, atkCd:0, atkA:0, hurtT:0, iframe:0, dead:false, deadT:0,
           phase:Math.random()*6, age:Math.random()*10, moving:false, kx:0, kz:0, stuckT:0, dayT:0 };
}
function beastHit(m, dmg){
  if(m.dead || m.iframe>0) return;
  const K = BEAST[m.kind];
  m.hp -= dmg; m.hurtT = 0.3; m.iframe = 0.3; m.angry = K.memory; m.replanT = 0;
  const dx=m.x-player.x, dz=m.z-player.z, d=Math.hypot(dx,dz)||1, kb = m.kind==='bear' ? 0.08 : 0.18;
  m.kx = dx/d*kb; m.kz = dz/d*kb;
  if(m.hp<=0){
    m.dead = true; m.deadT = 0; m.path = null;
    const x=Math.floor(m.x), y=Math.floor(m.y)+1, z=Math.floor(m.z);
    for(const [id,lo,hi] of K.drops) for(let n=roll(lo,hi); n>0; n--) spawnDrop(x,y,z,id);
  }
}
function updateBeast(m, dt){
  const K = BEAST[m.kind], cx=Math.floor(m.x), cy=Math.round(m.y), cz=Math.floor(m.z);
  m.atkA = Math.max(0, m.atkA - dt*3.5);
  const dxp = player.x-m.x, dzp = player.z-m.z, dist = Math.hypot(dxp,dzp), dyp = player.y-m.y;
  if(K.night && !ratNight && !isTestZ(m.z)){ m.dayT += dt; if(m.dayT>15 && dist>18) return 'gone'; }        // spiders slink off at sunrise
  if(dead) m.angry = 0;
  else if(m.angry<=0 && dist<K.aggro && Math.abs(dyp)<4) m.angry = K.memory;
  if(m.angry>0){
    m.angry -= dist > K.aggro*2.5+8 ? dt*3 : dt*0.2;                                   // it forgets you only once you're well away
    if(dist<K.reach && Math.abs(dyp)<1.6){
      m.moving = false; m.yaw = Math.atan2(dxp,-dzp);
      if(m.atkCd<=0){ hurt(K.bite); m.atkCd = K.cd; m.atkA = 1; }
      return;
    }
    m.replanT -= dt;
    if(m.replanT<=0 || !m.path || m.pi>=m.path.length){
      m.replanT = 0.4+Math.random()*0.2;
      const p = ratPath(cx,cy,cz,(x,y,z)=>Math.hypot(x+0.5-player.x,z+0.5-player.z)<1.2 && Math.abs(y-player.y)<2, beastAllowed, 500);
      if(p) ratSetPath(m,p); else m.path = null;
    }
    if(m.path && ratWalk(m, K.run)) return;
    // no route (you're on a ledge, say): edge straight toward you where the ground allows
    const st = Math.min(dist, K.run*frameScale), nx = m.x+dxp/dist*st, nz = m.z+dzp/dist*st;
    if(ratCanStand(Math.floor(nx),cy,Math.floor(nz))){ m.x = nx; m.z = nz; m.moving = true; m.phase += st*5; } else m.moving = false;
    m.yaw = Math.atan2(dxp,-dzp);
    return;
  }
  if(m.state==='idle'){
    m.moving = false; m.idleT -= dt;
    if(Math.random()<dt*0.3) m.yaw += (Math.random()-0.5)*1.2;
    if(m.idleT<=0){
      const a=Math.random()*6.283, d=3+Math.random()*9, tx=m.x+Math.cos(a)*d, tz=m.z+Math.sin(a)*d;
      const p = ratPath(cx,cy,cz,(x,y,z)=>Math.hypot(x+0.5-tx,z+0.5-tz)<1.6 && Math.abs(y-cy)<=3, beastAllowed, 300);
      if(p){ ratSetPath(m,p); m.state='wander'; } else m.idleT = 1+Math.random()*2;
    }
  } else if(!ratWalk(m, K.walk)){ m.state='idle'; m.idleT = 2+Math.random()*5; }
}
function trySpawnBeasts(){
  const cnt = {}; let total = 0;
  for(const m of mobs) if(BEAST[m.kind]){ cnt[m.kind] = (cnt[m.kind]||0)+1; total++; }
  if(total>=BEAST_TOTAL || Math.random()>0.6) return;
  for(let attempt=0; attempt<30; attempt++){
    const a=Math.random()*6.283, d=24+Math.random()*28, x=Math.floor(player.x+Math.cos(a)*d), z=Math.floor(player.z+Math.sin(a)*d);
    const y = colInfo(x,z).h+1;
    if(!ratCanStand(x,y,z) || !beastAllowed(x,y,z)) continue;
    const b = biomeAt(x,z);
    const opts = Object.keys(BEAST).filter(k=>{ const K=BEAST[k]; return K.where(b,y) && (!K.night || ratNight) && (cnt[k]||0)<K.max; });
    if(!opts.length) continue;
    if(nearVillage(x,z)) continue;                                                  // they keep away from settlements
    let w = 0; for(const k of opts) w += BEAST[k].weight;
    let r = Math.random()*w, kind = opts[0]; for(const k of opts){ r -= BEAST[k].weight; if(r<=0){ kind = k; break; } }
    const K = BEAST[kind];
    for(let n=roll(K.group[0],K.group[1]); n>0 && (cnt[kind]||0)<K.max; n--){
      const sx=x+Math.floor(Math.random()*5)-2, sz=z+Math.floor(Math.random()*5)-2, sy=colInfo(sx,sz).h+1;
      if(ratCanStand(sx,sy,sz) && beastAllowed(sx,sy,sz) && mobs.length<80){ mobs.push(newBeast(kind,sx,sy,sz)); cnt[kind] = (cnt[kind]||0)+1; }
    }
    return;
  }
}
// ---- the models: boxes in mob space (x right, y up, z forward), in blocks ----
function beastBoxes(m, out){
  out.length = 0;
  const run = m.moving ? 1 : 0, ph = m.phase, A = m.atkA, hurtF = m.hurtT>0;
  const add = (cx,cy,cz,w,h,l,col,pt,col2,glow)=>out.push({x0:cx-w/2,x1:cx+w/2,y0:cy,y1:cy+h,z0:cz-l/2,z1:cz+l/2,col,col2,pt,glow:!!glow});
  const sw = i=>Math.sin(ph*1.5+(i===1||i===2?Math.PI:0))*0.09*run;
  if(m.kind==='bear'){
    const B=[112,78,50], D=[88,60,38], MZ=[172,136,96], bob = run*Math.abs(Math.sin(ph))*0.03;
    add(0,0.42+bob,-0.1, 0.88,0.7,1.4, B,1,D);                                         // the bulk
    add(0,1.12+bob,0.3, 0.72,0.14,0.52, B,1,D);                                        // shoulder hump
    const hy = 0.66+bob+A*0.14, hz = 0.8+A*0.22;                                       // the head lunges when it swipes
    add(0,hy,hz, 0.56,0.5,0.46, B,1,D);
    add(0,hy+0.02,hz+0.3, 0.3,0.24,0.18, MZ,1,[152,118,82]);
    add(0,hy+0.19,hz+0.395, 0.12,0.08,0.02, [28,22,20]);
    add(0,hy-0.02-A*0.08,hz+0.27, 0.26,0.06,0.16, [120,40,40]);                         // jaw drops open on the bite
    for(const s of [-1,1]){
      add(s*0.15,hy+0.32,hz+0.235, 0.07,0.07,0.02, [24,20,18]);
      add(s*0.21,hy+0.5,hz-0.08, 0.14,0.12,0.08, D);
    }
    for(let i=0;i<4;i++){
      const side = i%2 ? 0.28 : -0.28, zc = i<2 ? 0.42 : -0.6, lift = (i<2 && A>0.3) ? A*0.25 : 0;
      add(side,lift,zc+sw(i), 0.28,0.46,0.3, D,1,B);
      add(side,lift,zc+sw(i)+0.17, 0.26,0.05,0.04, [226,214,188]);                      // claws
    }
    add(0,0.96+bob,-0.83, 0.16,0.14,0.08, D);
  } else if(m.kind==='tiger'){
    const T=[214,148,68], T2=[200,134,58], S=[62,40,26], W=[238,224,192], bob = run*Math.abs(Math.sin(ph))*0.03;
    add(0,0.5+bob,-0.1, 0.56,0.5,1.25, T,1,T2);
    for(const z of [-0.55,-0.27,0.01,0.29]) add(0,0.62+bob,z, 0.58,0.39,0.07, S);      // stripes over the back and sides
    add(0,0.48+bob,-0.1, 0.5,0.04,1.0, W);
    const hy = 0.72+bob+A*0.06, hz = 0.68+A*0.24;
    add(0,hy,hz, 0.44,0.38,0.4, T,1,T2);
    add(0,hy,hz+0.26, 0.26,0.18,0.14, W);
    add(0,hy+0.13,hz+0.335, 0.08,0.05,0.02, [70,44,40]);
    add(0,hy+0.3,hz+0.205, 0.06,0.08,0.01, S);
    for(const s of [-1,1]){
      add(s*0.12,hy+0.24,hz+0.205, 0.07,0.06,0.02, [226,196,58]);
      add(s*0.15,hy+0.38,hz, 0.1,0.1,0.06, T);
      add(s*0.07,hy-0.22-A*0.04,hz+0.29, 0.05,0.26,0.05, [248,244,230]);               // the sabre fangs
    }
    for(let i=0;i<4;i++){
      const side = i%2 ? 0.18 : -0.18, zc = i<2 ? 0.38 : -0.56;
      add(side,0,zc+sw(i), 0.17,0.52,0.2, T,1,T2);
      add(side,0,zc+sw(i)+0.01, 0.19,0.07,0.22, W);
    }
    [[-0.78,0.88],[-0.9,0.78],[-1.0,0.66],[-1.06,0.54]].forEach(([z,y],i)=>add(Math.sin(m.age*2.2+i*0.7)*0.03*i,y+bob,z, 0.09,0.09,0.14, i===3?S:T));
  } else if(m.kind==='spider'){
    const B=[60,48,44], D=[40,32,30], R=[164,44,32], L=[76,60,52], bob = run*Math.abs(Math.sin(ph*2))*0.02;
    add(0,0.42+bob,-0.42, 0.8,0.6,0.82, B,1,D);                                        // abdomen
    add(0,1.02+bob,-0.48, 0.14,0.02,0.44, R); add(-0.2,1.02+bob,-0.3, 0.12,0.02,0.12, R); add(0.2,1.02+bob,-0.3, 0.12,0.02,0.12, R);
    add(0,0.36+bob,0.18, 0.52,0.36,0.5, B,1,D);                                        // body
    add(0,0.38+bob+A*0.05,0.5+A*0.12, 0.36,0.26,0.2, D);                                 // head
    for(const s of [-1,1]){
      add(s*0.08,0.54+bob+A*0.05,0.6+A*0.12, 0.07,0.06,0.02, [236,46,34],0,0,true);      // eyes that glow red
      add(s*0.15,0.59+bob+A*0.05,0.6+A*0.12, 0.04,0.04,0.02, [236,46,34],0,0,true);
      add(s*(0.07+A*0.03),0.24+bob,0.62+A*0.14, 0.05,0.16,0.05, [30,24,22]);             // fangs
      [0.34,0.18,0.02,-0.14].forEach((z,i)=>{
        const spread = [0.32,0.1,-0.12,-0.34][i], ph2 = ph*2+i*1.6+(s>0?Math.PI:0), lift = run*Math.max(0,Math.sin(ph2))*0.12, swing = run*Math.cos(ph2)*0.08;
        const zo = z+spread+swing;
        add(s*0.41,0.56+bob,z, 0.34,0.1,0.08, L);                                       // up to the knee
        add(s*0.7,0.74+bob,(z+zo)/2, 0.4,0.1,0.08, L);
        add(s*0.92,lift,zo, 0.08,0.84+bob-lift,0.08, D);                                // and down to the ground
      });
    }
  } else if(m.kind==='scorpion'){
    const C=[160,104,50], D=[112,68,32], Lt=[196,140,72], bob = run*Math.abs(Math.sin(ph*2))*0.015;
    add(0,0.22+bob,0.12, 0.62,0.3,0.52, C,1,D);
    add(0,0.22+bob,-0.32, 0.52,0.28,0.4, C,1,D);
    add(0,0.2+bob,0.48, 0.42,0.26,0.24, D,1,C);
    for(const s of [-1,1]){
      add(s*0.09,0.47+bob,0.6, 0.05,0.04,0.02, [20,14,10]);
      add(s*0.3,0.26+bob,0.68+A*0.1, 0.12,0.12,0.38, C,1,D);                             // claw arms
      add(s*0.36,0.22+bob,0.94+A*0.14, 0.22,0.2,0.22, Lt,1,C);
      add(s*(0.29-A*0.04),0.24+bob,1.12+A*0.14, 0.06,0.08,0.18, D);                     // pincers snap shut on the attack
      add(s*(0.43+A*0.04),0.24+bob,1.12+A*0.14, 0.06,0.08,0.18, D);
      [0.2,-0.05,-0.3].forEach((z,i)=>{ const ph2 = ph*2+i*2+(s>0?Math.PI:0), lf = run*Math.max(0,Math.sin(ph2))*0.06;
        add(s*0.42,0.2+bob,z, 0.28,0.07,0.07, D); add(s*0.58,lf,z+run*Math.cos(ph2)*0.06, 0.06,0.24-lf,0.06, D); });
    }
    const T = [[-0.62,0.3],[-0.82,0.48],[-0.9,0.72],[-0.82,0.96],[-0.62,1.12]];        // the tail arcs up and over, and strikes forward
    T.forEach(([z,y],i)=>{ const k = i/4; add(0,y+bob-A*0.18*k,z+A*0.5*k*k, 0.2-i*0.02,0.2,0.2, i%2?D:C,1,D); });
    add(0,1.04+bob-A*0.25,-0.42+A*0.6, 0.12,0.12,0.12, [44,28,20]);
    add(0,0.94+bob-A*0.25,-0.34+A*0.62, 0.05,0.12,0.05, [24,16,12]);                   // the stinger
  }
  if(hurtF) for(const b of out) b.col = [Math.min(255,b.col[0]+70), b.col[1]*0.6, b.col[2]*0.6];
  return out;
}
'''
rep("function updateMobs(){\n", beast+"function updateMobs(){\n")
# hooks
rep("  wbSpawnT -= dt; if(wbSpawnT<=0){ wbSpawnT = 11; if(!underNow) trySpawnWb(); }",
    "  wbSpawnT -= dt; if(wbSpawnT<=0){ wbSpawnT = 11; if(!underNow) trySpawnWb(); }\n  beastSpawnT -= dt; if(beastSpawnT<=0){ beastSpawnT = 13; if(!underNow) trySpawnBeasts(); }")
rep("    if(m.kind==='wb'){ updateWb(m,dt); continue; }",
    "    if(m.kind==='wb'){ updateWb(m,dt); continue; }\n    if(BEAST[m.kind]){ if(updateBeast(m,dt)==='gone') mobs.splice(i,1); continue; }")
rep("else if(m.kind==='wb') wbHit(m,dmg); else if(m.kind==='npc')", "else if(m.kind==='wb') wbHit(m,dmg); else if(BEAST[m.kind]) beastHit(m,dmg); else if(m.kind==='npc')")
rep("  const BR = m.kind==='cat' ? 0.95 : m.kind==='wb' ? 2.3 : 0.8;", "  const BR = m.kind==='cat' ? 0.95 : m.kind==='wb' ? 2.3 : BEAST[m.kind] ? BEAST[m.kind].br : 0.8;")
rep("m.kind==='wb' ? wbBoxes(m,_rb) : m.kind==='sap'", "m.kind==='wb' ? wbBoxes(m,_rb) : BEAST[m.kind] ? beastBoxes(m,_rb) : m.kind==='sap'")
rep("m.kind==='wb'?2.5:0.85)*(RH/2)", "m.kind==='wb'?2.5:BEAST[m.kind]?BEAST[m.kind].rect:0.85)*(RH/2)")
rep("m.kind==='wb' ? 1.5 : 0.35; }", "m.kind==='wb' ? 1.5 : BEAST[m.kind] ? BEAST[m.kind].tall : 0.35; }")
# test hall: two beast rooms at the near end of the hall
rep("fill(-1,FY,-3,125,FY+9,3,STONE_BRICK); fill(0,FY+1,-2,124,FY+7,2,AIR); fill(0,FY,-2,124,FY,2,FLAGSTONE);",
    "fill(-25,FY,-3,125,FY+9,3,STONE_BRICK); fill(-24,FY+1,-2,124,FY+7,2,AIR); fill(-24,FY,-2,124,FY,2,FLAGSTONE);")
rep("    [1,4,{name:'UNDERWORLD GATE', h:9, floor:DARKWOOD, wall:STONE_BRICK}]\n",
    "    [1,4,{name:'UNDERWORLD GATE', h:9, floor:DARKWOOD, wall:STONE_BRICK}],\n    [-1,-1,{name:'BEASTS: BEAR + TIGER', h:8, floor:GRASS, wall:STONE_BRICK, mobs:['bear+tiger',2]}], [1,-1,{name:'BEASTS: SPIDER + SCORPION', h:8, floor:SAND, wall:SANDSTONE, mobs:['spider+scorpion',2]}]\n")
rep("for(let x=2;x<=122;x+=6) for(const r of [-2,0,2]) put(x,FY+8,r,GLOW);", "for(let x=-22;x<=122;x+=6) for(const r of [-2,0,2]) put(x,FY+8,r,GLOW);")
rep("      for(let i=0;i<n;i++){ const x = Math.floor(mx)+(i%3)-1, z = Math.floor(mz)+Math.floor(i/3)*(room.side<0?-1:1)*2;\n        mobs.push(kind==='wb'",
    "      const kinds = kind.split('+');\n      for(let i=0;i<n;i++){ const x = Math.floor(mx)+(i%3)*4-4, z = Math.floor(mz)+Math.floor(i/3)*(room.side<0?-1:1)*2, kind = kinds[i%kinds.length];\n        if(BEAST[kind]){ mobs.push(newBeast(kind,x,my,z)); continue; }\n        mobs.push(kind==='wb'")
open(p,'w').write(s); print('ok')
