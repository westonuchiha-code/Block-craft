p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
rep("const SIGNPOST = 1131, SPELLMAKER = 1132;", "const SIGNPOST = 1131, SPELLMAKER = 1132, FIRE = 1135, TINDERBOX = 1136;")
rep("  NAMES[SPELLMAKER] = 'spellmaker';", """  // fire: a few tongues of flame, walk-through, bright
  IS_SHAPED[FIRE]=1; PASS[FIRE]=1; SH_BOXES[FIRE]=[[.08,0,.1,.32,.72,.34],[.6,0,.12,.86,.92,.4],[.16,0,.6,.44,.84,.88],[.56,0,.56,.9,.62,.9],[.34,0,.34,.66,1,.66]]; COLORS[FIRE]=[255,150,40]; NAMES[FIRE]='fire';
  NAMES[TINDERBOX] = 'tinderbox'; COLORS[TINDERBOX] = [120,110,104];
  NAMES[SPELLMAKER] = 'spellmaker';""")
rep("  if(IS_VINE[b]){ const g = h3(cx,Math.floor(py*8)+cy*8,cz,614);", """  if(b===FIRE){                                                        // flickering flame: white-yellow at the root, orange, then red at the tips
    const fr = performance.now()/90, n = vnoise((tx+cx*3)/2.5, (ty + fr)/2.2, 615), hgt = py + n*0.35;
    _pr.col = hgt<0.3 ? [255,246,170] : hgt<0.6 ? [255,190,60] : hgt<0.85 ? [250,120,30] : [210,60,20]; _pr.glow = true;
    return _pr;
  }
  if(IS_VINE[b]){ const g = h3(cx,Math.floor(py*8)+cy*8,cz,614);""")
rep("|| id===CAP_T || id===LAMP || id===EMBER || id===CANDLE) IS_EMIT[id] = 1;", "|| id===CAP_T || id===LAMP || id===EMBER || id===CANDLE || id===FIRE) IS_EMIT[id] = 1;")
rep("|| id===CANDLE || IS_WBP[id]) LIGHT_PASS[id] = 1;", "|| id===CANDLE || IS_WBP[id] || id===FIRE) LIGHT_PASS[id] = 1;")
rep("IS_EMIT[LANT_OFF0]=IS_EMIT[LANT_OFF0+1]=0;", """HARD[FIRE]=0; HAND_OK.add(FIRE); DROP[FIRE]=0; FLAT_ITEMS.add(TINDERBOX);
// what burns: anything made of wood, leaves, straw, cloth or paper, and plants
const IS_FLAM = new Uint8Array(NB);
for(let id=0; id<NB; id++){
  if(IS_LOG[id] || IS_LEAF[id] || IS_PLANT[id] || IS_SAP[id] || IS_FLOWER[id] || IS_BED[id] || IS_DOOR[id] || IS_FENCE[id] || IS_GATE[id] || IS_VINE[id]) IS_FLAM[id] = 1;
  if(IS_FURN[id] && id!==CANDLE) IS_FLAM[id] = 1;
  if(IS_SHAPED[id] && PLANK_IDS.includes(SH_BASE[id])) IS_FLAM[id] = 1;                       // wooden slabs, stairs, corners
}
for(const id of [...PLANK_IDS, HAY, THATCH, BOOKSHELF, CRAFT_TABLE, BARREL, CRATE, FRAME, FRAME_X, FRAME_D1, FRAME_D2, BEAM, SHINGLE, DARKWOOD, PALM_LOG, PALM_LEAF, CACTUS, LITTER, TALL_GRASS, HEDGE]) IS_FLAM[id] = 1;
for(let i=0;i<12;i++){ IS_FLAM[WOOL0+i] = 1; IS_FLAM[RUG0+i] = 1; }
IS_EMIT[LANT_OFF0]=IS_EMIT[LANT_OFF0+1]=0;""")
# ---------- fire life ----------
rep("function fxExplode(b, direct){", r"""// ---------- fire: it catches on wood, leaves, straw and cloth, spreads to whatever burns nearby, eats it, and dies down ----------
// Rain puts it out in the open, water beside it puts it out at once. Standing in it hurts (armor doesn't help). Burning down part
// of a village costs you its goodwill.
const fires = new Map();
let fireT = 0, fireDmgT = 0, fireRepT = 0;
function fireCanSit(x,y,z){ const b = getB(x,y,z); if(!(b===AIR || (IS_PLANT[b] && b!==CATNIP_RIPE))) return false; return !PASS[getB(x,y-1,z)] || fireFuelNear(x,y,z); }
function fireFuelNear(x,y,z){ for(const [a,b,c] of WDIRS) if(IS_FLAM[getB(x+a,y+b,z+c)]) return true; return false; }
function ignite(x,y,z){
  if(fires.size>=300 || !fireCanSit(x,y,z)) return false;
  for(const [a,b,c] of WDIRS) if(IS_WATER[getB(x+a,y+b,z+c)]) return false;
  setB(x,y,z,FIRE); fires.set(x+','+y+','+z, { x,y,z, t:0, life: 6 + Math.random()*10 }); return true;
}
function burnBlock(x,y,z){
  const b = getB(x,y,z); if(!IS_FLAM[b]) return;
  if(IS_BED[b]){ const o = bedOther(b,x,y,z); if(IS_BED[getB(o[0],o[1],o[2])]) setB(o[0],o[1],o[2],AIR); }
  if(IS_DOOR[b]){ const oy = y+(SH_HALF[b]?-1:1); if(IS_DOOR[getB(x,oy,z)]) setB(x,oy,z,AIR); }
  setB(x,y,z,AIR); placedSet.delete(x+','+y+','+z);
  if(IS_LOG[b] || IS_LEAF[b]) queueLeafScan(x,y,z);
  if(fireRepT<=0 && worldGen>=2){ const rx = Math.floor(x/VREG), rz = Math.floor(z/VREG), v = villageAt(rx,rz);
    if(v && v.rects && inVillageRects(v,x,z,0)){ addRep([rx,rz], -2); fireRepT = 3; } }
  if(Math.random()<0.6) ignite(x,y,z);
}
function fireTick(dt){
  fireDmgT -= dt; fireRepT -= dt;
  // standing in flames hurts; so do the beasts
  if(fireDmgT<=0){ fireDmgT = 0.5;
    const fx0 = Math.floor(player.x), fz0 = Math.floor(player.z);
    if(getB(fx0,Math.floor(player.y),fz0)===FIRE || getB(fx0,Math.floor(player.y+1),fz0)===FIRE) hurt(1, true);
    for(const m of mobs) if(!m.dead && getB(Math.floor(m.x),Math.floor(m.y+0.2),Math.floor(m.z))===FIRE) mobDamage(m, 2, null); }
  fireT += dt; if(fireT<0.25 || !fires.size) return; const step = fireT; fireT = 0;
  let edits = 0;
  for(const [k,f] of fires){
    if(getB(f.x,f.y,f.z)!==FIRE){ fires.delete(k); continue; }
    f.t += step;
    const wet = WDIRS.some(([a,b,c])=>IS_WATER[getB(f.x+a,f.y+b,f.z+c)]) || (rainOn && biomeAt(f.x,f.z)<3 && ratTop(f.x,f.z)<=f.y+1 && Math.random()<0.15);
    const fuel = fireFuelNear(f.x,f.y,f.z);
    if(wet || f.t>f.life || (!fuel && f.t>2.5)){ setB(f.x,f.y,f.z,AIR); fires.delete(k); if(++edits>24) break; continue; }
    if(!fuel || edits>24) continue;
    // eat a neighbour now and then, and leap to nearby spots beside more fuel
    for(const [a,b,c] of WDIRS){ const x = f.x+a, y = f.y+b, z = f.z+c; if(IS_FLAM[getB(x,y,z)] && Math.random() < 0.035*step*4){ burnBlock(x,y,z); edits++; } }
    if(Math.random() < 0.22*step*4){ const x = f.x + Math.floor(Math.random()*3)-1, y = f.y + Math.floor(Math.random()*4)-1, z = f.z + Math.floor(Math.random()*3)-1;
      if(fireFuelNear(x,y,z) && ignite(x,y,z)) edits++; }
  }
  if(fires.size>300) for(const [k,f] of fires){ if(fires.size<=300) break; setB(f.x,f.y,f.z,AIR); fires.delete(k); }
}
// lava sets light to things that burn beside it (looked for now and then, near you)
function lavaFireTick(){
  for(let t=0;t<30;t++){
    const x = Math.floor(player.x + (Math.random()-0.5)*32), y = Math.floor(player.y + (Math.random()-0.5)*16), z = Math.floor(player.z + (Math.random()-0.5)*32);
    if(!IS_LAVA[getB(x,y,z)]) continue;
    for(let a=-2;a<=2;a++) for(let b=0;b<=2;b++) for(let c=-2;c<=2;c++) if(Math.random()<0.05 && fireFuelNear(x+a,y+b,z+c)) ignite(x+a,y+b,z+c);
  }
}
function fxExplode(b, direct){
  { const gx = Math.floor(b.x), gy = Math.floor(b.y), gz = Math.floor(b.z);                                // a fireball sets alight whatever burns around it
    for(let a=-2;a<=2;a++) for(let c=-1;c<=2;c++) for(let d=-2;d<=2;d++){ if(a*a+c*c+d*d>5) continue; const x = gx+a, y = gy+c, z = gz+d;
      if(fireFuelNear(x,y,z) ? Math.random()<0.6 : Math.random()<0.08) ignite(x,y,z); } }""")
# lightning sets fire where it strikes the ground
rep("    } else pts.push(aim);\n    fx.push({ kind:'bolt', pts, age:0, hand:true });", "    } else { pts.push(aim); if(bh && Math.random()<0.4) ignite(Math.floor(aim[0]-f[0]*0.3), Math.floor(aim[1]-f[1]*0.3), Math.floor(aim[2]-f[2]*0.3)); }\n    fx.push({ kind:'bolt', pts, age:0, hand:true });")
# ticking
rep("function updateMobs(){\n  const dt = frameScale/60;\n  mpTick(dt);", "function updateMobs(){\n  const dt = frameScale/60;\n  mpTick(dt); fireTick(dt);")
rep("  exploreT -= dt; if(exploreT<=0){ exploreT = 1; exploreTick(); cryptTick(); }", "  exploreT -= dt; if(exploreT<=0){ exploreT = 1; exploreTick(); cryptTick(); lavaFireTick(); }")
# tinderbox: strike a spark where you aim
rep("  const hit = target();\n  if(!hit) return;\n  if(hit.b === CRAFT_TABLE){ openCraft(3); return; }", """  const hit = target();
  if(!hit) return;
  if(HOTBAR[sel]===TINDERBOX && inv[TINDERBOX]>0){ const x = hit.x+(hit.nx|0), y = hit.y+(hit.ny|0), z = hit.z+(hit.nz|0); if(hit.b===GATE && lightGate(hit.x,hit.y,hit.z)) return; ignite(x,y,z) || skillToast('nothing here will catch'); return; }
  if(hit.b === CRAFT_TABLE){ openCraft(3); return; }""")
rep("  { out:[SPELLMAKER,1],   pat:['CBC','SSS'],", "  { out:[TINDERBOX,1],    pat:['I','C'],               key:{I:IRON_INGOT, C:COAL_ITEM} },\n  { out:[SPELLMAKER,1],   pat:['CBC','SSS'],")
rep("  { name:'Spellmaker',", "  { name:'Tinderbox',          out:[TINDERBOX,1],    ing:{[IRON_INGOT]:1, [COAL_ITEM]:1} },\n  { name:'Spellmaker',")
rep("    case SACK: paintIcon(g,(P,E)=>{", """    case TINDERBOX: paintIcon(g,(P,E)=>{ for(let y=7;y<=13;y++) for(let x=3;x<=12;x++) P(x,y, y===7||x===3 ? [150,140,132] : y===13||x===12 ? [70,64,60] : [112,104,98]);
              for(let x=4;x<=11;x++) P(x,10,[84,60,40]); P(10,4,[255,220,90]); P(11,3,[255,170,40]); P(9,5,[255,190,60]); P(12,5,[255,240,170]); }); return true;
    case SACK: paintIcon(g,(P,E)=>{""")
rep("SHORT[GOLD]='gold';", "SHORT[TINDERBOX]='tinder'; SHORT[GOLD]='gold';")
rep("  P(SPELLMAKER, 120);", "  P(SPELLMAKER, 120); P(TINDERBOX, 25);")
rep("STONE_SWORD, IRON_PICK, IRON_AXE, IRON_SHOVEL, IRON_SWORD, IRON_INGOT,", "STONE_SWORD, IRON_PICK, IRON_AXE, IRON_SHOVEL, IRON_SWORD, IRON_INGOT, TINDERBOX,")
# save / load
rep("gold, armor, book, bookSel, mp,", "gold, armor, book, bookSel, mp, fires:[...fires.values()].slice(0,300),")
rep("  book = meta.book || [];", "  fires.clear(); for(const f of (meta.fires||[])) fires.set(f.x+','+f.y+','+f.z, f);\n  book = meta.book || [];")
rep("  add('MAGIC', [SPELLMAKER,", "  add('FIRE', [TINDERBOX, HAY, THATCH, PLANKS, WOOL0, BOOKSHELF]);\n  add('MAGIC', [SPELLMAKER,")
open(p,'w').write(s); print('ok')
