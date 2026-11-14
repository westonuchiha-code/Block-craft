import re
p='/home/claude/blockcraft_prototype.html'
s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)>=1, a[:60]
    if cnt==1: assert s.count(a)==1, ('multi',a[:60],s.count(a))
    s=s.replace(a,b)

# 1. ids / names / colors / helper arrays
rep("COLORS[26] = [238,244,250]; // snow\n", """COLORS[26] = [238,244,250]; // snow
// ---------- woods: maple, oak, birch, spruce. Each has its own log, planks, leaves and sapling ----------
const LOG_IDS = [7,27,28,29], PLANK_IDS = [8,30,31,32], LEAF_IDS = [9,33,34,35], SAP_IDS = [36,37,38,39];
const WOOD_NAMES = ['maple','oak','birch','spruce'];
const IS_LOG = new Uint8Array(256), IS_PLANK = new Uint8Array(256), IS_LEAF = new Uint8Array(256), IS_SAP = new Uint8Array(256);
const SP_OF = new Uint8Array(256);        // which wood (0..3) a log / planks / leaves / sapling id belongs to
const PASS = new Uint8Array(256);         // blocks you can walk through
const SEETHRU = new Uint8Array(256);      // blocks whose texture has see-through gaps (leaves, saplings)
PASS[AIR] = 1; PASS[WATER] = 1;
for(let w=0; w<4; w++){
  IS_LOG[LOG_IDS[w]] = IS_PLANK[PLANK_IDS[w]] = IS_LEAF[LEAF_IDS[w]] = IS_SAP[SAP_IDS[w]] = 1;
  SP_OF[LOG_IDS[w]] = SP_OF[PLANK_IDS[w]] = SP_OF[LEAF_IDS[w]] = SP_OF[SAP_IDS[w]] = w;
  SEETHRU[LEAF_IDS[w]] = SEETHRU[SAP_IDS[w]] = 1;
  PASS[SAP_IDS[w]] = 1;
  NAMES[LOG_IDS[w]] = WOOD_NAMES[w] + ' log';
  NAMES[PLANK_IDS[w]] = WOOD_NAMES[w] + ' planks';
  NAMES[LEAF_IDS[w]] = WOOD_NAMES[w] + ' leaves';
  NAMES[SAP_IDS[w]] = WOOD_NAMES[w] + ' sapling';
}
COLORS[27]=[92,68,44]; COLORS[28]=[226,224,214]; COLORS[29]=[62,44,30];        // oak, birch, spruce logs
COLORS[30]=[174,134,82]; COLORS[31]=[214,198,142]; COLORS[32]=[110,80,48];     // their planks
COLORS[33]=[56,104,38]; COLORS[34]=[118,156,66]; COLORS[35]=[34,76,52];        // their leaves (maple leaves take the biome color)
const SAP_CHANCE = 0.05;                  // chance a leaf drops a sapling when broken or when it decays
const saplings = new Map();               // "x,y,z" -> { x, y, z, t }: planted saplings waiting to grow (t = seconds left)
""")
rep("DROP[LEAVES]=0;\n","DROP[LEAVES]=0; for(const id of LEAF_IDS) DROP[id]=0;\n")

# 2. trees
i0=s.index("// tree that covers (x,y,z), if any.")
i1=s.index("function blockAt(x,y,z){")
trees = r'''// ---------- trees ----------
// three growth shapes: ROUND (one trunk, a round canopy), CONIFER (tall cone) and GREAT (thick 2 x 2 trunk, wide canopy, big side branches)
const SH_ROUND=0, SH_CONIFER=1, SH_GREAT=2;
// what each biome grows: [wood, shape, weight]
const TREE_TABLE = [
  [[0,SH_ROUND,55],[2,SH_ROUND,30],[1,SH_GREAT,15]],      // Autumn Woods: maple, birch, great oak
  [[1,SH_ROUND,50],[2,SH_ROUND,30],[3,SH_CONIFER,20]],    // Green Forest: oak, birch, spruce
  [[3,SH_CONIFER,65],[2,SH_ROUND,20],[1,SH_GREAT,15]]     // Pine Highlands: spruce, birch, great oak
];
// a column that might hold a tree: returns its hash value (low wins), or -1
function isCand(x,z){ const hv = h3(x,0,z,SEED+99); return (hv<0.055 && hv<treeChance(x,z)) ? hv : -1; }
const treeCache = new Map();
// the tree rooted at this column, or null. Trees keep a gap from each other, and only grow on grass.
function rootTree(rx,rz){
  const key = chunkKey(rx,rz);
  let t = treeCache.get(key);
  if(t!==undefined) return t;
  t = null;
  const hv = isCand(rx,rz);
  if(hv>=0){
    let ok = true;
    for(let dx=-2; dx<=2 && ok; dx++) for(let dz=-2; dz<=2; dz++){
      if(!dx && !dz) continue;
      const o = isCand(rx+dx,rz+dz);
      if(o>=0 && o<hv){ ok = false; break; }
    }
    const ci = ok ? colInfo(rx,rz) : null;
    if(ci && ci.top===GRASS && !ci.open && ci.h>SEA+1 && ci.h+24<H){
      const tbl = TREE_TABLE[ci.bio];
      let tot = 0; for(const e of tbl) tot += e[2];
      let pick = h3(rx,1,rz,SEED+98)*tot, e = tbl[0];
      for(const q of tbl){ if(pick<q[2]){ e = q; break; } pick -= q[2]; }
      const sp = e[0]; let shape = e[1], base = ci.h+1;
      if(shape===SH_GREAT){                              // a 2 x 2 trunk needs flat grass under all four blocks
        let flat = true;
        for(const [ox,oz] of [[1,0],[0,1],[1,1]]){
          const c2 = colInfo(rx+ox,rz+oz);
          if(c2.top!==GRASS || c2.open || c2.h<=SEA+1 || Math.abs(c2.h-ci.h)>1) flat = false;
          else base = Math.max(base, c2.h+1);
        }
        if(!flat){ shape = sp===3 ? SH_CONIFER : SH_ROUND; base = ci.h+1; }
      }
      t = { x:rx, z:rz, y:base, sp, shape };
    }
  }
  if(treeCache.size > 40000) treeCache.clear();
  treeCache.set(key,t);
  return t;
}
// leaves in a flat disc of radius R around a center (cell-center coordinates), with a ragged edge
function leafDisc(out,ccx,cy,ccz,R,k){
  for(let X=Math.floor(ccx-R-1); X<=Math.ceil(ccx+R); X++) for(let Z=Math.floor(ccz-R-1); Z<=Math.ceil(ccz+R); Z++){
    const d2 = (X+0.5-ccx)*(X+0.5-ccx) + (Z+0.5-ccz)*(Z+0.5-ccz);
    if(d2>R*R) continue;
    if(R>1.4 && d2>(R-1)*(R-1) && h3(X,cy*5+k,Z,SEED+78)<0.25) continue;
    out.push([X,cy,Z]);
  }
}
// the blocks of a tree whose trunk starts at (x,y,z). For GREAT, (x,z) is the corner of its 2 x 2 trunk.
function buildTree(sp,shape,x,y,z){
  const logs=[], leaves=[];
  const rr = i => h3(x,y*7+i,z,SEED+77);
  if(shape===SH_ROUND){
    const big = sp===0, tall = sp===2;                           // maple: wide and round; birch: tall and slim
    const n = (tall?5:4) + Math.floor(rr(0)*3) + (big?1:0);
    for(let i=0;i<n;i++) logs.push([x,y+i,z]);
    const L = y+n-1;
    const layers = big ? [[-2,2.3],[-1,3.1],[0,3.1],[1,2.3],[2,1.4]]
                 : tall ? [[-2,1.6],[-1,2.2],[0,2.2],[1,1.6],[2,1.0]]
                 : [[-1,2.4],[0,2.4],[1,1.7],[2,1.0]];
    layers.forEach(([dy,R],k)=>leafDisc(leaves,x+0.5,L+dy,z+0.5,R,k));
  } else if(shape===SH_CONIFER){
    const n = 7 + Math.floor(rr(0)*4);
    for(let i=0;i<n;i++) logs.push([x,y+i,z]);
    const L = y+n-1, seq = [0.6,1.5,2.4,1.5,2.4,3.2,2.4,3.2,2.4,3.2];
    for(let k=0;k<n;k++) leafDisc(leaves,x+0.5,L+2-k,z+0.5,seq[Math.min(k,seq.length-1)],k);
  } else {
    const n = 9 + Math.floor(rr(0)*5);
    for(let dx=0;dx<2;dx++) for(let dz=0;dz<2;dz++) for(let i=-1;i<n;i++) logs.push([x+dx,y+i,z+dz]);
    const L = y+n-1;
    [[-4,2.5],[-3,4.0],[-2,4.8],[-1,5.0],[0,4.6],[1,3.6],[2,2.2],[3,1.2]].forEach(([dy,R],k)=>leafDisc(leaves,x+1,L+dy,z+1,R,k));
    // big branches jutting out from the upper trunk, each ending in a puff of leaves
    const DIRS = [[1,0],[0,1],[-1,0],[0,-1]];
    const nb = 3 + (rr(1)>0.5 ? 1 : 0), d0 = Math.floor(rr(30)*4);
    for(let b=0;b<nb;b++){
      const [ddx,ddz] = DIRS[(b+d0)%4], side = rr(40+b)>0.5 ? 1 : 0;
      let bx = ddx>0 ? x+2 : ddx<0 ? x-1 : x+side;
      let bz = ddz>0 ? z+2 : ddz<0 ? z-1 : z+side;
      const by = y + Math.floor(n*0.45) + Math.floor(rr(10+b)*n*0.3), len = 2 + Math.floor(rr(20+b)*3);
      let ex=bx, ey=by, ez=bz;
      for(let i=0;i<len;i++){ ex=bx+ddx*i; ez=bz+ddz*i; ey=by+Math.floor(i/2); logs.push([ex,ey,ez]); }
      leafDisc(leaves,ex+0.5,ey-1,ez+0.5,2.0,0); leafDisc(leaves,ex+0.5,ey,ez+0.5,2.4,1); leafDisc(leaves,ex+0.5,ey+1,ez+0.5,1.6,2);
    }
  }
  return { logs, leaves };
}
// put every tree that reaches this chunk into its block data (leaves only fill empty space; logs also replace leaves)
function treesForChunk(data,cx,cz){
  const x0=cx*CS, z0=cz*CS, M=9;
  const placed=[];
  for(let rx=x0-M; rx<x0+CS+M; rx++) for(let rz=z0-M; rz<z0+CS+M; rz++){
    if(h3(rx,0,rz,SEED+99)>=0.055) continue;
    const t = rootTree(rx,rz);
    if(!t) continue;
    const b = buildTree(t.sp,t.shape,t.x,t.y,t.z);
    const lid = LEAF_IDS[t.sp];
    for(const [X,Y,Z] of b.leaves){
      if(X<x0||X>=x0+CS||Z<z0||Z>=z0+CS||Y<1||Y>=H) continue;
      const idx=(Y*CS+(Z-z0))*CS+(X-x0);
      if(data[idx]===AIR) data[idx]=lid;
    }
    placed.push([b.logs, LOG_IDS[t.sp]]);
  }
  for(const [logs,gid] of placed) for(const [X,Y,Z] of logs){
    if(X<x0||X>=x0+CS||Z<z0||Z>=z0+CS||Y<1||Y>=H) continue;
    const idx=(Y*CS+(Z-z0))*CS+(X-x0);
    if(data[idx]===AIR || IS_LEAF[data[idx]]) data[idx]=gid;
  }
}
// is there a tree candidate within r blocks of this column? (used to keep the spawn point clear of trees)
function treeNear(x,z,r){
  for(let dx=-r; dx<=r; dx++) for(let dz=-r; dz<=r; dz++) if(isCand(x+dx,z+dz)>=0) return true;
  return false;
}

'''
s = s[:i0] + trees + s[i1:]
rep("    const t = treeBlock(x,y,z); return t===-1 ? AIR : t;\n","    return AIR;\n")
rep("  const ed = chunkEdits.get(chunkKey(cx,cz));\n  if(ed) for(const [idx,b] of ed) data[idx]=b;\n",
    "  treesForChunk(data,cx,cz);\n  const ed = chunkEdits.get(chunkKey(cx,cz));\n  if(ed) for(const [idx,b] of ed) data[idx]=b;\n  for(let i=0;i<data.length;i++) if(IS_SAP[data[i]]){          // planted saplings in a freshly loaded chunk start growing again\n    const lx=i%CS, lz=Math.floor(i/CS)%CS, y=Math.floor(i/(CS*CS)), x=cx*CS+lx, z=cz*CS+lz, k=x+','+y+','+z;\n    if(!saplings.has(k)) saplings.set(k,{x,y,z,t:60+Math.random()*120});\n  }\n")
rep("      if(treeBlock(x,ci.h+1,z)!==-1 || treeBlock(x,ci.h+2,z)!==-1 || treeBlock(x,ci.h+4,z)!==-1) continue;\n","      if(treeNear(x,z,6)) continue;\n")
rep("  surfaceCache.clear(); colCache.clear();","  surfaceCache.clear(); colCache.clear(); treeCache.clear(); saplings.clear();")
# roof
rep("if(b!==AIR && b!==LEAVES && b!==WATER){ t=y+1; break; } }   // leaves and water don't count as a roof",
    "if(b!==AIR && !IS_LEAF[b] && !IS_SAP[b] && b!==WATER){ t=y+1; break; } }   // leaves, saplings and water don't count as a roof")
rep("    if(b!==AIR && b!==WATER){ player.y = y+1; return; }","    if(!PASS[b]){ player.y = y+1; return; }")
rep("    if(b!==AIR && b!==WATER) return true;\n  }\n  return false;","    if(!PASS[b]) return true;\n  }\n  return false;")
rep("if(e.vy<0 && bb!==AIR && bb!==WATER){","if(e.vy<0 && !PASS[bb]){")

# 3. textures
rep("    case LOG: {\n      if(top){","    case 27: case 28: case 29: return extraLogTex(b,top,tx,ty,r);\n    case LOG: {\n      if(top){")
rep("    case PLANKS: {\n      // same pale color as the inside of the log","    case PLANKS: case 30: case 31: case 32: {\n      // same pale color as the inside of the log")
rep("    case LEAVES:\n      if(r>0.75) return [40,25,10];                                          // gaps in the canopy\n      return",
    "    case LEAVES: case 33: case 34: case 35:\n      if(r>0.75) return [40,25,10];                                          // gaps in the canopy\n      if(LEAF_PAL[b]) return scaleC(LEAF_PAL[b][r>0.45?1:0], 0.9+0.2*r);\n      return")
rep("    case CRAFT_TABLE: {\n      const edgeT","    case 36: case 37: case 38: case 39: return sapPix(b,tx,ty) || [255,0,255];\n    case CRAFT_TABLE: {\n      const edgeT")
rep("function scaleC(c,s){ return [c[0]*s, c[1]*s, c[2]*s]; }\n", r'''function scaleC(c,s){ return [c[0]*s, c[1]*s, c[2]*s]; }
const LEAF_PAL = { 33:[[56,108,38],[46,92,32]], 34:[[122,160,64],[104,142,54]], 35:[[34,78,54],[26,62,42]] };   // oak, birch, spruce leaves
// oak, birch and spruce bark and cut ends
function extraLogTex(b,top,tx,ty,r){
  if(b===27){                                                    // oak: dark brown, deep furrows
    if(top){ const d=Math.hypot(tx-7.5,ty-7.5); return d<2.2 ? [138,98,58] : Math.floor(d)%2 ? [152,114,70] : [172,134,86]; }
    if(h3(tx,ty>>1,3,SEED+25)>0.94) return [34,24,16];
    return h3(tx,0,0,SEED+24)<0.4 ? scaleC([50,36,24],0.85+0.3*r) : scaleC([96,72,46],0.9+0.2*r);
  }
  if(b===28){                                                    // birch: white bark with dark horizontal marks
    if(top){ const d=Math.hypot(tx-7.5,ty-7.5); return d<2.2 ? [168,140,92] : Math.floor(d)%2 ? [200,176,120] : [214,194,140]; }
    const mark = h3(tx>>1, ty, 9, SEED+26) > 0.86;
    if(mark) return [42,40,38];
    return scaleC([226,224,214], 0.9+0.12*r);
  }
  if(top){ const d=Math.hypot(tx-7.5,ty-7.5); return d<2.2 ? [92,64,38] : Math.floor(d)%2 ? [112,80,50] : [128,94,60]; }   // spruce
  if(h3(tx,ty>>1,3,SEED+25)>0.95) return [30,20,12];
  return h3(tx,0,0,SEED+24)<0.45 ? scaleC([44,30,20],0.85+0.3*r) : scaleC([76,54,36],0.9+0.2*r);
}
// saplings: a 16 x 16 sprite drawn on every side of the block, with empty gaps. '.' is empty, L leaf, D dark leaf, T stem
const SAP_ROUND = ['................','................','......LL........','.....LLLL.LL....','....LLLLLLLLL...','...LLLLDLLLLLL..','...LLLLLLLLLL...','....LLLLLLLLL...','.....LLLLLLL....','......LLLL......','.......TT.......','.......TT.......','.......TT.......','.......TT.......','.......TT.......','.......TT.......'];
const SAP_CONE  = ['................','.......LL.......','.......LL.......','......LLLL......','......LLLL......','.....LLDLLL.....','.....LLLLLL.....','....LLLLLLLL....','....LLDLLLLL....','...LLLLLLLLLL...','.......TT.......','.......TT.......','.......TT.......','.......TT.......','.......TT.......','.......TT.......'];
const SAP_LEAF = [[205,100,40],[66,122,44],[120,162,66],[34,84,54]];
function sapPix(b,tx,ty){
  const w = SP_OF[b], ch = (w===3 ? SAP_CONE : SAP_ROUND)[15-ty][tx];
  if(ch==='.' || !ch) return null;
  const r = h3(tx,ty,b,SEED+21);
  if(ch==='T') return scaleC(w===2 ? [200,195,180] : [100,76,50], 0.85+0.3*r);
  return scaleC(SAP_LEAF[w], (ch==='D'?0.7:1)*(0.85+0.3*r));
}
''')
rep("function isLeafHole(hit, wx, wy, wz){","function isLeafHole(hit, wx, wy, wz){")
rep("  return h3(tx,ty,LEAVES,SEED+21)>0.75;      // same test the leaf texture uses for its holes",
    "  if(IS_SAP[hit.b]) return hit.face===1 || sapPix(hit.b,tx,ty)===null;   // saplings: only the sprite is solid\n  return h3(tx,ty,hit.b,SEED+21)>0.75;      // same test the leaf texture uses for its holes")
rep("for(let pass=0; hit && hit.b===LEAVES && pass<3; pass++){","for(let pass=0; hit && SEETHRU[hit.b] && pass<3; pass++){")
rep("lit = !sh ? 1 : (sh.b===LEAVES ? 0.45 : 0);","lit = !sh ? 1 : (SEETHRU[sh.b] ? 0.45 : 0);")
rep("(hit.b===GRASS || hit.b===LEAVES) ? biomeCol(hit.x,hit.z) : 0);","(hit.b===GRASS || hit.b===LEAVES) ? biomeCol(hit.x,hit.z) : 0);")

# 4. gameplay tables
rep("const REQ_TIER = { [STONE]:1, [COBBLE]:1, [COAL]:1 };\n","""const REQ_TIER = { [STONE]:1, [COBBLE]:1, [COAL]:1 };
for(let w=0; w<4; w++){
  HARD[LOG_IDS[w]]=2; HARD[PLANK_IDS[w]]=2; HARD[LEAF_IDS[w]]=0.2; HARD[SAP_IDS[w]]=0;
  for(const id of [LOG_IDS[w],PLANK_IDS[w],LEAF_IDS[w],SAP_IDS[w]]) HAND_OK.add(id);
  KIND[LOG_IDS[w]]='axe'; KIND[PLANK_IDS[w]]='axe'; KIND[LEAF_IDS[w]]='sword';
}
""")
# leaf decay
rep("if(getB(cx+dx,cy+dy,cz+dz)!==LOG) continue;","if(!IS_LOG[getB(cx+dx,cy+dy,cz+dz)]) continue;")
rep("          if(getB(cx+nx,cy+ny,cz+nz)!==LEAVES) continue;","          if(!IS_LEAF[getB(cx+nx,cy+ny,cz+nz)]) continue;")
rep("      if(getB(cx+nx,cy+ny,cz+nz)!==LEAVES) continue;","      if(!IS_LEAF[getB(cx+nx,cy+ny,cz+nz)]) continue;")
rep("        if(getB(x,y,z)!==LEAVES){ leafUnsupported.delete(key); continue; }","        if(!IS_LEAF[getB(x,y,z)]){ leafUnsupported.delete(key); continue; }")
rep("    if(getB(e.x,e.y,e.z)!==LEAVES){ leafUnsupported.delete(key); continue; }","    const lb = getB(e.x,e.y,e.z);\n    if(!IS_LEAF[lb]){ leafUnsupported.delete(key); continue; }")
rep("      setB(e.x,e.y,e.z,AIR);\n      leafUnsupported.delete(key);","      setB(e.x,e.y,e.z,AIR);\n      if(Math.random()<SAP_CHANCE) spawnDrop(e.x,e.y,e.z,SAP_IDS[SP_OF[lb]]);   // falling leaves sometimes leave a sapling\n      leafUnsupported.delete(key);")
rep("  if(hit.b===LOG || hit.b===LEAVES) queueLeafScan(hit.x, hit.y, hit.z);\n","""  if(IS_LOG[hit.b] || IS_LEAF[hit.b]) queueLeafScan(hit.x, hit.y, hit.z);
  const above = getB(hit.x,hit.y+1,hit.z);
  if(IS_SAP[above]){                                       // a sapling can't float: it pops off when its ground goes
    setB(hit.x,hit.y+1,hit.z,AIR); saplings.delete(hit.x+','+(hit.y+1)+','+hit.z); spawnDrop(hit.x,hit.y+1,hit.z,above);
  }
  if(IS_SAP[hit.b]) saplings.delete(hit.x+','+hit.y+','+hit.z);
""")
rep("  const drop = (hit.b in DROP) ? DROP[hit.b] : hit.b;\n","  if(IS_LEAF[hit.b] && Math.random()<SAP_CHANCE) spawnDrop(hit.x, hit.y, hit.z, SAP_IDS[SP_OF[hit.b]]);   // leaves sometimes drop a sapling\n  const drop = (hit.b in DROP) ? DROP[hit.b] : hit.b;\n")
# placing
rep("  if(!COLORS[b] || TOOLS[b] || b===STICK) return;","  if(!IS_SAP[b] && (!COLORS[b] || TOOLS[b] || b===STICK)) return;")
rep("  { const here = getB(x,y,z); if(here!==AIR && here!==WATER) return; }   // water can be built over, like in Minecraft\n  // don't place a block inside the player\n  if(player.x+0.3>x",
    "  { const here = getB(x,y,z); if(here!==AIR && here!==WATER) return; }   // water can be built over, like in Minecraft\n  if(IS_SAP[b]){ const below=getB(x,y-1,z); if((below!==GRASS && below!==DIRT) || getB(x,y,z)!==AIR) return; }   // saplings need grass or dirt under them\n  // don't place a block inside the player\n  if(!IS_SAP[b] && player.x+0.3>x")
rep("  if(b===LOG) queueLeafScan(x,y,z);       // a log put back can hold up leaves that were falling","  if(IS_LOG[b]) queueLeafScan(x,y,z);       // a log put back can hold up leaves that were falling\n  if(IS_SAP[b]) saplings.set(x+','+y+','+z,{x,y,z,t:60+Math.random()*120});")
# recipes
rep("  { name:'Maple planks (from maple log)', out:[PLANKS,4], ing:{[LOG]:1} },\n",
    "  ...[0,1,2,3].map(w=>({ name:WOOD_NAMES[w][0].toUpperCase()+WOOD_NAMES[w].slice(1)+' planks (from '+WOOD_NAMES[w]+' log)', out:[PLANK_IDS[w],4], ing:{[LOG_IDS[w]]:1} })),\n")
rep("""function canCraft(r){
  for(const id in r.ing) if((inv[id]||0) < r.ing[id]) return false;
  return true;
}
function craftRecipe(r){
  if(!canCraft(r)) return;
  for(const id in r.ing) inv[id] -= r.ing[id];""","""// a recipe that asks for PLANKS accepts planks of any wood
function planksTotal(){ let n=0; for(const id of PLANK_IDS) n += inv[id]||0; return n; }
function haveOf(id){ return +id===PLANKS ? planksTotal() : (inv[id]||0); }
function takePlanks(n){
  while(n>0){
    let best = PLANK_IDS[0];
    for(const id of PLANK_IDS) if((inv[id]||0) > (inv[best]||0)) best = id;     // use up the biggest stack first
    const k = Math.min(n, inv[best]||0); if(k<=0) return;
    inv[best] -= k; n -= k;
  }
}
function canCraft(r){
  for(const id in r.ing) if(haveOf(id) < r.ing[id]) return false;
  return true;
}
function craftRecipe(r){
  if(!canCraft(r)) return;
  for(const id in r.ing){ if(+id===PLANKS) takePlanks(r.ing[id]); else inv[id] -= r.ing[id]; }""")
rep("      const have = inv[id]||0, want = r.ing[id];","      const have = haveOf(id), want = r.ing[id];")
rep("      slot.title = NAMES[id];\n      slot.appendChild(iconCanvas(+id));","      slot.title = +id===PLANKS ? 'any planks' : NAMES[id];\n      slot.appendChild(iconCanvas(+id));")
rep("      if(filled.length===1 && filled[0]===r.shapeless) return r;","      if(filled.length===1 && IS_LOG[filled[0]]) return { out:[PLANK_IDS[SP_OF[filled[0]]],4] };   // any log makes its own planks")
rep("        else if(r.key[want] !== have) ok = false;","        else if(!(r.key[want]===have || (r.key[want]===PLANKS && IS_PLANK[have]))) ok = false;")
# flat held/icon
rep("  if(count>0 && id===STICK){","  if(count>0 && (id===STICK || IS_SAP[id])){")
rep("function drawToolIcon(g, id){\n","function drawToolIcon(g, id){\n  if(IS_SAP[id]){\n    for(let y=0;y<16;y++) for(let x=0;x<16;x++){ const c=sapPix(id,x,15-y); if(!c) continue; g.fillStyle=`rgb(${c[0]|0},${c[1]|0},${c[2]|0})`; g.fillRect(x,y,1,1); }\n    return;\n  }\n")
rep("SHORT[PLANKS]='m.plank';\nSHORT[LOG]='m.log';","SHORT[PLANKS]='m.plank';\nSHORT[LOG]='m.log';") if False else None
rep("SHORT[STONE_SHOVEL]='s.shvl'; SHORT[STONE_SWORD]='s.sword';","SHORT[STONE_SHOVEL]='s.shvl'; SHORT[STONE_SWORD]='s.sword';\nSHORT[27]='o.log'; SHORT[28]='b.log'; SHORT[29]='s.log'; SHORT[30]='o.plank'; SHORT[31]='b.plank'; SHORT[32]='s.plank';\nfor(const id of LEAF_IDS) SHORT[id]='leaves'; for(const id of SAP_IDS) SHORT[id]='sapl';")
rep("`coal ${inv[COAL_ITEM]||0} | maple planks ${inv[PLANKS]||0} | maple logs ${inv[LOG]||0}`;","`coal ${inv[COAL_ITEM]||0} | planks ${planksTotal()} | logs ${LOG_IDS.reduce((a,id)=>a+(inv[id]||0),0)}`;")
rep("NAMES[24] = 'crafting table';","NAMES[9] = 'maple leaves'; NAMES[24] = 'crafting table';")
# growth
rep("function punch(){","""// ---------- saplings grow into trees (about two minutes on average) when there is room ----------
function stampBlocks(list){
  const touched = new Set();
  for(const [x,y,z,b] of list){
    if(y<1 || y>=H) continue;
    const cx=Math.floor(x/CS), cz=Math.floor(z/CS), c=getChunk(cx,cz);
    const idx=(y*CS+(z-cz*CS))*CS+(x-cx*CS);
    c.data[idx]=b;
    const k=chunkKey(cx,cz);
    let ed=chunkEdits.get(k); if(!ed){ ed=new Map(); chunkEdits.set(k,ed); }
    ed.set(idx,b);
    const [rx,rz]=regionOf(cx,cz); dirtyRegions.add(rx+','+rz);
    touched.add(c);
  }
  for(const c of touched) computeDerived(c);
  scheduleSave();
}
function growSapling(s){
  const key = s.x+','+s.y+','+s.z, id = getB(s.x,s.y,s.z);
  if(!IS_SAP[id]){ saplings.delete(key); return; }
  const soil = (x,z)=>{ const b=getB(x,s.y-1,z); return b===GRASS || b===DIRT; };
  if(!soil(s.x,s.z)){ setB(s.x,s.y,s.z,AIR); spawnDrop(s.x,s.y,s.z,id); saplings.delete(key); return; }
  const w = SP_OF[id];
  let tree=null, foot=[[s.x,s.z]];
  for(const [ox,oz] of [[0,0],[-1,0],[0,-1],[-1,-1]]){          // four of one kind in a 2 x 2 make a great tree
    const bx=s.x+ox, bz=s.z+oz, cells=[[bx,bz],[bx+1,bz],[bx,bz+1],[bx+1,bz+1]];
    if(cells.every(([x,z])=>getB(x,s.y,z)===id && soil(x,z))){ tree=buildTree(w,SH_GREAT,bx,s.y,bz); foot=cells; break; }
  }
  if(!tree) tree = buildTree(w, w===3 ? SH_CONIFER : SH_ROUND, s.x, s.y, s.z);
  const logs = tree.logs.filter(l=>l[1]>=s.y);
  for(const [x,y,z] of logs){
    const b=getB(x,y,z);
    if(y>=H-3 || !(b===AIR || IS_LEAF[b] || IS_SAP[b])){ s.t = 20+Math.random()*20; return; }     // no room yet: try again later
  }
  const list=[];
  for(const [x,y,z] of tree.leaves) if(getB(x,y,z)===AIR) list.push([x,y,z,LEAF_IDS[w]]);
  for(const [x,y,z] of logs) list.push([x,y,z,LOG_IDS[w]]);
  for(const [x,z] of foot) saplings.delete(x+','+s.y+','+z);
  stampBlocks(list);
}
let sapTimer = 0;
function updateSaplings(){
  sapTimer += frameScale/60;
  if(sapTimer < 1) return;
  sapTimer = 0;
  for(const [k,s] of saplings){
    if(!chunks.has(chunkKey(Math.floor(s.x/CS),Math.floor(s.z/CS)))) continue;     // only loaded chunks grow
    s.t -= 1;
    if(s.t<=0) growSapling(s);
  }
}
function punch(){""")
rep("  updateLeaves();","  updateLeaves();\n  updateSaplings();")
open(p,'w').write(s)
