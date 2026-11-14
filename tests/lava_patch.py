p='/home/claude/blockcraft_prototype.html'
s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a[:60],s.count(a)); s=s.replace(a,b)

# ---- A. ids, arrays
rep("const waterQ = new Map();      // cells to re-check: \"x,y,z\" -> [x,y,z]",
"""const waterQ = new Map();      // cells to re-check: "x,y,z" -> [x,y,z]
// lava: 47 is a source, 48..50 are flowing lava (strength 1..3). Overworld lava only creeps 3 blocks from a source, slowly.
const LAVA = 47, OBSIDIAN = 56;
const WOOD_BUCKET = 52, WATER_BUCKET = 53, STONE_BUCKET = 54, LAVA_BUCKET = 55;    // wood buckets carry water, stone buckets carry lava
const IS_LAVA = new Uint8Array(256), LAVA_LEVEL = new Uint8Array(256);
IS_LAVA[LAVA] = 1; LAVA_LEVEL[LAVA] = 4; PASS[LAVA] = 1; NAMES[LAVA] = 'lava';
for(let l=1; l<=3; l++){ IS_LAVA[LAVA+l] = 1; LAVA_LEVEL[LAVA+l] = l; PASS[LAVA+l] = 1; NAMES[LAVA+l] = 'flowing lava'; }
for(let i=LAVA; i<=LAVA+3; i++) COLORS[i] = [226,96,22];
COLORS[OBSIDIAN] = [30,22,46]; NAMES[OBSIDIAN] = 'obsidian';
NAMES[WOOD_BUCKET] = 'wood bucket'; NAMES[WATER_BUCKET] = 'water bucket'; NAMES[STONE_BUCKET] = 'stone bucket'; NAMES[LAVA_BUCKET] = 'lava bucket';
const LAVA_Y = 7;               // empty cave space at or below this height fills with lava lakes""")

# ---- B. lavaHas helper next to waterHas
rep("function waterHas(x,y,z,py){","""function lavaHas(x,y,z,py){
  const b = getB(x,y,z);
  if(!IS_LAVA[b]) return false;
  const l = LAVA_LEVEL[b];
  if(l>=4 || IS_LAVA[getB(x,y+1,z)]) return true;
  return py < y + l/4;
}
function waterHas(x,y,z,py){""")

# ---- C. cast: lava hits as (partial-height) blocks
rep("""    if(inW){ W.len+=t-tIn; inW=false; }
    if(b!==AIR){
      if(out){""","""    if(inW){ W.len+=t-tIn; inW=false; }
    if(IS_LAVA[b]){
      const lv = LAVA_LEVEL[b];
      let ht = t, hf = face, top = false;
      if(lv<4 && !IS_LAVA[getB(x,y+1,z)]){                           // low flowing lava only fills the bottom part of its cell
        const hTop = y + lv/4, tOut = Math.min(tmx,tmy,tmz);
        if(oy+dy*t > hTop){
          if(dy<0){ const tp=(hTop-oy)/dy; if(tp<tOut){ ht=tp; hf=1; top=true; } else continue; } else continue;
        }
      }
      if(out){ out.x=x; out.y=y; out.z=z; out.b=b; out.t=ht; out.face=hf; out.nx=hf===0?-sx:0; out.ny=hf===1?(top?1:-sy):0; out.nz=hf===2?-sz:0; return out; }
      return { x,y,z,b,t:ht,face:hf, nx: hf===0?-sx:0, ny: hf===1?(top?1:-sy):0, nz: hf===2?-sz:0 };
    }
    if(b!==AIR){
      if(out){""")

# ---- D. computeDerived: lava gives light
rep("for(let i=0;i<d.length;i++) if(d[i]===GLOW){ L[i]=15; q.push(i); }","for(let i=0;i<d.length;i++) if(d[i]===GLOW || IS_LAVA[d[i]]){ L[i]=15; q.push(i); }")

# ---- E. worldgen lava lakes in deep caves
rep("  if(y>=2 && isCave(x,y,z)) return (h<SEA && y<=SEA) ? WATER : AIR;     // caves under the sea are flooded",
    "  if(y>=2 && isCave(x,y,z)) return y<=LAVA_Y ? LAVA : (h<SEA && y<=SEA) ? WATER : AIR;     // deep caves hold lava; caves under the sea are flooded")

# ---- F. textures: lava and obsidian tiles
rep("  // LEAVES (non-hole texels)","""  // LAVA: dark crust over bright orange, wraps vertically so it can scroll
  { const r=R(30); TILES.lava=clumpFill(r,[[130,34,10],[188,62,12],[232,104,18],[255,170,44]],4,8,0.45); }
  // OBSIDIAN: near-black glass with purple sheen and pale flecks
  { const r=R(31), t=clumpFill(r,[[20,14,32],[30,22,46],[42,30,64],[26,18,40]],4,8,0.4); scatter(t,r,6,1,1,[96,80,140]); scatter(t,r,3,2,1,[58,44,90]); TILES.obsidian=t; }
  // LEAVES (non-hole texels)""")
rep("    case GLOW: return TILES.glow[yy][tx];","    case GLOW: return TILES.glow[yy][tx];\n    case LAVA: case LAVA+1: case LAVA+2: case LAVA+3: return TILES.lava[yy][tx];\n    case OBSIDIAN: return TILES.obsidian[yy][tx];")

# ---- G. render: lava is lit by itself and its texture scrolls
rep("        let c = texColor(hit.b, hit.face, hit.ny, tx, ty, (hit.b===GRASS || hit.b===LEAVES) ? biomeCol(hit.x,hit.z) : 0);",
    "        let c = texColor(hit.b, hit.face, hit.ny, tx, IS_LAVA[hit.b] ? (ty+lavaFrame)&15 : ty, (hit.b===GRASS || hit.b===LEAVES) ? biomeCol(hit.x,hit.z) : 0);")
rep("        R = c[0]*Math.max(lr,floorL); G = c[1]*Math.max(lg,floorL); B = c[2]*Math.max(lb,floorL);",
    "        R = c[0]*Math.max(lr,floorL); G = c[1]*Math.max(lg,floorL); B = c[2]*Math.max(lb,floorL);\n        if(IS_LAVA[hit.b]){ R=c[0]; G=c[1]; B=c[2]; }                              // lava glows on its own")
rep("let waterFrame = 0;","let waterFrame = 0, lavaFrame = 0;")
rep("  waterFrame = Math.floor(performance.now()/700);","  waterFrame = Math.floor(performance.now()/700);\n  lavaFrame = Math.floor(performance.now()/500)&15;")

# ---- H. targeting looks through lava; placing replaces lava
rep("""function target(){
  const {f} = camVectors();
  return cast(player.x, player.y+1.6, player.z, f[0],f[1],f[2], REACH);
}""","""function target(){
  const {f} = camVectors();
  const ox=player.x, oy=player.y+1.6, oz=player.z;
  let h = cast(ox,oy,oz, f[0],f[1],f[2], REACH), off = 0;
  for(let k=0; h && IS_LAVA[h.b] && k<4; k++){                     // you can't hit lava itself: aim through it
    off = h.t + 0.002;
    const nh = cast(ox+f[0]*off, oy+f[1]*off, oz+f[2]*off, f[0],f[1],f[2], REACH-off);
    if(nh) nh.t += off;
    h = nh;
  }
  return h;
}""")
rep("{ const here = getB(x,y,z); if(here!==AIR && !IS_WATER[here]) return; }   // water can be built over, like in Minecraft","{ const here = getB(x,y,z); if(here!==AIR && !IS_WATER[here] && !IS_LAVA[here]) return; }   // water and lava can be built over, like in Minecraft")
rep("if(!hit || hit.b===BEDROCK){ crack = null; return; }","if(!hit || hit.b===BEDROCK || hit.b===OBSIDIAN){ crack = null; return; }")

# ---- I. fluids: lava flow, reactions, infinite water (inserted before 'let sapTimer')
fl = r'''
// ---------- lava ----------
// Source lava never runs out and never grows. Flowing lava runs 3 blocks from a source, one block every 1.5 seconds, and falls first.
const lavaQ = new Map();
function lavaPoke(x,y,z){
  lavaQ.set(x+','+y+','+z,[x,y,z]);
  for(const [a,b,c] of WDIRS){ const yy=y+b; if(yy>=1 && yy<H) lavaQ.set((x+a)+','+yy+','+(z+c),[x+a,yy,z+c]); }
}
function lavaLevelFor(x,y,z){
  if(IS_LAVA[getB(x,y+1,z)]) return 3;                       // lava above: it falls in at full flowing strength
  let best = 0;
  for(const [dx,dz] of H4){
    const n = getB(x+dx,y,z+dz);
    if(!IS_LAVA[n]) continue;
    if(n===LAVA) return 3;                                     // next to a source
    const l = LAVA_LEVEL[n];
    if(l<=1) continue;
    const bn = getB(x+dx,y-1,z+dz);
    if(bn===AIR || LAVA_LEVEL[bn]<4 && IS_LAVA[bn]) continue;  // lava with a drop under it falls instead of spreading
    if(l-1>best) best = l-1;
  }
  return best;
}
// write one cell straight into its chunk (the same way flowing water does), remember it for saving, and wake the neighbours
function writeCell(x,y,z,id){
  const cx=Math.floor(x/CS), cz=Math.floor(z/CS), c=getChunk(cx,cz);
  const idx=(y*CS+(z-cz*CS))*CS+(x-cx*CS);
  c.data[idx]=id;
  const k=chunkKey(cx,cz);
  let ed=chunkEdits.get(k); if(!ed){ ed=new Map(); chunkEdits.set(k,ed); }
  ed.set(idx,id);
  const [rx,rz]=regionOf(cx,cz); dirtyRegions.add(rx+','+rz);
  computeDerived(c);
  waterPoke(x,y,z); lavaPoke(x,y,z);
}
// A lava cell next to water (on a side or above) cools: a source becomes obsidian, flowing lava becomes cobblestone.
// Lava that falls onto water turns that water into stone.
function lavaReact(x,y,z){
  const b = getB(x,y,z);
  if(!IS_LAVA[b]) return;
  for(const [a,bb,c] of [[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[0,1,0]]){
    if(IS_WATER[getB(x+a,y+bb,z+c)]){ writeCell(x,y,z, b===LAVA ? OBSIDIAN : COBBLE); return; }
  }
  if(y>0 && IS_WATER[getB(x,y-1,z)]) writeCell(x,y-1,z,STONE);
}
// water has just appeared at (x,y,z): any lava touching it reacts
function waterReact(x,y,z){
  for(const [a,b,c] of WDIRS){ if(IS_LAVA[getB(x+a,y+b,z+c)]) lavaReact(x+a,y+b,z+c); }
}
let lavaTimer = 0;
function updateLava(){
  lavaTimer += frameScale/60;
  if(lavaTimer < 1.5) return;                                 // one flow step every 1.5 seconds, much slower than water
  lavaTimer = 0;
  if(!lavaQ.size) return;
  const batch = []; let n = 0;
  for(const [k,p] of lavaQ){ batch.push(p); lavaQ.delete(k); if(++n>=300) break; }
  for(const [x,y,z] of batch){
    const b = getB(x,y,z);
    if(IS_LAVA[b]) lavaReact(x,y,z);
    const b2 = getB(x,y,z);
    if(b2!==AIR && !(IS_LAVA[b2] && b2!==LAVA)) continue;     // only empty cells and flowing lava change
    const L = lavaLevelFor(x,y,z), want = L ? LAVA+L : AIR;
    if(want===b2) continue;
    writeCell(x,y,z,want);
    lavaReact(x,y,z);
  }
  scheduleSave();
}
'''
rep("let sapTimer = 0;", fl+"let sapTimer = 0;")

# water: infinite sources + react with lava
rep("""    const L = waterLevelFor(x,y,z), want = L ? 39+L : AIR;
    if(want===b) continue;""","""    let L = waterLevelFor(x,y,z), want = L ? 39+L : AIR;
    { let srcN = 0; for(const [dx,dz] of H4) if(getB(x+dx,y,z+dz)===WATER) srcN++;                    // two sources side by side make a new source
      if(srcN>=2){ const bb = getB(x,y-1,z); if(!PASS[bb] || bb===WATER) want = WATER; } }
    if(want===b) continue;""")
rep("""    touched.add(c);
    waterPoke(x,y,z);
  }
  for(const c of touched) computeDerived(c);""","""    touched.add(c);
    waterPoke(x,y,z); lavaPoke(x,y,z);
    waterReact(x,y,z);
  }
  for(const c of touched) computeDerived(c);""")

# setB hooks
rep("  waterPoke(x,y,z);                       // water next to a changed block may need to flow or drain\n}","  waterPoke(x,y,z);                       // water next to a changed block may need to flow or drain\n  lavaPoke(x,y,z);\n  if(IS_WATER[b]) waterReact(x,y,z);\n  else if(IS_LAVA[b]) lavaReact(x,y,z);\n}")
rep("waterQ.clear(); mobs.length = 0;","waterQ.clear(); lavaQ.clear(); mobs.length = 0;")
rep("  updateWater();\n  updateMobs();","  updateWater();\n  updateLava();\n  updateMobs();")

# rats avoid lava
rep("  if(!PASS[b] || IS_WATER[b]) return false;\n  const f = ratGet(x,y-1,z);","  if(!PASS[b] || IS_WATER[b] || IS_LAVA[b]) return false;\n  const f = ratGet(x,y-1,z);")
open(p,'w').write(s)
