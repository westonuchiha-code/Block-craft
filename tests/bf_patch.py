p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# items
rep("const SACK = 1089;", "const RAW_FISH = 1133, COOKED_FISH = 1134;\nconst SACK = 1089;")
rep("FOOD_VAL[RAW_MEAT] = 2;", """[[RAW_FISH,'raw slaughterfish',[150,170,160]],[COOKED_FISH,'grilled fish',[196,150,96]]].forEach(([id,n,c])=>{ NAMES[id]=n; COLORS[id]=c; FLAT_ITEMS.add(id); });
FOOD_VAL[RAW_FISH] = 2; ING_VAL[RAW_FISH] = 5; FOOD_VAL[COOKED_FISH] = 5;
FOOD_VAL[RAW_MEAT] = 2;""")
rep("COOK_RECIPES.push({ name:'steak', out:[STEAK,1], ing:{[RAW_MEAT]:1}, list:[RAW_MEAT], back:null });", "COOK_RECIPES.push({ name:'steak', out:[STEAK,1], ing:{[RAW_MEAT]:1}, list:[RAW_MEAT], back:null });\nCOOK_RECIPES.push({ name:'grilled fish', out:[COOKED_FISH,1], ing:{[RAW_FISH]:1}, list:[RAW_FISH], back:null });")
rep("      const cooked = DISHES.some(d=>d.id===id) || id===STEAK || id===MEAT_STEW;", "      const cooked = DISHES.some(d=>d.id===id) || id===STEAK || id===MEAT_STEW || id===COOKED_FISH;")
rep("SHORT[GOLD]='gold';", "SHORT[RAW_FISH]='r.fish'; SHORT[COOKED_FISH]='fish'; SHORT[GOLD]='gold';")
rep("  P(LEATHER, 12);", "  P(RAW_FISH, 4); P(COOKED_FISH, 9);\n  P(LEATHER, 12);")
rep("  fisher:     { title:'Fisher\\'s stall', sell:[WOOD_BUCKET, WATER_BUCKET, RAW_MEAT, STEAK], buy:[RAW_MEAT, LEATHER, SILK] },",
    "  fisher:     { title:'Fisher\\'s stall', sell:[WOOD_BUCKET, WATER_BUCKET, RAW_FISH, COOKED_FISH, RAW_MEAT], buy:[RAW_FISH, COOKED_FISH, RAW_MEAT, LEATHER, SILK] },")
rep("    case RAW_MEAT: case STEAK: paintIcon(g,(P,E)=>{", """    case RAW_FISH: case COOKED_FISH: paintIcon(g,(P,E)=>{ const raw = id===RAW_FISH, B = raw?[124,150,134]:[186,138,84], D = raw?[80,104,90]:[130,90,52], L = raw?[200,120,110]:[224,184,120];
              E(7.5,8.5,5.8,3,null,(x,y,dx,dy)=>dy>0.35 ? L : (x+y)%3===0 ? D : B); for(const [x,y] of [[13,6],[14,5],[13,11],[14,12],[13,7],[13,10],[12,8],[12,9]]) P(x,y,D); P(4,7,[20,20,20]); if(!raw) for(let x=4;x<=10;x+=3) P(x,9,[96,60,30]); }); return true;
    case RAW_MEAT: case STEAK: paintIcon(g,(P,E)=>{""")
# creatures
rep("  scorpion: { hp:20, bite:3, cd:1.3,", """  bat:      { hp:6, bite:2, cd:0.8, walk:0.06, run:0.12, aggro:12, memory:15, reach:1.2, tall:0.5, br:1.3, rect:1.4, max:6, group:[2,4], weight:1.1, night:true, fly:true,
              where:(b,y)=>true, drops:[[LEATHER,0,1]] },
  fish:     { hp:10, bite:3, cd:0.9, walk:0.04, run:0.1, aggro:12, memory:15, reach:1.3, tall:0.5, br:1.5, rect:1.6, max:5, group:[1,3], weight:0, swim:true,
              where:()=>false, drops:[[RAW_FISH,1,2]] },
  scorpion: { hp:20, bite:3, cd:1.3,""")
rep("function updateBeast(m, dt){", r"""// ---- giant bats and slaughterfish: they move freely in air or water instead of walking ----
function updateFlyer(m, dt){
  const K = BEAST[m.kind];
  m.atkA = Math.max(0, m.atkA - dt*3.5); m.flap = (m.flap||0) + dt*(m.kind==='bat' ? 18 : 6);
  const okCell = (x,y,z)=>{ const b = getB(Math.floor(x),Math.floor(y),Math.floor(z)); return K.swim ? !!IS_WATER[b] : PASS[b] && !IS_WATER[b] && !IS_LAVA[b]; };
  if(K.swim && !okCell(m.x, m.y+0.25, m.z)){ m.outT = (m.outT||0) + dt; m.vy = (m.vy||0) - 0.5*dt; if(!okCell(m.x, m.y-0.1+ m.vy, m.z) && PASS[getB(Math.floor(m.x),Math.floor(m.y+m.vy),Math.floor(m.z))]) m.y += m.vy; if(m.outT>6){ m.hp = 0; m.dead = true; m.deadT = 0; } return; }     // a fish on dry land flops and dies
  m.outT = 0;
  if(K.night && !ratNight && !isTestZ(m.z) && !m.crypt){ m.dayT += dt; if(m.dayT>15 && Math.hypot(player.x-m.x, player.z-m.z)>18) return 'gone'; }
  const px = player.x, py = player.y + 1.2, pz = player.z, dist = Math.hypot(px-m.x, py-m.y, pz-m.z);
  if(dead) m.angry = 0;
  else if(m.angry<=0 && dist<K.aggro*stealthMul() && (!K.swim || bodyInWater)) m.angry = K.memory;
  if(K.swim && !bodyInWater && m.angry>0) m.angry -= dt*4;                        // fish give up once you leave the water
  let tx, ty, tz, sp;
  if(m.angry>0){
    m.angry -= dist > K.aggro*2 ? dt*3 : dt*0.3;
    tx = px; ty = py; tz = pz; sp = K.run;
    if(dist<K.reach && m.atkCd<=0){ hurt(lvlDmg(K.bite, m.lvl)); m.atkCd = K.cd; m.atkA = 1; }
  } else {
    if(!m.goal || Math.hypot(m.goal[0]-m.x, m.goal[1]-m.y, m.goal[2]-m.z) < 0.8 || Math.random()<dt*0.15){
      const hx = m.hx ?? m.x, hz = m.hz ?? m.z; m.hx = hx; m.hz = hz;
      const gy = K.swim ? m.y + (Math.random()-0.5)*2 : colInfo(Math.floor(m.x),Math.floor(m.z)).h + 2 + Math.random()*5;
      m.goal = [hx+(Math.random()-0.5)*14, Math.min(H-2, gy), hz+(Math.random()-0.5)*14];
    }
    [tx,ty,tz] = m.goal; sp = K.walk;
  }
  const dx = tx-m.x, dy = ty-m.y, dz = tz-m.z, d = Math.hypot(dx,dy,dz)||1;
  const wob = m.kind==='bat' ? Math.sin(m.age*7)*0.4 : 0;
  m.vx = (m.vx||0)*0.85 + (dx/d)*sp*0.15; m.vy = (m.vy||0)*0.85 + (dy/d + wob)*sp*0.15; m.vz = (m.vz||0)*0.85 + (dz/d)*sp*0.15;
  const nx = m.x + m.vx*frameScale, ny = m.y + m.vy*frameScale, nz = m.z + m.vz*frameScale;
  if(okCell(nx, ny+0.25, nz)){ m.x = nx; m.y = ny; m.z = nz; }
  else if(okCell(nx, m.y+0.25, nz)){ m.x = nx; m.z = nz; m.vy = 0; }
  else if(okCell(m.x, ny+0.25, m.z)){ m.y = ny; m.vx = m.vz = 0; m.goal = null; }
  else { m.vx = m.vy = m.vz = 0; m.goal = null; }
  m.yaw = Math.atan2(m.vx, -m.vz) || m.yaw; m.moving = true;
}
function updateBeast(m, dt){
  if(BEAST[m.kind].fly || BEAST[m.kind].swim) return updateFlyer(m, dt);""")
# beasts that a villager fights back... flyers fine. Spawning bats (night, in the air; or in caves) and fish (in water near you)
rep("function trySpawnBeasts(){", r"""function trySpawnFlyers(cnt){
  // bats: at night over open land, or any time in a cave while you're underground
  const under = player.y < colInfo(Math.floor(player.x),Math.floor(player.z)).h - 6;
  if((ratNight || under) && (cnt.bat||0) < BEAST.bat.max && Math.random()<0.5){
    for(let t=0;t<20;t++){
      const x = Math.floor(player.x + (Math.random()-0.5)*40), z = Math.floor(player.z + (Math.random()-0.5)*40);
      if(Math.hypot(x-player.x, z-player.z) < 14 || nearVillage(x,z)) continue;
      const y = under ? Math.floor(player.y + (Math.random()-0.5)*8) : colInfo(x,z).h + 3 + Math.floor(Math.random()*4);
      if(!PASS[getB(x,y,z)] || IS_WATER[getB(x,y,z)] || !PASS[getB(x,y+1,z)]) continue;
      if(under && ratTop(x,z) <= y+2) continue;                                       // cave bats stay under rock
      for(let n=roll(2,4); n>0 && (cnt.bat||0)<BEAST.bat.max; n--){ mobs.push(newBeast('bat', x, y, z)); cnt.bat = (cnt.bat||0)+1; }
      return;
    }
  }
  // slaughterfish: in lakes and rivers deep enough to swim in
  if((cnt.fish||0) < BEAST.fish.max && Math.random()<0.5){
    for(let t=0;t<24;t++){
      const x = Math.floor(player.x + (Math.random()-0.5)*44), z = Math.floor(player.z + (Math.random()-0.5)*44);
      if(Math.hypot(x-player.x, z-player.z) < 10) continue;
      const ci = colInfo(x,z); if(ci.h >= SEA-2 || ci.open) continue;
      const y = ci.h + 1 + Math.floor(Math.random()*Math.max(1, SEA-ci.h-2));
      if(!IS_WATER[getB(x,y,z)] || !IS_WATER[getB(x,y+1,z)]) continue;
      for(let n=roll(1,3); n>0 && (cnt.fish||0)<BEAST.fish.max; n--){ mobs.push(newBeast('fish', x, y, z)); cnt.fish = (cnt.fish||0)+1; }
      return;
    }
  }
}
function trySpawnBeasts(){
  { const c = {}; for(const m of mobs) if(m.kind==='bat' || m.kind==='fish') c[m.kind] = (c[m.kind]||0)+1; trySpawnFlyers(c); }""")
rep("    const opts = Object.keys(BEAST).filter(k=>{ const K=BEAST[k]; return K.where(b,y) && (!K.night || ratNight) && (cnt[k]||0)<K.max; });",
    "    const opts = Object.keys(BEAST).filter(k=>{ const K=BEAST[k]; return !K.fly && !K.swim && K.where(b,y) && (!K.night || ratNight) && (cnt[k]||0)<K.max; });")
rep("  for(const m of mobs) if(BEAST[m.kind]){ cnt[m.kind] = (cnt[m.kind]||0)+1; total++; }", "  for(const m of mobs) if(BEAST[m.kind] && m.kind!=='bat' && m.kind!=='fish'){ cnt[m.kind] = (cnt[m.kind]||0)+1; total++; }")
# models
rep("  else if(BEAST[m.kind].undead){", r"""  else if(m.kind==='bat'){
    // a giant bat: furry body, big ears, leathery wings beating up and down
    const B = [70,54,46], D = [48,36,30], W = [96,70,60], f = Math.sin(m.flap||0);
    add(0,0.18,0, 0.3,0.3,0.36, B,5,D);
    add(0,0.3,0.24, 0.22,0.2,0.16, B,5,D);
    for(const sx of [-1,1]){ add(sx*0.07,0.5,0.26, 0.06,0.12,0.05, D); add(sx*0.06,0.38,0.325, 0.05,0.04,0.01, [230,60,40],0,0,true);
      add(sx*0.33,0.28+f*0.12,0, 0.36,0.04,0.34, W,5,D); add(sx*0.66,0.28+f*0.3,-0.04, 0.32,0.03,0.28, W,5,D); }
    add(0,0.21+A*0.03,0.335, 0.1,0.04,0.02, [236,232,220]);                         // fangs
  } else if(m.kind==='fish'){
    // a slaughterfish: a long armoured body, a red belly, a row of teeth and a sweeping tail
    const B = [92,118,98], D = [64,84,70], R = [168,72,60], sw = Math.sin(m.flap||0)*0.12;
    add(0,0.12,0, 0.3,0.3,0.9, B,5,D); add(0,0.06,0.05, 0.26,0.08,0.7, R,5,[140,56,48]);
    add(0,0.12,0.5+A*0.06, 0.26,0.22,0.2, B,5,D);
    add(0,0.13,0.6+A*0.06, 0.2,0.03,0.04, [236,232,220]); add(0,0.27,0.6+A*0.06, 0.2,0.03,0.04, [236,232,220]);       // jaws of teeth
    for(const sx of [-1,1]){ add(sx*0.135,0.26,0.5, 0.02,0.05,0.05, [220,200,60]); add(sx*0.2,0.12,0.15, 0.12,0.03,0.14, D); }
    add(0,0.42,0, 0.04,0.14,0.36, D);                                                  // dorsal fin
    add(sw,0.14,-0.52, 0.06,0.2,0.16, D); add(sw*1.6,0.12,-0.66, 0.04,0.34,0.14, D);  // tail
  } else if(BEAST[m.kind].undead){""")
open(p,'w').write(s); print('ok')
