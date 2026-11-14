p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# ---------- ids, names ----------
rep("const SACK = 1089;", """// ---- metals: iron, adamantite and mithril (the rarest and best). Ores lie deeper the better they are; smelt them into ingots. ----
const IRON_ORE = 1090, ADAM_ORE = 1091, MITH_ORE = 1092, IRON_INGOT = 1093, ADAM_INGOT = 1094, MITH_INGOT = 1095;
const METAL_TOOL0 = 1096;          // 1096..1110: iron, adamantite, mithril x pick, axe, shovel, sword, hoe
const MT = (tier3, k)=>METAL_TOOL0 + tier3*5 + k;          // tier3: 0 iron, 1 adamantite, 2 mithril; k: 0 pick, 1 axe, 2 shovel, 3 sword, 4 hoe
const IRON_PICK = MT(0,0), IRON_AXE = MT(0,1), IRON_SHOVEL = MT(0,2), IRON_SWORD = MT(0,3), IRON_HOE = MT(0,4);
const ADAM_PICK = MT(1,0), ADAM_AXE = MT(1,1), ADAM_SHOVEL = MT(1,2), ADAM_SWORD = MT(1,3), ADAM_HOE = MT(1,4);
const MITH_PICK = MT(2,0), MITH_AXE = MT(2,1), MITH_SHOVEL = MT(2,2), MITH_SWORD = MT(2,3), MITH_HOE = MT(2,4);
const METALS = [ { key:'iron', name:'iron', ore:IRON_ORE, ingot:IRON_INGOT, tier:3, dur:250 },
                 { key:'adam', name:'adamantite', ore:ADAM_ORE, ingot:ADAM_INGOT, tier:4, dur:900 },
                 { key:'mith', name:'mithril', ore:MITH_ORE, ingot:MITH_INGOT, tier:5, dur:1600 } ];
NAMES[IRON_ORE] = 'iron ore'; NAMES[ADAM_ORE] = 'adamantite ore'; NAMES[MITH_ORE] = 'mithril ore';
COLORS[IRON_ORE] = [150,138,128]; COLORS[ADAM_ORE] = [110,138,124]; COLORS[MITH_ORE] = [150,166,190];
NAMES[IRON_INGOT] = 'iron ingot'; NAMES[ADAM_INGOT] = 'adamantite ingot'; NAMES[MITH_INGOT] = 'mithril ingot';
COLORS[IRON_INGOT] = [196,196,204]; COLORS[ADAM_INGOT] = [70,150,112]; COLORS[MITH_INGOT] = [196,222,255];
for(const id of [IRON_INGOT, ADAM_INGOT, MITH_INGOT]) FLAT_ITEMS.add(id);
METALS.forEach((M,t)=>['pickaxe','axe','shovel','sword','hoe'].forEach((k,i)=>{ NAMES[MT(t,i)] = M.name+' '+k; }));
const SACK = 1089;""")
# ---------- tools ----------
rep("  [STONE_HOE]:    { kind:'hoe',    tier:2, speed:1,   dur:131 }\n};",
    "  [STONE_HOE]:    { kind:'hoe',    tier:2, speed:1,   dur:131 }\n};\nMETALS.forEach((M,t)=>['pick','axe','shovel','sword','hoe'].forEach((k,i)=>{ TOOLS[MT(t,i)] = { kind:k, tier:M.tier, speed:1, dur:M.dur }; }));")
rep("const TIER_POW = { 1:1.25, 2:1.7, 3:2.5, 4:4.5 };", "const TIER_POW = { 1:1.25, 2:1.7, 3:2.5, 4:3.4, 5:4.5 };          // wood, stone, iron, adamantite, mithril")
rep("// power (wood 1.25, stone 1.7, iron 2.5, the top tier 4.5).", "// power (wood 1.25, stone 1.7, iron 2.5, adamantite 3.4, mithril 4.5).")
rep("  const soft = base<=5 && T && T.tier>=4;                                      // top-tier shovel on soft ground: one stroke",
    "  const soft = base<=5 && T && T.tier>=5;                                      // a mithril shovel on soft ground: one stroke")
rep("S(COAL, 11);", "S(COAL, 11); S(IRON_ORE, 12); S(ADAM_ORE, 16); S(MITH_ORE, 20);")
rep("const REQ_TIER = { ", "const REQ_TIER = { [IRON_ORE]:2, [ADAM_ORE]:3, [MITH_ORE]:4, ")
rep("const KIND = { ", "const KIND = { [IRON_ORE]:'pick', [ADAM_ORE]:'pick', [MITH_ORE]:'pick', ")
rep("function toolKind(id){ return (id===WOOD_HOE || id===STONE_HOE) ? 4 : (id-WOOD_PICK)%4; }",
    "function toolKind(id){ return ({pick:0, axe:1, shovel:2, sword:3, hoe:4})[TOOLS[id].kind]; }")
rep("  const kind=toolKind(id), stone=id>=STONE_PICK && id<=STONE_SWORD || id===STONE_HOE;", "  const kind=toolKind(id);")
rep("  const hr = stone ? STONE_HEAD_RGB : WOOD_HEAD_RGB;", "  const hr = HEAD_RGB[TOOLS[id].tier] || WOOD_HEAD_RGB;")
rep("const STONE_HEAD_RGB = [[201,201,201],[154,154,154],[95,95,95]];  // stone head",
    "const STONE_HEAD_RGB = [[201,201,201],[154,154,154],[95,95,95]];  // stone head\nconst HEAD_RGB = { 1:WOOD_HEAD_RGB, 2:STONE_HEAD_RGB, 3:[[236,236,240],[188,190,198],[118,120,130]], 4:[[150,226,188],[72,158,118],[30,92,66]], 5:[[236,246,255],[170,206,246],[104,136,188]] };")
rep("HEADC = T ? (T.tier>=2 ? [136,136,144] : [176,134,76]) : null;", "HEADC = T ? ({1:[176,134,76], 2:[136,136,144], 3:[196,198,206], 4:[72,158,118], 5:[176,210,248]})[T.tier] : null;")
rep("(r.out[0] >= WOOD_PICK && r.out[0] <= STONE_SWORD) || r.out[0]===WOOD_HOE || r.out[0]===STONE_HOE ||", "!!TOOLS[r.out[0]] ||")
rep("if((hb===WOOD_HOE || hb===STONE_HOE) && inv[hb]>0){ hoeUse(hb); return; }", "if(TOOLS[hb] && TOOLS[hb].kind==='hoe' && inv[hb]>0){ hoeUse(hb); return; }")
for k in ['IRON','ADAM','MITH']: pass
# icons go through the tool sprite path: make sure new tools are not caught by a block-icon branch (they are not FLAT_ITEMS but TOOLS)
# ---------- recipes ----------
rep("  { out:[STONE_HOE,1],    pat:['CC','S ','S '],        key:{C:COBBLE, S:STICK} },",
"""  { out:[STONE_HOE,1],    pat:['CC','S ','S '],        key:{C:COBBLE, S:STICK} },
  ...METALS.flatMap((M,t)=>[
    { out:[MT(t,0),1], pat:['III',' S ',' S '], key:{I:M.ingot, S:STICK} },
    { out:[MT(t,1),1], pat:['II','IS',' S'],    key:{I:M.ingot, S:STICK} },
    { out:[MT(t,1),1], pat:['II','SI','S '],    key:{I:M.ingot, S:STICK} },
    { out:[MT(t,2),1], pat:['I','S','S'],       key:{I:M.ingot, S:STICK} },
    { out:[MT(t,3),1], pat:['I','I','S'],       key:{I:M.ingot, S:STICK} },
    { out:[MT(t,4),1], pat:['II',' S',' S'],    key:{I:M.ingot, S:STICK} },
    { out:[MT(t,4),1], pat:['II','S ','S '],    key:{I:M.ingot, S:STICK} } ]),""")
rep("  { name:'Stone hoe',          out:[STONE_HOE,1],    ing:{[COBBLE]:2, [STICK]:2} },",
"""  { name:'Stone hoe',          out:[STONE_HOE,1],    ing:{[COBBLE]:2, [STICK]:2} },
  ...METALS.flatMap((M,t)=>[['pickaxe',3,2],['axe',3,2],['shovel',1,2],['sword',2,1],['hoe',2,2]].map(([k,ni,ns],i)=>({ name:(M.name[0].toUpperCase()+M.name.slice(1))+' '+k, out:[MT(t,i),1], ing:{[M.ingot]:ni, [STICK]:ns} }))),""")
rep("  { name:'Glass (4 sand, 1 coal)',     out:[GLASS,4], ing:{[SAND]:4, [COAL_ITEM]:1} },",
"""  { name:'Iron ingot (1 iron ore, 1 coal)',             out:[IRON_INGOT,1], ing:{[IRON_ORE]:1, [COAL_ITEM]:1} },
  { name:'Adamantite ingot (1 adamantite ore, 2 coal)', out:[ADAM_INGOT,1], ing:{[ADAM_ORE]:1, [COAL_ITEM]:2} },
  { name:'Mithril ingot (1 mithril ore, 3 coal)',       out:[MITH_INGOT,1], ing:{[MITH_ORE]:1, [COAL_ITEM]:3} },
  { name:'Glass (4 sand, 1 coal)',     out:[GLASS,4], ing:{[SAND]:4, [COAL_ITEM]:1} },""")
# ---------- world generation: ore veins, deeper is rarer and better ----------
rep("  if(h3(x,y,z,SEED+7)<0.04) return COAL;\n  return y>=h-6 ? stoneFace(x,y,z,h) : rockAt(x,y,z);",
"""  { const o = oreAt(x,y,z); if(o) return o; }
  if(h3(x,y,z,SEED+7)<0.04) return COAL;
  return y>=h-6 ? stoneFace(x,y,z,h) : rockAt(x,y,z);""")
rep("// rock near the surface also grows moss on the low, damp cliffs\nfunction stoneFace(x,y,z,h){",
"""// ore veins: small clumps (a few blocks in a 2x2x2 cell). Iron is found anywhere below y 48; adamantite only below 20; mithril
// only down by the lava, below 11. Roughly: iron 1 block in 150 of deep rock, adamantite 1 in 600, mithril 1 in 1500.
function oreAt(x,y,z){
  const cx = x>>1, cy = y>>1, cz = z>>1;
  if(y<=10 && h3(cx,cy,cz,SEED+93)<0.0012*1.6 && h3(x,y,z,SEED+94)<0.55) return MITH_ORE;
  if(y<=20 && h3(cx,cy,cz,SEED+91)<0.003*1.6 && h3(x,y,z,SEED+92)<0.55) return ADAM_ORE;
  if(y<=48 && h3(cx,cy,cz,SEED+89)<0.0075*1.6 && h3(x,y,z,SEED+90)<0.55) return IRON_ORE;
  return 0;
}
// rock near the surface also grows moss on the low, damp cliffs
function stoneFace(x,y,z,h){""")
# ---------- textures ----------
rep("    TILES.coal=t; }", """    TILES.coal=t; }
  // ORES: stone with clusters of coloured mineral, each with a bright glint (iron: rusty tan; adamantite: deep green; mithril: pale silver-blue)
  const oreTile = (seed, dark, mid, light)=>{ const t=TILES.stone.map(row=>row.slice()), r=R(seed);
    const spots=[[2,1],[10,2],[6,7],[12,9],[2,11],[8,13]];
    for(const [x0,y0] of spots){ const n = 3+Math.floor(r()*3);
      for(let k=0;k<n;k++){ const x=(x0+Math.floor(r()*3))%16, y=(y0+Math.floor(r()*3))%16; t[y][x]=mid; if(r()<0.5) t[(y+1)%16][x]=dark; }
      t[y0%16][(x0+1)%16]=light; }
    return t; };
  TILES.ironOre = oreTile(201, [140,96,64], [206,160,122], [244,214,182]);
  TILES.adamOre = oreTile(202, [26,84,58], [56,150,104], [150,232,190]);
  TILES.mithOre = oreTile(203, [110,140,190], [176,206,244], [255,255,255]);""")
rep("    case ANDESITE: return TILES.andesite[yy][tx];", "    case ANDESITE: return TILES.andesite[yy][tx];\n    case IRON_ORE: return TILES.ironOre[yy][tx];\n    case ADAM_ORE: return TILES.adamOre[yy][tx];\n    case MITH_ORE: return TILES.mithOre[yy][tx];")
# ingot icons
rep("    case SACK: paintIcon(g,(P,E)=>{", """    case IRON_INGOT: case ADAM_INGOT: case MITH_INGOT: paintIcon(g,(P,E)=>{ const c = COLORS[id], lt = scaleC(c,1.2), dk = scaleC(c,0.62);
              for(let y=6;y<=11;y++) for(let x=2+(11-y)*0;x<=13;x++){ const top = y<=7, edge = x===2||x===13||y===11; P(x,y, top ? lt : edge ? dk : c); }
              for(let x=4;x<=11;x++) P(x,5,lt); for(let x=4;x<=7;x++) P(x,6,[255,255,255]); }); return true;
    case SACK: paintIcon(g,(P,E)=>{""")
# ---------- economy hooks ----------
rep("  P(LEATHER, 12);", "  P(IRON_ORE, 8); P(IRON_INGOT, 15); P(ADAM_ORE, 30); P(ADAM_INGOT, 55); P(MITH_ORE, 70); P(MITH_INGOT, 120);\n  METALS.forEach((M,t)=>[3,3,1,2,2].forEach((n,i)=>{ PRICE[MT(t,i)] = Math.round(PRICE[M.ingot]*n*1.4 + 8 + (i===3 ? 10 : 0)); }));\n  P(LEATHER, 12);")
rep("STONE_SWORD, BARS0, LANTERN0+1, WOOD_BUCKET, CROSSBOW],", "STONE_SWORD, IRON_PICK, IRON_AXE, IRON_SHOVEL, IRON_SWORD, IRON_INGOT, BARS0, LANTERN0+1, WOOD_BUCKET, CROSSBOW],")
rep("                buy:[COAL_ITEM, LEATHER, CHITIN, BONE,", "                buy:[COAL_ITEM, IRON_ORE, IRON_INGOT, ADAM_ORE, ADAM_INGOT, MITH_ORE, MITH_INGOT, LEATHER, CHITIN, BONE,")
rep("  miner:      { title:'Quarry goods', sell:[COAL_ITEM, COBBLE, STONE, ANDESITE, GRANITE, DIORITE, STONE_PICK], buy:[COAL_ITEM,",
    "  miner:      { title:'Quarry goods', sell:[COAL_ITEM, COBBLE, STONE, ANDESITE, GRANITE, DIORITE, IRON_ORE, STONE_PICK, IRON_PICK], buy:[COAL_ITEM, IRON_ORE, ADAM_ORE, MITH_ORE,")
rep("const FETCH_WANTS = { blacksmith:[LEATHER,CHITIN,COAL_ITEM],", "const FETCH_WANTS = { blacksmith:[LEATHER,CHITIN,COAL_ITEM,IRON_ORE,IRON_INGOT],")
rep("miner:[COAL_ITEM,COBBLE],", "miner:[COAL_ITEM,COBBLE,IRON_ORE],")
rep("  add('BEAST DROPS + MEAT',", "  add('ORES + METAL', [IRON_ORE, ADAM_ORE, MITH_ORE, IRON_INGOT, ADAM_INGOT, MITH_INGOT, ...Array.from({length:15},(_,i)=>METAL_TOOL0+i)]);\n  add('BEAST DROPS + MEAT',")
rep("SHORT[GOLD]='gold';", "SHORT[IRON_ORE]='i.ore'; SHORT[ADAM_ORE]='a.ore'; SHORT[MITH_ORE]='m.ore'; SHORT[IRON_INGOT]='iron'; SHORT[ADAM_INGOT]='adam.'; SHORT[MITH_INGOT]='mith.';\n['i','a','m'].forEach((p,t)=>['pick','axe','shvl','sword','hoe'].forEach((k,i)=>{ SHORT[MT(t,i)] = p+'.'+k; }));\nSHORT[GOLD]='gold';")
# dungeons / underworld loot: a little metal
rep("  dungeon: [[GOLD,15,80,.85],", "  dungeon: [[GOLD,15,80,.85],[IRON_INGOT,1,4,.45],[ADAM_INGOT,1,1,.06],")
rep("  under:   [[GOLD,20,120,.8],", "  under:   [[GOLD,20,120,.8],[IRON_INGOT,2,5,.5],[ADAM_INGOT,1,2,.15],[MITH_INGOT,1,1,.05],")
open(p,'w').write(s); print('ok')
