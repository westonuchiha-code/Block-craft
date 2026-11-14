p='/home/claude/blockcraft_prototype.html'
s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a[:60],s.count(a)); s=s.replace(a,b)

# player in lava
rep("  headUnder   = waterHas(Math.floor(player.x), Math.floor(player.y+1.6), Math.floor(player.z), player.y+1.6);\n  if(bodyInWater){",
"""  headUnder   = waterHas(Math.floor(player.x), Math.floor(player.y+1.6), Math.floor(player.z), player.y+1.6);
  const inLava = lavaHas(Math.floor(player.x), Math.floor(player.y+0.1), Math.floor(player.z), player.y+0.1) ||
                 lavaHas(Math.floor(player.x), Math.floor(player.y+0.9), Math.floor(player.z), player.y+0.9);
  if(inLava){ lavaT -= frameScale/60; if(lavaT<=0){ hurt(2); lavaT = 0.5; } } else lavaT = 0;      // 2 hearts a second while you are in lava
  if(bodyInWater || inLava){""")
rep("    mx*=0.6; mz*=0.6;\n    // flowing water carries","    mx*=0.6; mz*=0.6;\n    if(inLava){ mx*=0.55; mz*=0.55; }                                  // lava is thick: you wade through it slowly\n    // flowing water carries")
rep("let air = AIR_MAX, drownT = 0,","let lavaT = 0;\nlet air = AIR_MAX, drownT = 0,")

# buckets: use
rep("  if(dead) return;\n  swingT = 1;\n  const hit = target();\n  if(!hit) return;\n  if(hit.b === CRAFT_TABLE)","  if(dead) return;\n  swingT = 1;\n  { const hb = HOTBAR[sel]; if(hb>=WOOD_BUCKET && hb<=LAVA_BUCKET && inv[hb]>0){ bucketUse(hb); return; } }\n  const hit = target();\n  if(!hit) return;\n  if(hit.b === CRAFT_TABLE)")
rep("function placeBlock(){","""// A bucket scoops up a SOURCE block of its fluid (wood: water, stone: lava) or pours its fluid out as a new source where you aim.
function bucketUse(id){
  const {f} = camVectors(), ox=player.x, oy=player.y+1.6, oz=player.z;
  const full = id===WATER_BUCKET || id===LAVA_BUCKET;
  const swapTo = nid => {                                      // the bucket changes into its filled / empty form
    inv[id]--; if(inv[id]<=0) delete inv[id];
    inv[nid] = Math.min(99, (inv[nid]||0)+1);
    if(HOTBAR[sel]===id && !inv[id]) HOTBAR[sel] = nid;
    scheduleSave();
  };
  let prev = null;
  for(let t=0.1; t<=REACH; t+=0.05){
    const x=Math.floor(ox+f[0]*t), y=Math.floor(oy+f[1]*t), z=Math.floor(oz+f[2]*t);
    if(prev && prev[0]===x && prev[1]===y && prev[2]===z) continue;
    const b = getB(x,y,z);
    if(!full){
      if(b===(id===WOOD_BUCKET ? WATER : LAVA)){ setB(x,y,z,AIR); swapTo(id===WOOD_BUCKET ? WATER_BUCKET : LAVA_BUCKET); return; }
      if(!PASS[b]) return;
    } else {
      if(!PASS[b]){                                            // a solid block: pour into the cell in front of it
        if(!prev) return;
        const pb = getB(prev[0],prev[1],prev[2]);
        if(pb!==AIR && !(IS_WATER[pb] && pb!==WATER) && !(IS_LAVA[pb] && pb!==LAVA)) return;
        setB(prev[0],prev[1],prev[2], id===WATER_BUCKET ? WATER : LAVA);
        swapTo(id===WATER_BUCKET ? WOOD_BUCKET : STONE_BUCKET);
        return;
      }
    }
    prev = [x,y,z];
  }
}
function placeBlock(){""")

# bucket icons and held
rep("  if(id===STICK){                                                       // a hand-drawn diagonal stick, no smoothing",
"""  if(id>=WOOD_BUCKET && id<=LAVA_BUCKET){                               // buckets: wood carries water, stone carries lava
    const stone = id===STONE_BUCKET || id===LAVA_BUCKET;
    const body = stone ? [128,130,138] : [156,116,68], dark = stone ? [88,90,98] : [108,78,46], light = stone ? [176,178,186] : [196,156,100];
    const fluid = id===WATER_BUCKET ? [60,110,214] : id===LAVA_BUCKET ? [240,110,24] : null;
    const put = (x,y,c)=>{ g.fillStyle=`rgb(${c[0]|0},${c[1]|0},${c[2]|0})`; g.fillRect(x,y,1,1); };
    for(const [x,y] of [[4,3],[5,2],[6,1],[7,1],[8,1],[9,1],[10,2],[11,3]]) put(x,y,[84,84,92]);        // the handle
    for(let x=3;x<=12;x++) put(x,4,light);                                                               // the rim
    if(fluid) for(let x=4;x<=11;x++){ put(x,4,fluid); }
    for(let y=5;y<=13;y++){
      const x0 = y>9 ? 4 : 3, x1 = y>9 ? 11 : 12;
      for(let x=x0;x<=x1;x++) put(x,y, x===x0 ? light : x===x1 ? dark : (y%4===1 ? dark : body));       // staves and hoops
    }
    for(let x=4;x<=11;x++) put(x,14,dark);
    if(fluid){ put(5,4,[255,255,255]); }
    return;
  }
  if(id===STICK){                                                       // a hand-drawn diagonal stick, no smoothing""")
rep("  if(count>0 && (id===STICK || IS_SAP[id])){","  if(count>0 && (id===STICK || IS_SAP[id] || (id>=WOOD_BUCKET && id<=LAVA_BUCKET))){")

# crafting
rep("  { name:'Stone sword',        out:[STONE_SWORD,1],  ing:{[COBBLE]:2, [STICK]:1} }\n];","  { name:'Stone sword',        out:[STONE_SWORD,1],  ing:{[COBBLE]:2, [STICK]:1} },\n  { name:'Wood bucket (carries water)',  out:[WOOD_BUCKET,1],  ing:{[PLANKS]:3} },\n  { name:'Stone bucket (carries lava)',  out:[STONE_BUCKET,1], ing:{[COBBLE]:3} }\n];")
rep("  { out:[STONE_SWORD,1],  pat:['C','C','S'],           key:{C:COBBLE, S:STICK} }\n];","  { out:[STONE_SWORD,1],  pat:['C','C','S'],           key:{C:COBBLE, S:STICK} },\n  { out:[WOOD_BUCKET,1],  pat:['P P',' P '],           key:{P:PLANKS} },\n  { out:[STONE_BUCKET,1], pat:['C C',' C '],           key:{C:COBBLE} }\n];")
rep("(craftTab===1) === (r.out[0] >= WOOD_PICK && r.out[0] <= STONE_SWORD)","(craftTab===1) === ((r.out[0] >= WOOD_PICK && r.out[0] <= STONE_SWORD) || (r.out[0] >= WOOD_BUCKET && r.out[0] <= LAVA_BUCKET))")
open(p,'w').write(s)
