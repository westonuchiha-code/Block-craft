p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    a = a.replace('\\u2014','\u2014')
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# new worlds get roads
rep("name, seed, gen:3, inv:{}, tod:0.15, player:null }));", "name, seed, gen:4, inv:{}, tod:0.15, player:null }));")
rep("let worldGen = 2;                        // 1 = a world from before villages existed (it gets none), 2 = villages",
    "let worldGen = 2;                        // 1 = a world from before villages existed (it gets none), 2 = villages, 4 = roads and signposts between them")
# ---------- signpost block ----------
rep("  // beds: two cells, a low mattress on a plank frame;", """  // a signpost: a post with a board; use it to read where the road goes
  IS_SHAPED[SIGNPOST]=1; SH_BOXES[SIGNPOST]=[[.4375,0,.4375,.5625,1.25,.5625],[.0625,.75,.4375,.9375,1.125,.5625]]; SH_COL[SIGNPOST]=[[.4375,0,.4375,.5625,1.25,.5625]];
  SH_BASE[SIGNPOST]=PLANK_IDS[0]; SH_MAT[SIGNPOST]=0; COLORS[SIGNPOST]=COLORS[PLANK_IDS[0]]; NAMES[SIGNPOST]='signpost';
  // beds: two cells, a low mattress on a plank frame;""")
rep("const IS_SHAPED = new Uint8Array(NB),", "const SIGNPOST = 1131;\nconst IS_SHAPED = new Uint8Array(NB),")
rep("S(COAL, 11);", "S(COAL, 11); S(SIGNPOST, 4);")
rep("const KIND = { ", "const KIND = { [SIGNPOST]:'axe', ")
# ---------- roads, names, signs ----------
mod = r'''
// ---------- roads between villages, village names and signposts (worlds made from now on) ----------
// Every village is joined by a dirt road to its nearest neighbour. The road wanders a little, avoids water, and where it leaves
// a village a signpost names the place it leads to and how far it is.
const VN_A = ['Raven','Oak','Stone','Thorn','Ash','Elder','Black','Wolf','Mill','Brook','Iron','Fern','Mead','Hollow','Grey','Cold'];
const VN_B = ['ford','wick','dale','stead','mere','haven','cross','field','hold','bury','moor','well','gate','ton'];
function villageName(rx,rz){ const a = Math.floor(h3(rx,31,rz,SEED+700)*VN_A.length), b = Math.floor(h3(rx,32,rz,SEED+701)*VN_B.length); return VN_A[a]+VN_B[b]; }
const roadEdgeCache = new Map(), roadChunkCache = new Map();
function inVillageRects(v,x,z,m){ for(const R of v.rects) if(x>=R.x0-m && x<=R.x1+m && z>=R.z0-m && z<=R.z1+m) return true; return false; }
// the road edges whose line passes near region (rx,rz)
function roadEdgesNear(rx,rz){
  const key = chunkKey(rx,rz); let E = roadEdgeCache.get(key); if(E) return E;
  E = [];
  if(worldGen>=4 && !isUnder(rz*VREG) && !isTestZ(rz*VREG)){
    const seen = new Set();
    for(let a=-2;a<=2;a++) for(let b=-2;b<=2;b++){
      const ax = rx+a, az = rz+b, va = villageAt(ax,az); if(!va || !va.houses) continue;
      const ca = villageCentre(va); let best = null, bd = 1e9;
      for(let c=-2;c<=2;c++) for(let d=-2;d<=2;d++){ if(!c && !d) continue; const vb = villageAt(ax+c, az+d); if(!vb || !vb.houses) continue;
        const cb = villageCentre(vb), dd = Math.hypot(cb[0]-ca[0], cb[1]-ca[1]); if(dd<bd){ bd = dd; best = [ax+c, az+d, vb, cb]; } }
      if(!best || bd>520) continue;
      const k = [ax+','+az, best[0]+','+best[1]].sort().join('|'); if(seen.has(k)) continue; seen.add(k);
      const [bx,bz,vb,cb] = best, len = bd, ux = (cb[0]-ca[0])/len, uz = (cb[1]-ca[1])/len;
      const e = { ax:ca[0], az:ca[1], ux, uz, nx:-uz, nz:ux, len, seed:h3(ax,bx,az+bz,SEED+710)*6.28, va, vb, ra:[ax,az], rb:[bx,bz] };
      // keep only edges that pass within reach of this region
      const x0 = Math.min(ca[0],cb[0])-12, x1 = Math.max(ca[0],cb[0])+12, z0 = Math.min(ca[1],cb[1])-12, z1 = Math.max(ca[1],cb[1])+12;
      if(x1 < rx*VREG || x0 > (rx+1)*VREG || z1 < rz*VREG || z0 > (rz+1)*VREG) continue;
      // a signpost just outside each village, beside the road
      e.signs = [];
      for(const [from, v0, toR] of [[0, va, [bx,bz]], [1, vb, [ax,az]]]){
        for(let t=4; t<len/2; t+=1){
          const tt = from ? len-t : t, p = roadPoint(e, tt);
          if(!inVillageRects(v0, p[0], p[1], 3)){ const sgn = from ? -1 : 1, sx = Math.floor(p[0]+e.nx*2.6*sgn), sz = Math.floor(p[1]+e.nz*2.6*sgn);
            e.signs.push({ x:sx, z:sz, to:toR, toName:villageName(toR[0],toR[1]), dist:Math.round(len/10)*10, dir:from ? dirWord(cb[0],cb[1],ca[0],ca[1]) : dirWord(ca[0],ca[1],cb[0],cb[1]), here:villageName(from?bx:ax, from?bz:az) }); break; }
        }
      }
      E.push(e);
    }
  }
  roadEdgeCache.set(key, E); return E;
}
function roadWig(e,t){ const fade = Math.min(1, t/30, (e.len-t)/30); return (4*Math.sin(t/37+e.seed) + 2*Math.sin(t/13+e.seed*2))*Math.max(0,fade); }
function roadPoint(e,t){ const w = roadWig(e,t); return [e.ax+e.ux*t+e.nx*w, e.az+e.uz*t+e.nz*w]; }
// per chunk: which columns are road, and where the signposts stand
function roadChunk(cx,cz){
  const key = chunkKey(cx,cz); let R = roadChunkCache.get(key); if(R) return R;
  R = { road:new Uint8Array(CS*CS), signs:new Map() };
  if(worldGen>=4){
    const E = roadEdgesNear(Math.floor(cx*CS/VREG), Math.floor(cz*CS/VREG));
    for(const e of E){
      for(const sg of e.signs) if(Math.floor(sg.x/CS)===cx && Math.floor(sg.z/CS)===cz) R.signs.set(sg.x+','+sg.z, sg);
      for(let i=0;i<CS;i++) for(let j=0;j<CS;j++){
        const x = cx*CS+i, z = cz*CS+j, t = (x+0.5-e.ax)*e.ux + (z+0.5-e.az)*e.uz;
        if(t<0 || t>e.len) continue;
        const off = (x+0.5-e.ax)*e.nx + (z+0.5-e.az)*e.nz;
        if(Math.abs(off - roadWig(e,t)) <= 1.05 && !inVillageRects(e.va,x,z,1) && !inVillageRects(e.vb,x,z,1)) R.road[i*CS+j] = 1;
      }
    }
  }
  if(roadChunkCache.size>3000) roadChunkCache.clear();
  roadChunkCache.set(key, R); return R;
}
function roadAt(x,z){ if(worldGen<4) return false; const cx = Math.floor(x/CS), cz = Math.floor(z/CS); return !!roadChunk(cx,cz).road[(x-cx*CS)*CS + (z-cz*CS)]; }
function nearRoad(x,z){ if(worldGen<4) return false; for(let dx=-3;dx<=3;dx++) for(let dz=-3;dz<=3;dz++) if(roadAt(x+dx,z+dz)) return true; return false; }
function signAt(x,z){ if(worldGen<4) return null; const cx = Math.floor(x/CS), cz = Math.floor(z/CS); return roadChunk(cx,cz).signs.get(x+','+z) || null; }
'''
rep("function villageNoTree(x,z){", mod+"function villageNoTree(x,z){")
# trees keep off the road
rep("if(okTop && !ci.open && ci.h>SEA+1 && ci.h+24<H && !villageNoTree(rx,rz)){", "if(okTop && !ci.open && ci.h>SEA+1 && ci.h+24<H && !villageNoTree(rx,rz) && !nearRoad(rx,rz)){")
# the road surface and signposts in terrain
rep("    if(y===h+1 && ci.top===GRASS && !ci.open && h>SEA){ if(catnipAt(x,z))",
    "    if(y===h+1 && worldGen>=4 && !ci.open && h>SEA && signAt(x,z)) return SIGNPOST;\n    if(y===h+1 && ci.top===GRASS && !ci.open && h>SEA && worldGen>=4 && roadAt(x,z)) return AIR;\n    if(y===h+1 && ci.top===GRASS && !ci.open && h>SEA){ if(catnipAt(x,z))")
rep("    if(y===h) return ci.top===STONE ? stoneFace(x,y,z,h) : ci.top;",
    "    if(y===h && worldGen>=4 && !ci.open && h>SEA && (ci.top===GRASS || ci.top===DIRT || ci.top===SNOW || ci.top===SAND) && roadAt(x,z)) return PATH;\n    if(y===h) return ci.top===STONE ? stoneFace(x,y,z,h) : ci.top;")
# reading a signpost
rep("  if(hit.b === CRAFT_TABLE){ openCraft(3); return; }", """  if(hit.b === CRAFT_TABLE){ openCraft(3); return; }
  if(hit.b === SIGNPOST){ const sg = signAt(hit.x,hit.z); skillToast(sg ? `${sg.here}<br><small>\\u2192 ${sg.toName}, ${sg.dist} paces ${sg.dir}</small>` : 'The sign is weathered blank', true); return; }""")
# ---------- discovered places, the map, wagons, inns ----------
mod2 = r'''
// ---------- the map, discovered villages, wagons and inns ----------
// Places you have been fill in on your map (MENU > MAP, or M). Villages you have walked into are marked with their names, and from
// any village or homestead you can take a wagon to any village you have already visited, for gold and a few hours of the day.
// The villager in a village lets you rent a room: it becomes your respawn point, and you wake up rested.
let explored = new Set(), visitedV = new Set(), exploreT = 0, lastVillageName = '';
const mapTiles = new Map();
function exploreTick(){
  if(testWorld || isUnder(player.z) || isTestZ(player.z)) return;
  const cx = Math.floor(player.x/CS), cz = Math.floor(player.z/CS);
  for(let a=-4;a<=4;a++) for(let b=-4;b<=4;b++) if(a*a+b*b<=17) explored.add((cx+a)+','+(cz+b));
  const rx = Math.floor(player.x/VREG), rz = Math.floor(player.z/VREG);
  let inName = '';
  for(let a=-1;a<=1;a++) for(let b=-1;b<=1;b++){ const v = villageAt(rx+a,rz+b); if(!v || !v.houses) continue;
    const c = villageCentre(v); if(Math.hypot(c[0]-player.x, c[1]-player.z) < 45){ const k = (rx+a)+','+(rz+b); inName = villageName(rx+a,rz+b);
      if(!visitedV.has(k)){ visitedV.add(k); skillToast(inName.toUpperCase()+'<br><small>discovered</small>', true); scheduleSave(); } } }
  for(const hs of homesteads) if(Math.hypot(hs.cx-player.x, hs.cz-player.z) < 30) inName = hs.name;
  if(inName && inName!==lastVillageName && !skillToastT) skillToast(inName);
  lastVillageName = inName;
}
function mapTile(cx,cz){
  const k = cx+','+cz; let c = mapTiles.get(k); if(c) return c;
  c = document.createElement('canvas'); c.width = c.height = 8; const g = c.getContext('2d'), img = g.createImageData(8,8);
  for(let i=0;i<8;i++) for(let j=0;j<8;j++){
    const x = cx*CS+i*2, z = cz*CS+j*2, ci = colInfo(x,z);
    let col = ci.h<=SEA && !ci.open ? [52,92,170] : (COLORS[ci.top] || [120,120,120]);
    if(roadAt(x,z) || roadAt(x+1,z)) col = [150,120,80];
    const sh = 0.75 + Math.max(-0.2, Math.min(0.35, (ci.h-SEA)/60));
    const o = (j*8+i)*4; img.data[o] = col[0]*sh; img.data[o+1] = col[1]*sh; img.data[o+2] = col[2]*sh; img.data[o+3] = 255;
  }
  g.putImageData(img,0,0); mapTiles.set(k,c); if(mapTiles.size>6000) mapTiles.clear(); return c;
}
let mapZoom = 1, mapPick = null;
function knownPlaces(){
  const out = [];
  for(const k of visitedV){ const [rx,rz] = k.split(',').map(Number), v = villageAt(rx,rz); if(!v || !v.houses) continue; const c = villageCentre(v); out.push({ kind:'v', key:k, name:villageName(rx,rz), x:c[0], z:c[1] }); }
  for(const hs of homesteads) out.push({ kind:'h', key:'h'+hs.id, name:hs.name, x:hs.cx, z:hs.cz });
  return out;
}
function atPlace(){ return knownPlaces().find(p=>Math.hypot(p.x-player.x, p.z-player.z) < 50) || null; }
function wagonCost(p){ const d = Math.hypot(p.x-player.x, p.z-player.z); return { gold:Math.round(5 + d/15), hours:Math.max(1, Math.round(d/90)), d }; }
function drawMap(){
  const cv = document.getElementById('mapCanvas'), g = cv.getContext('2d'), W = cv.width, Hh = cv.height, S = 0.5*mapZoom;     // pixels per block
  g.fillStyle = '#0d0e0b'; g.fillRect(0,0,W,Hh); g.imageSmoothingEnabled = false;
  const px = player.x, pz = player.z, toS = (x,z)=>[W/2+(x-px)*S, Hh/2+(z-pz)*S];
  const r = Math.ceil(Math.max(W,Hh)/(S*CS)/2)+1, pcx = Math.floor(px/CS), pcz = Math.floor(pz/CS);
  for(let a=-r;a<=r;a++) for(let b=-r;b<=r;b++){ const cx = pcx+a, cz = pcz+b; if(!explored.has(cx+','+cz)) continue; const [sx,sy] = toS(cx*CS, cz*CS); g.drawImage(mapTile(cx,cz), sx, sy, CS*S+0.6, CS*S+0.6); }
  g.font = 'bold 11px monospace'; g.textAlign = 'center';
  const mark = (x,z,col,label,sq)=>{ const [sx,sy] = toS(x,z); if(sx<-40||sy<-20||sx>W+40||sy>Hh+20) return; g.fillStyle = '#000'; g.fillRect(sx-5,sy-5,10,10); g.fillStyle = col; g.fillRect(sx-4,sy-4,8,8);
    if(label){ g.fillStyle = 'rgba(0,0,0,.65)'; const w = g.measureText(label).width; g.fillRect(sx-w/2-3, sy-20, w+6, 13); g.fillStyle = col; g.fillText(label, sx, sy-10); } };
  for(const p of knownPlaces()) mark(p.x, p.z, p.kind==='h' ? '#8fdc6a' : '#e3cf95', p.name);
  for(const q of quests){ const t = q.kind==='hunt' && q.state==='active' ? q.at : q.kind==='deliver' ? q.tvc : null; if(t) mark(t[0], t[1], '#e05040', q.kind==='hunt' ? BEAST_NAME[q.beast] : q.toName); }
  for(const sk of deathSacks) mark(sk.x, sk.z, '#ffe28c', 'your belongings');
  // you: an arrow pointing the way you face
  const f = camVectors().f, a = Math.atan2(f[0], f[2]);
  g.save(); g.translate(W/2, Hh/2); g.rotate(-a); g.fillStyle = '#fff'; g.strokeStyle = '#000'; g.lineWidth = 2;
  g.beginPath(); g.moveTo(0,9); g.lineTo(-6,-6); g.lineTo(0,-2); g.lineTo(6,-6); g.closePath(); g.stroke(); g.fill(); g.restore();
  g.fillStyle = '#8f8a7a'; g.textAlign = 'left'; g.font = '10px monospace'; g.fillText('N ↑', 8, 14);
}
function renderMapSide(){
  const el = document.getElementById('mapSide'), here = atPlace();
  let h = `<div class="skNote">${here ? 'You are at '+here.name+'.' : 'Wagons leave from villages and homesteads.'} Tap a place to travel there.</div>`;
  for(const p of knownPlaces().sort((a,b)=>Math.hypot(a.x-player.x,a.z-player.z)-Math.hypot(b.x-player.x,b.z-player.z))){
    const c = wagonCost(p), isHere = here && here.key===p.key;
    h += `<div class="tkRow"><span class="tkNm" style="color:${p.kind==='h'?'#8fdc6a':'#e3cf95'}">${p.name}</span><span class="tkPr">${isHere ? 'here' : Math.round(c.d/10)*10+' paces '+dirWord(player.x,player.z,p.x,p.z)}</span>`;
    if(!isHere) h += `<button data-go="${p.key}" ${!here || gold<c.gold ? 'disabled' : ''}>WAGON ${c.gold}g · ${c.hours}h</button>`;
    h += `</div>`;
  }
  el.innerHTML = h;
}
function openMap(){
  craftOpen = true; if(document.pointerLockElement) document.exitPointerLock();
  const cv = document.getElementById('mapCanvas'), box = cv.parentElement; cv.width = Math.min(560, box.clientWidth||360); cv.height = Math.min(380, Math.round(window.innerHeight*0.5));
  document.getElementById('mapMenu').classList.add('show'); drawMap(); renderMapSide();
}
function closeMap(){ document.getElementById('mapMenu').classList.remove('show'); craftOpen = false; }
function advanceHours(hours){
  let t = tod + hours/24;
  while(t>=1){ t -= 1; tod = 0.0001; rainDawn(false); villagerDawn(); homesteadDawn(); questDawn(); }
  tod = t; rainPrevTod = tod;
}
function wagonTo(key){
  const p = knownPlaces().find(q=>q.key===key), here = atPlace(); if(!p || !here) return;
  const c = wagonCost(p); if(gold<c.gold) return;
  gold -= c.gold; food = Math.max(2, food - Math.min(6, Math.round(c.hours/2)));
  advanceHours(c.hours);
  player.x = p.x+0.5; player.z = p.z+0.5; player.vy = 0;
  updateChunks();
  let best = null;
  for(let r=0;r<12 && !best;r++) for(let a=-r;a<=r && !best;a++) for(let b=-r;b<=r;b++){ if(Math.max(Math.abs(a),Math.abs(b))!==r) continue;
    const x = Math.floor(p.x)+a, z = Math.floor(p.z)+b, y = colInfo(x,z).h+1; if(ratCanStand(x,y,z) && PASS[getB(x,y+1,z)] && !roadAt(x,z)===false || ratCanStand(x,y,z) && PASS[getB(x,y+1,z)]){ best = [x,y,z]; break; } }
  if(best){ player.x = best[0]+0.5; player.y = best[1]; player.z = best[2]+0.5; } else player.y = colInfo(Math.floor(p.x),Math.floor(p.z)).h+2;
  fallPeakY = player.y; safeT = 2; vitalKey = '';
  for(let i=mobs.length-1;i>=0;i--) if(Math.hypot(mobs[i].x-player.x, mobs[i].z-player.z) > 70) mobs.splice(i,1);
  closeMap(); sleepMsg(`After ${c.hours} hours on the road, you arrive at ${p.name}.`, 2600); scheduleSave();
}
'''
rep("// ---------- the map, discovered villages", "") if "// ---------- the map, discovered villages" in s else None
rep("function villageCentre(v){", mod2+"function villageCentre(v){")
# explore tick in the 200ms interval: piggyback on updateMobs npc timer
rep("  if(NPCS_IN_WORLD){ npcSpawnT -= dt; if(npcSpawnT<=0){ npcSpawnT = 3; trySpawnNpcs(); questTick(); } }",
    "  if(NPCS_IN_WORLD){ npcSpawnT -= dt; if(npcSpawnT<=0){ npcSpawnT = 3; trySpawnNpcs(); questTick(); } }\n  exploreT -= dt; if(exploreT<=0){ exploreT = 1; exploreTick(); }")
# inn: rent a room from the villager
rep("    if(m.job==='blacksmith'){ const rc = repairCost(); if(rc>0) h += `<button data-a=\"repair\">REPAIR (${rc}g)</button>`; }",
    "    if(m.job==='blacksmith'){ const rc = repairCost(); if(rc>0) h += `<button data-a=\"repair\">REPAIR (${rc}g)</button>`; }\n    if(m.job==='villager' && m.house && m.house.bed) h += `<button data-a=\"room\">RENT A ROOM (8g)</button>`;")
rep("  else if(a==='repair'){", """  else if(a==='room'){
    if(gold<8) talkLine = 'A room is 8 gold. You have '+gold+'.';
    else { gold -= 8; bedSpawn = m.house.bed.slice(); health = maxHP(); vitalKey = '';
      if(Math.sin(tod*Math.PI*2) < -0.05){ closeTalk(); const el = document.getElementById('sleepov'); if(el){ el.textContent = 'Sleeping...'; el.classList.add('dark'); el.style.opacity = '1'; }
        clearTimeout(sleepMsg.t); sleepMsg.t = setTimeout(()=>{ advanceHours(((1.02-tod)%1)*24); scheduleSave(); if(el){ el.textContent = 'Good morning'; el.style.opacity = '0'; } }, 1300); return; }
      talkLine = 'The bed upstairs is yours. You feel rested. If you fall, you will wake up here.'; scheduleSave(); }
  }
  else if(a==='repair'){""")
# village name in talk header and news
rep("  document.getElementById('talkName').textContent = m.name + ' \\u2014 ' + (JOB_TITLE[m.job]||'Villager');",
    "  document.getElementById('talkName').textContent = m.name + ' \\u2014 ' + (JOB_TITLE[m.job]||'Villager') + (hsOf(m) ? ' of '+hsOf(m).name : m.village ? ' of '+villageName(m.village[0],m.village[1]) : '');")
rep("    lines.push(`The nearest village lies about ${Math.round(bd/10)*10} paces to the ${DIR8[k]}.`); }",
    "    lines.push(`${best.length>2 ? best[2] : 'The nearest village'} lies about ${Math.round(bd/10)*10} paces to the ${DIR8[k]}.`); }")
rep("const c = villageCentre(v), d = Math.hypot(c[0]-hc[0], c[1]-hc[1]); if(d<bd){ bd = d; best = c; } }",
    "const c = villageCentre(v), d = Math.hypot(c[0]-hc[0], c[1]-hc[1]); if(d<bd){ bd = d; best = [c[0], c[1], villageName(rx+a, rz+b)]; } }")
# map UI
rep('    <button id="charBtn">APPEARANCE</button>', '    <button id="mapBtn">MAP</button>\n    <button id="charBtn">APPEARANCE</button>')
rep('<div id="skillToast"></div>', '''<div id="mapMenu"><div id="mapPanel"><div id="skillTop"><h2>Map</h2><span><button id="mapOut">\\u2212</button> <button id="mapIn">+</button> <button id="mapClose">DONE</button></span></div><div><canvas id="mapCanvas" width="360" height="300"></canvas></div><div id="mapSide"></div></div></div>
<div id="skillToast"></div>'''.replace('\\u2212','&minus;'))
rep("  #skillMenu.show { display:flex; }", """  #skillMenu.show { display:flex; }
  #mapMenu { position:fixed; inset:0; z-index:21; display:none; align-items:center; justify-content:center; color:#d8cfb8; font-family:monospace; background:rgba(0,0,0,.92); }
  #mapMenu.show { display:flex; }
  #mapPanel { width:min(96vw,600px); max-height:96vh; overflow-y:auto; padding:10px 12px; box-sizing:border-box; background:linear-gradient(#1b1d18,#0f100e); border:2px solid #050605; box-shadow:inset 0 0 0 1px #8c7640; }
  #mapPanel h2 { margin:0; color:#e3cf95; letter-spacing:3px; font-size:18px; }
  #mapPanel button { font:12px monospace; letter-spacing:1px; padding:6px 10px; background:linear-gradient(#34372f,#1d1f1a); color:#e3cf95; border:2px solid #050605; box-shadow:inset 0 0 0 1px #8c7640; }
  #mapPanel button:disabled { opacity:.35; }
  #mapCanvas { width:100%; display:block; border:2px solid #050605; box-shadow:inset 0 0 0 1px #3a3d35; image-rendering:pixelated; margin:6px 0; }
  #mapSide .tkRow { border-top:1px solid #2a2c26; padding:5px 0; }""")
rep("document.getElementById('skillBtn').addEventListener('click', openSkills);", """document.getElementById('skillBtn').addEventListener('click', openSkills);
document.getElementById('mapBtn').addEventListener('click', ()=>{ closeMenu(); paused = false; openMap(); });
document.getElementById('mapClose').addEventListener('click', closeMap);
document.getElementById('mapIn').addEventListener('click', ()=>{ mapZoom = Math.min(4, mapZoom*2); drawMap(); });
document.getElementById('mapOut').addEventListener('click', ()=>{ mapZoom = Math.max(0.25, mapZoom/2); drawMap(); });
document.getElementById('mapSide').addEventListener('click', e=>{ const b = e.target.closest('button'); if(b && !b.disabled && b.dataset.go) wagonTo(b.dataset.go); });""")
rep("function closeCraft(){\n  if(document.getElementById('skillMenu').classList.contains('show')){ closeSkills(); return; }",
    "function closeCraft(){\n  if(document.getElementById('mapMenu').classList.contains('show')){ closeMap(); return; }\n  if(document.getElementById('skillMenu').classList.contains('show')){ closeSkills(); return; }")
rep("  if(e.code==='KeyJ' && !e.repeat && !paused && document.activeElement.tagName!=='INPUT'){",
    "  if(e.code==='KeyM' && !e.repeat && !paused && document.activeElement.tagName!=='INPUT'){ if(document.getElementById('mapMenu').classList.contains('show')) closeMap(); else if(!craftOpen) openMap(); return; }\n  if(e.code==='KeyJ' && !e.repeat && !paused && document.activeElement.tagName!=='INPUT'){")
# save / load
rep("gold, armor, trained:trainedDay, homesteads, homesteadId,", "gold, armor, trained:trainedDay, homesteads, homesteadId, explored:[...explored], visited:[...visitedV],")
rep("  trainedDay = meta.trained || {}; homesteads", "  explored = new Set(meta.explored || []); visitedV = new Set(meta.visited || []); mapTiles.clear(); roadEdgeCache.clear(); roadChunkCache.clear();\n  trainedDay = meta.trained || {}; homesteads")
open(p,'w').write(s); print('ok')
