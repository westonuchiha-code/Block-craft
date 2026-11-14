p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# ---------- daedra ----------
rep("  scorpion: { hp:20, bite:3, cd:1.3,", """  daedra:   { hp:26, bite:4, cd:1.1, walk:0.035, run:0.08, aggro:18, memory:30, reach:1.7, tall:2.2, br:2.6, rect:2.6, max:0, group:[1,1], weight:0, undead:true, demon:true, ranged:true,
              where:()=>false, drops:[[EMBER,1,3]], gold:[10,30] },
  daedroth: { hp:48, bite:7, cd:1.3, walk:0.03, run:0.075, aggro:14, memory:30, reach:2.2, tall:2.6, br:3.0, rect:3.0, max:0, group:[1,1], weight:0, undead:true, demon:true,
              where:()=>false, drops:[[BONE,1,3]], gold:[20,50] },
  scorpion: { hp:20, bite:3, cd:1.3,""")
# undead flag on demons gives free pathing; keep their drops/undead-only perks separate (ranger bonus excluded is fine)
rep("    if(m.kind==='cryptlord'){ spawnDrop(x,y,z, Math.random()<0.25 ? MITH_INGOT : ADAM_INGOT);", "    if(m.kind==='daedroth' && Math.random()<0.35) spawnDrop(x,y,z, Math.random()<0.2 ? MITH_INGOT : ADAM_INGOT);\n    if(m.kind==='cryptlord'){ spawnDrop(x,y,z, Math.random()<0.25 ? MITH_INGOT : ADAM_INGOT);")
# ranged attack: hurl a fireball when in sight, at mid range
rep("  if(m.angry>0){\n    m.angry -= dist > K.aggro*2.5+8 ? dt*3 : dt*0.2;", """  if(K.ranged && m.angry>0 && !dead){
    m.shotCd = (m.shotCd||1.5) - dt;
    const hd = Math.hypot(dxp,dzp);
    if(m.shotCd<=0 && hd>3 && hd<18 && Math.abs(dyp)<8){
      const ox = m.x, oy = m.y+1.7, oz = m.z, tx = player.x, ty = player.y+1.2, tz = player.z, d = Math.hypot(tx-ox,ty-oy,tz-oz)||1;
      let clear = true; for(let t=1; t<d-1; t+=0.5){ const b = getB(Math.floor(ox+(tx-ox)*t/d), Math.floor(oy+(ty-oy)*t/d), Math.floor(oz+(tz-oz)*t/d)); if(!PASS[b] && !IS_LAVA[b]){ clear = false; break; } }
      if(clear){ fx.push({ kind:'ball', enemy:true, x:ox, y:oy, z:oz, vx:(tx-ox)/d*13, vy:(ty-oy)/d*13, vz:(tz-oz)/d*13, age:0, trail:[], dmg:lvlDmg(4, m.lvl) }); m.shotCd = 2.6 + Math.random(); m.atkA = 1; m.yaw = Math.atan2(dxp,-dzp); }
      else m.shotCd = 0.5;
    }
  }
  if(m.angry>0){
    m.angry -= dist > K.aggro*2.5+8 ? dt*3 : dt*0.2;""")
# enemy fireballs: hit you (armor applies), not the beasts; still set things alight
rep("""        for(const m of mobs){
          if(m.dead || m.removed || !m.kind) continue;
          const yy = Math.max(m.y, Math.min(m.y+mobTall(m), e.y));""", """        if(e.enemy){ if(Math.hypot(player.x-e.x, Math.max(player.y, Math.min(player.y+1.7, e.y))-e.y, player.z-e.z) < 0.7){ hurt(e.dmg||4); stop = true; } }
        else for(const m of mobs){
          if(m.dead || m.removed || !m.kind) continue;
          const yy = Math.max(m.y, Math.min(m.y+mobTall(m), e.y));""")
rep("      if(stop){ fx.splice(i,1); fxExplode(e, hitMob); }", "      if(stop){ fx.splice(i,1); if(e.enemy){ fx.push({ kind:'boom', x:e.x, y:e.y, z:e.z, age:0, seed:Math.random()*1000, size:0.7 }); const gx = Math.floor(e.x), gy = Math.floor(e.y), gz = Math.floor(e.z); for(let a=-1;a<=1;a++) for(let c=0;c<=1;c++) for(let d=-1;d<=1;d++) if(Math.random()<0.3) ignite(gx+a,gy+c,gz+d); } else fxExplode(e, hitMob); }")
# models
rep("  } else if(BEAST[m.kind].undead){", r"""  } else if(BEAST[m.kind].demon){
    // daedra: a fire daedra is a horned, black-and-ember figure with burning hands; a daedroth is a hulking crocodile-headed brute
    const fd = m.kind==='daedra', S = fd ? 1.05 : 1.3, bob = run*Math.abs(Math.sin(ph))*0.03;
    const A2 = (cx,cy,cz,w,h,l,col,pt,col2,glow)=>add(cx*S,cy*S+bob,cz*S,w*S,h*S,l*S,col,pt,col2,glow);
    const SK = fd ? [62,22,20] : [74,96,52], SD = fd ? [40,14,14] : [56,74,40], EM = [255,140,30];
    const lg = i=>Math.sin(ph*1.6+(i?Math.PI:0))*0.18*run;
    for(const i of [0,1]){ const x = i ? 0.13 : -0.13; A2(x,0,lg(i)*0.5, 0.2,0.78,0.22, SK,5,SD); if(!fd) A2(x,0,lg(i)*0.5+0.12, 0.22,0.07,0.1, [220,214,190]); }
    A2(0,0.78,0, 0.52,0.74,0.3, SK,5,SD);
    if(fd){ A2(0,1.05,0.151, 0.08,0.4,0.01, EM,0,0,true); A2(-0.12,0.95,0.151, 0.06,0.2,0.01, EM,0,0,true); A2(0.13,1.2,0.151, 0.05,0.18,0.01, EM,0,0,true); }   // glowing cracks
    else { A2(0,0.86,-0.36, 0.2,0.18,0.5, SK,5,SD); A2(0,0.8,-0.68, 0.12,0.12,0.3, SD); A2(0,1.2,-0.1, 0.4,0.24,0.06, [96,120,64]); }   // tail, spines
    for(const i of [0,1]){ const x = i ? 0.35 : -0.35, atk = A*(i ? 1 : 0.4);
      A2(x,0.84+atk*0.3,-lg(i)*0.6+atk*0.35, 0.18,0.68,0.18, SK,5,SD);
      if(fd) A2(x,0.76+atk*0.3,-lg(i)*0.6+atk*0.35, 0.22,0.14,0.22, [255,190,60],0,0,true);                // burning hands
      else A2(x,0.78+atk*0.3,-lg(i)*0.6+atk*0.35+0.1, 0.2,0.08,0.06, [220,214,190]); }                        // claws
    if(fd){ A2(0,1.52,0, 0.42,0.42,0.4, SK,5,SD); for(const sx of [-1,1]){ A2(sx*0.17,1.94,0, 0.08,0.2,0.08, [30,20,18]); A2(sx*0.24,2.1,0, 0.06,0.12,0.06, [30,20,18]); A2(sx*0.1,1.68,0.201, 0.1,0.06,0.01, [255,230,80],0,0,true); } }
    else { A2(0,1.48,0.05, 0.44,0.4,0.44, SK,5,SD); A2(0,1.5,0.45+A*0.05, 0.3,0.2,0.4, SK,5,SD); A2(0,1.47-A*0.05,0.45, 0.28,0.06,0.38, [150,40,40]);
      for(const z of [0.3,0.42,0.54,0.62]) for(const sx of [-1,1]) A2(sx*0.15,1.46,z, 0.03,0.05,0.03, [236,230,210]);
      for(const sx of [-1,1]) A2(sx*0.16,1.74,0.22, 0.08,0.06,0.04, [240,200,40],0,0,true); }
  } else if(BEAST[m.kind].undead){""")
# the undead branch must not catch demons first: demon branch placed before it. Undead-pathing for demons via K.undead flag (already set).
# spawning in the underworld (with the beetles, every 20s)
rep("ogreSpawnT -= dt; if(ogreSpawnT<=0){ ogreSpawnT = 20; if(!underNow){ trySpawnOgre(); trySpawnMino(); } else trySpawnBeetles(); }",
    "ogreSpawnT -= dt; if(ogreSpawnT<=0){ ogreSpawnT = 20; if(!underNow){ trySpawnOgre(); trySpawnMino(); } else { trySpawnBeetles(); if(isUnder(player.z)) trySpawnDaedra(); } }")
rep("function trySpawnBeetles(force){", r"""// daedra walk the underworld: fire daedra hurl flame from a distance, daedroths close in to tear
function trySpawnDaedra(){
  let n = 0; for(const m of mobs) if(m.kind==='daedra' || m.kind==='daedroth') n++;
  if(n>=3 || Math.random()>0.55) return;
  for(let t=0;t<12;t++){
    const a = Math.random()*6.283, r = 18+Math.random()*16, x = Math.floor(player.x+Math.cos(a)*r), z = Math.floor(player.z+Math.sin(a)*r);
    const c = underCol(x,z); if(c.hf<=UNDER_LAVA+1 || c.hf>=c.hc-4) continue;
    const y = c.hf+1; if(!PASS[getB(x,y,z)] || !PASS[getB(x,y+1,z)] || !PASS[getB(x,y+2,z)]) continue;
    mobs.push(newBeast(Math.random()<0.6 ? 'daedra' : 'daedroth', x, y, z)); return;
  }
}
function trySpawnBeetles(force){""")
rep("const nm = { bear:'a grizzly bear',", "const nm = { daedra:'fire daedra', daedroth:'a daedroth', bat:'giant bats', fish:'slaughterfish', bear:'a grizzly bear',")
rep("const BEAST_NAME = { skeleton:'skeleton',", "const BEAST_NAME = { daedra:'fire daedra', daedroth:'daedroth', bat:'giant bat', fish:'slaughterfish', skeleton:'skeleton',")
# ---------- the map works in the underworld too ----------
rep("function exploreTick(){\n  if(testWorld || isUnder(player.z) || isTestZ(player.z)) return;", "function exploreTick(){\n  if(testWorld || isTestZ(player.z)) return;\n  if(isUnder(player.z)){ const cx = Math.floor(player.x/CS), cz = Math.floor(player.z/CS); for(let a=-3;a<=3;a++) for(let b=-3;b<=3;b++) if(a*a+b*b<=10) explored.add((cx+a)+','+(cz+b)); return; }")
rep("    const x = cx*CS+i*2, z = cz*CS+j*2, ci = colInfo(x,z);\n    let col = ci.h<=SEA && !ci.open ? [52,92,170] : (COLORS[ci.top] || [120,120,120]);",
    "    const x = cx*CS+i*2, z = cz*CS+j*2;\n    if(isUnder(z)){ const u = underCol(x,z), col = u.hf<=UNDER_LAVA ? [230,90,20] : u.hf>=u.hc ? [60,24,40] : [120,48,80], sh = 0.7 + Math.max(0,Math.min(0.4,(u.hf-UNDER_LAVA)/60)); const o = (j*8+i)*4; img.data[o]=col[0]*sh; img.data[o+1]=col[1]*sh; img.data[o+2]=col[2]*sh; img.data[o+3]=255; continue; }\n    const ci = colInfo(x,z);\n    let col = ci.h<=SEA && !ci.open ? [52,92,170] : (COLORS[ci.top] || [120,120,120]);")
rep("  for(let k=1;k<=5;k++){ const [cx0,cy0] = toS(0,0); g.beginPath(); g.arc(cx0, cy0, k*450*S, 0, Math.PI*2); g.stroke(); }",
    "  if(!isUnder(player.z)) for(let k=1;k<=5;k++){ const [cx0,cy0] = toS(0,0); g.beginPath(); g.arc(cx0, cy0, k*450*S, 0, Math.PI*2); g.stroke(); }")
rep("  let h = `<div class=\"skNote\">You are in ${DANGER_NAMES[Math.min(5,Math.floor(Math.hypot(player.x,player.z)/450))]} (danger ${dz}).",
    "  let h = `<div class=\"skNote\">You are in ${isUnder(player.z) ? 'the Underworld' : DANGER_NAMES[Math.min(5,Math.floor(Math.hypot(player.x,player.z)/450))]} (danger ${dz}).")
# test hall: add daedra to the beetle room
rep("[1,0,{name:'BEETLE FOLK', h:8, floor:FLESH, wall:FLESH2, mobs:['beetle',3]}]", "[1,0,{name:'BEETLE FOLK + DAEDRA', h:8, floor:FLESH, wall:FLESH2, mobs:['beetle',3]}]")
open(p,'w').write(s); print('ok')
