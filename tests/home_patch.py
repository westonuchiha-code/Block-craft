p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
mod = r'''
// ---------- homesteads: villages you build ----------
// A bed inside a proper house you built (walls all round, a roof, a door) is a home waiting for someone. At sunrise a traveller
// may move in, and their trade comes from what the house holds: a furnace makes a smith, a cooking table a baker, bookshelves a
// scholar, a stone cutter a miner, candles a cleric, hay or tilled soil by the door a farmer, water nearby a fisher. Once two have
// settled, the next newcomer keeps watch as a guard. Your settlers live like any villagers: they work, trade, give you jobs,
// defend the place, sleep at night, come back in their beds if they die, and leave if their bed is broken.
let homesteads = [], homesteadId = 1;
const HS_A = ['Oak','Stone','Raven','Mill','Ash','Brook','Thorn','Wolf','Elder','Hearth','Fern','Iron'], HS_B = ['hollow','ford','stead','wick','dale','haven','mere','hold','field','cross'];
function hsHere(x,z){ return homesteads.find(h=>Math.hypot(h.cx-x, h.cz-z) < 48) || null; }
// is the bed inside a closed, roofed room with a door? Walk the floor from the bed until we hit walls, the open sky, or wander too far.
function houseCheck(bx,by,bz){
  const head = getB(bx,by,bz); if(!IS_BED[head]) return { ok:false, why:'no bed' };
  const o = bedOther(head,bx,by,bz), seen = new Set(), q = [];
  const pass = (x,y,z)=>{ const b = getB(x,y,z); return (PASS[b] || IS_FURN[b] || IS_BED[b] || IS_LANTERN[b]) && !IS_DOOR[b] && !IS_WATER[b] && !IS_LAVA[b]; };
  for(const [x,z] of [[bx,bz],[o[0],o[2]]]) for(const [dx,dz] of H4) if(pass(x+dx,by,z+dz)) q.push([x+dx,z+dz]);
  for(const [x,z] of [[bx,bz],[o[0],o[2]]]) seen.add(x+','+z);
  let door = null, out = null, inside = null;
  while(q.length){
    const [x,z] = q.shift(), k = x+','+z; if(seen.has(k)) continue; seen.add(k);
    if(seen.size>260) return { ok:false, why:'too open: it needs walls all the way round' };
    if(Math.abs(x-bx)>14 || Math.abs(z-bz)>14) return { ok:false, why:'too open: it needs walls all the way round' };
    let roof = false; for(let y=by+2; y<=by+12; y++){ if(!PASS[getB(x,y,z)]){ roof = true; break; } }
    if(!roof) return { ok:false, why:'it needs a roof' };
    if(!inside && ratCanStand(x,by,z) && PASS[getB(x,by+1,z)]) inside = [x,by,z];
    for(const [dx,dz] of H4){
      const nx = x+dx, nz = z+dz, nb = getB(nx,by,nz);
      if(IS_DOOR[nb] && !door){ door = [nx,by,nz]; out = [nx+dx,by,nz+dz]; }
      if(pass(nx,by,nz) && pass(nx,by+1,nz)) q.push([nx,nz]);
    }
  }
  if(!door) return { ok:false, why:'it needs a door' };
  if(!inside) return { ok:false, why:'there is no room to stand' };
  // what the house holds decides the trade
  let job = 'villager'; const has = new Set();
  for(const k of seen){ const [x,z] = k.split(',').map(Number); for(let y=by-1;y<=by+2;y++){ const b = getB(x,y,z); has.add(b); for(const [dx,dz] of H4) has.add(getB(x+dx,y,z+dz)); } }
  let near = new Set(); for(let dx=-6;dx<=6;dx++) for(let dz=-6;dz<=6;dz++) for(let dy=-2;dy<=1;dy++) near.add(getB(out[0]+dx,by+dy,out[2]+dz));
  if(has.has(FURNACE) && has.has(CUTTER)) job = 'miner';
  else if(has.has(FURNACE)) job = 'blacksmith';
  else if(has.has(COOK_TABLE)) job = 'baker';
  else if(has.has(BOOKSHELF)) job = 'librarian';
  else if(has.has(CUTTER)) job = 'miner';
  else if([...has].some(b=>b===CANDLE)) job = 'cleric';
  else if(near.has(HAY) || near.has(TILLED) || near.has(TILLED_WET)) job = 'farmer';
  else if([...near].some(b=>IS_WATER[b])) job = 'fisher';
  return { ok:true, inside, door, out, job, rooms:seen.size };
}
// a bed was just placed: does it make a home?
function bedPlaced(x,y,z){
  if(testWorld || isUnder(z) || isTestZ(z)) return;
  if(nearVillage(x,z)){ skillToast('This village already has its people'); return; }
  const r = houseCheck(x,y,z);
  if(!r.ok){ skillToast('Not a home yet<br><small>'+r.why+'</small>', true); return; }
  let hs = hsHere(x,z);
  if(!hs){
    const id = homesteadId++, nm = HS_A[(id*7+Math.floor(x))%HS_A.length & 0xff % HS_A.length] || HS_A[0];
    hs = { id, name: HS_A[Math.abs(id*7+x)%HS_A.length] + HS_B[Math.abs(id*3+z)%HS_B.length], cx:x, cz:z, homes:[] };
    homesteads.push(hs); villageRep[vkey(['h',id])] = 40;
  }
  hs.homes.push({ bed:[x,y,z], inside:r.inside, out:r.out, door:r.door, job:r.job, ch:null });
  hs.cx = hs.homes.reduce((a,h)=>a+h.out[0],0)/hs.homes.length; hs.cz = hs.homes.reduce((a,h)=>a+h.out[2],0)/hs.homes.length;
  skillToast(`A home in ${hs.name}<br><small>someone may move in by morning${r.job!=='villager' ? ' · a '+(JOB_TITLE[r.job]||r.job).toLowerCase()+"'s house" : ''}</small>`, true);
  scheduleSave();
}
function homesteadDawn(){
  for(const hs of homesteads){
    for(let i=hs.homes.length-1;i>=0;i--){
      const H = hs.homes[i], key = 'h'+hs.id+':'+i, loaded = chunks.has(chunkKey(Math.floor(H.bed[0]/CS), Math.floor(H.bed[2]/CS)));
      if(!loaded) continue;
      const mine = bedSpawn && Math.abs(bedSpawn[0]-H.bed[0])<=1 && bedSpawn[1]===H.bed[1] && Math.abs(bedSpawn[2]-H.bed[2])<=1;
      if(!IS_BED[getB(H.bed[0],H.bed[1],H.bed[2])]){                                  // the bed is gone: so is whoever slept in it
        if(H.ch) skillToast(H.ch.name+' has left '+hs.name+'<br><small>their bed is gone</small>', true);
        H.ch = null; H.gone = true; delete villagerState[key]; continue;
      }
      H.gone = false;
      if(!H.ch && !mine && Math.random()<0.75){
        const r = houseCheck(H.bed[0],H.bed[1],H.bed[2]); if(!r.ok) continue;
        Object.assign(H, { inside:r.inside, out:r.out, door:r.door, job:r.job });
        const settled = hs.homes.filter(h=>h.ch).length, guards = hs.homes.filter(h=>h.ch && h.ch.job==='guard').length;
        const job = settled>=2 && !guards ? 'guard' : H.job;
        H.ch = npcGenerate(null, job); H.ch.job = job;
        skillToast(`${H.ch.name} the ${(JOB_TITLE[job]||job).toLowerCase()}<br><small>has moved into ${hs.name}</small>`, true);
      }
    }
  }
  scheduleSave();
}
function hsOf(m){ return m && m.village && m.village[0]==='h' ? homesteads.find(h=>h.id===m.village[1]) : null; }
function villageHouses(m){ const hs = hsOf(m); if(hs) return hs.homes.filter(h=>h.ch); const v = m.village && villageAt(m.village[0], m.village[1]); return v ? v.houses : []; }
function regionOf(m){ const hs = hsOf(m); if(hs) return [Math.floor(hs.cx/VREG), Math.floor(hs.cz/VREG)]; return m.village || [Math.floor(m.x/VREG), Math.floor(m.z/VREG)]; }
'''
rep("function villageCentre(v){", mod+"function villageCentre(v){")
# spawn settlers
rep("function trySpawnNpcs(){\n  if(isUnder(player.z) || isTestZ(player.z)) return;", """function trySpawnNpcs(){
  if(isUnder(player.z) || isTestZ(player.z)) return;
  for(const hs of homesteads){
    if(Math.hypot(hs.cx-player.x, hs.cz-player.z) > 90) continue;
    hs.homes.forEach((H,i)=>{
      if(!H.ch) return;
      const key = 'h'+hs.id+':'+i, st = villagerState[key];
      if((st && (st.dead || st.gone)) || mobs.some(m=>m.home===key)) return;
      if(Math.hypot(H.out[0]+0.5-player.x, H.out[2]+0.5-player.z) > 56) return;
      const at = ratNight && H.ch.job!=='guard' ? H.inside : H.out;
      if(!npcCanStand(at[0],at[1],at[2])) return;
      const m = newNpc(at[0],at[1],at[2], H.ch);
      m.home = key; m.house = H; m.village = ['h', hs.id]; m.vc = [hs.cx, hs.cz];
      mobs.push(m);
    });
  }""")
rep("    const [r, i] = k.split(':'), [rx,rz] = r.split(',').map(Number), v = villageAt(rx,rz), h = v && v.houses[+i];",
    "    if(k[0]==='h'){ delete villagerState[k]; continue; }              // settlers: back in their beds (homesteadDawn handles lost beds)\n    const [r, i] = k.split(':'), [rx,rz] = r.split(',').map(Number), v = villageAt(rx,rz), h = v && v.houses[+i];")
rep("  if(wrapped){ villagerDawn(); questDawn(); }", "  if(wrapped){ villagerDawn(); homesteadDawn(); questDawn(); }")
# generalize village lookups
rep("vv = villageAt(m.village[0], m.village[1]);\n        const q = h || vv.houses[Math.floor(Math.random()*vv.houses.length)];",
    "vv = villageHouses(m);\n        const q = h || vv[Math.floor(Math.random()*vv.length)] || m.house;")
rep("  const [rx,rz] = m.village || [Math.floor(m.x/VREG), Math.floor(m.z/VREG)], here = villageAt(rx,rz), hc = here ? villageCentre(here) : [m.x,m.z];",
    "  const [rx,rz] = regionOf(m), here = hsOf(m) ? null : villageAt(rx,rz), hc = m.vc || (here ? villageCentre(here) : [m.x,m.z]);")
rep("    const [rx,rz] = m.village; let best = null, bd = 1e9;", "    const [rx,rz] = regionOf(m); let best = null, bd = 1e9;")
# bed placement hook
rep("        setB(x,y,z,BED0+face*2); setB(x+d[0],y,z+d[1],BED0+face*2+1);\n        inv[b]--; scheduleSave(); return;",
    "        setB(x,y,z,BED0+face*2); setB(x+d[0],y,z+d[1],BED0+face*2+1);\n        inv[b]--; scheduleSave(); bedPlaced(x,y,z); return;")
# standing tab lists your homesteads
rep("function questSheetParts(){ const h = renderQuests(),", """function homesteadSheet(){
  if(!homesteads.length) return '<div class="skNote">You have no homestead yet. Build a house with walls, a roof and a door, and put a bed in it: a traveller may move in. What you put in the house decides their trade.</div>';
  let h = '';
  for(const hs of homesteads){
    const d = Math.hypot(hs.cx-player.x, hs.cz-player.z), where = d<15 ? 'right here' : `${Math.round(d/10)*10} paces ${dirWord(player.x,player.z,hs.cx,hs.cz)}`;
    h += `<div class="skRow"><div class="skHead"><b>${hs.name}</b><span>${hs.homes.filter(x=>x.ch).length} settled</span></div><div class="skDesc">${where} \\u00b7 ${repWord(repOf(['h',hs.id]))}</div>`;
    hs.homes.forEach((H,i)=>{ const st = villagerState['h'+hs.id+':'+i];
      h += `<div class="skDesc" style="color:#d8cfb8">\\u2022 ${H.ch ? H.ch.name+', '+(JOB_TITLE[H.ch.job]||H.ch.job).toLowerCase()+(st&&st.dead?' (back at sunrise)':'') : H.gone ? 'a house whose bed is gone' : 'an empty '+(H.job!=='villager' ? (JOB_TITLE[H.job]||H.job).toLowerCase()+"'s " : '')+'house, waiting'}</div>`; });
    h += `</div>`;
  }
  return h;
}
function questSheetParts(){ const h = renderQuests(),""")
rep("    h += sheetTab==='quests' ? qh : (sh || '<div class=\"skNote\">No village knows you yet.", "    h += sheetTab==='quests' ? qh : '<div class=\"tkHd\">YOUR HOMESTEADS</div>' + homesteadSheet() + '<div class=\"tkHd\" style=\"margin-top:14px\">VILLAGES</div>' + (sh || '<div class=\"skNote\">No village knows you yet.")
# don't list own homesteads twice in standing
rep("  const reps = Object.keys(villageRep).filter(k=>villageRep[k]);", "  const reps = Object.keys(villageRep).filter(k=>villageRep[k] && k[0]!=='h');")
# save / load
rep("gold, armor, trained:trainedDay,", "gold, armor, trained:trainedDay, homesteads, homesteadId,")
rep("  trainedDay = meta.trained || {};", "  trainedDay = meta.trained || {}; homesteads = meta.homesteads || []; homesteadId = meta.homesteadId || 1;")
open(p,'w').write(s); print('ok')
