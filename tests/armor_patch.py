p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# ---------- ids, names, recipes data ----------
rep("const SACK = 1089;", """// ---- armor: four pieces (head, chest, legs, feet) in five materials. Leather comes from bears and tigers, chitin from scorpions,
// the metals from deep ore. Worn armor turns away part of every blow (not falls, hunger, drowning or fire) and wears out as it does. ----
const ARMOR0 = 1111;                                      // 1111..1130: material m (0..4) x slot k (0 head, 1 chest, 2 legs, 3 feet)
const AR = (m,k)=>ARMOR0 + m*4 + k;
const ARMOR_MATS = [
  { key:'leather', mat:LEATHER,    names:['leather cap','leather jerkin','leather leggings','leather boots'], pts:[1,3,2,1], dur:80,   col:[138,90,50] },
  { key:'chitin',  mat:CHITIN,     names:['chitin helm','chitin cuirass','chitin greaves','chitin boots'],   pts:[2,4,3,1], dur:160,  col:[166,108,48] },
  { key:'iron',    mat:IRON_INGOT, names:['iron helm','iron cuirass','iron greaves','iron boots'],           pts:[2,6,5,2], dur:240,  col:[196,198,206] },
  { key:'adam',    mat:ADAM_INGOT, names:['adamantite helm','adamantite cuirass','adamantite greaves','adamantite boots'], pts:[3,7,6,3], dur:700, col:[62,152,110] },
  { key:'mith',    mat:MITH_INGOT, names:['mithril helm','mithril cuirass','mithril greaves','mithril boots'], pts:[3,8,6,3], dur:1200, col:[184,214,250] } ];
const ARMOR_SLOT = ['head','chest','legs','feet'], ARMOR_DURK = [0.85, 1.25, 1.15, 0.75];      // a cuirass lasts longest
const ARMOR = {};                                          // id -> { m, k, pts, dur }
ARMOR_MATS.forEach((M,m)=>M.names.forEach((n,k)=>{ const id = AR(m,k); NAMES[id] = n; COLORS[id] = M.col; FLAT_ITEMS.add(id); ARMOR[id] = { m, k, pts:M.pts[k], dur:Math.round(M.dur*ARMOR_DURK[k]) }; }));
const SACK = 1089;""")
rep("  ...METALS.flatMap((M,t)=>[\n    { out:[MT(t,0),1], pat:['III',' S ',' S '], key:{I:M.ingot, S:STICK} },",
"""  ...ARMOR_MATS.flatMap((M,m)=>[
    { out:[AR(m,0),1], pat:['MMM','M M'],        key:{M:M.mat} },
    { out:[AR(m,1),1], pat:['M M','MMM','MMM'],  key:{M:M.mat} },
    { out:[AR(m,2),1], pat:['MMM','M M','M M'],  key:{M:M.mat} },
    { out:[AR(m,3),1], pat:['M M','M M'],        key:{M:M.mat} } ]),
  ...METALS.flatMap((M,t)=>[
    { out:[MT(t,0),1], pat:['III',' S ',' S '], key:{I:M.ingot, S:STICK} },""")
rep("  ...METALS.flatMap((M,t)=>[['pickaxe',3,2],", "  ...ARMOR_MATS.flatMap((M,m)=>[5,8,7,4].map((n,k)=>({ name:M.names[k][0].toUpperCase()+M.names[k].slice(1), out:[AR(m,k),1], ing:{[M.mat]:n} }))),\n  ...METALS.flatMap((M,t)=>[['pickaxe',3,2],")
# armor goes on the tools tab of the crafting book
rep("(craftTab===1) === (!!TOOLS[r.out[0]] ||", "(craftTab===1) === (!!TOOLS[r.out[0]] || !!ARMOR[r.out[0]] ||")
# ---------- worn armor, damage, wear ----------
rep("function hurt(points){\n  if(dead || points <= 0) return;\n  health = Math.max(0, health - points);",
"""// what you wear: one piece per slot, each { id, dur, dye } (dye: a dye index for leather, or -1)
let armor = [null,null,null,null];
function armorPoints(){ let p = 0; for(const a of armor) if(a) p += ARMOR[a.id].pts; return p; }
function armorCut(){ return Math.min(0.8, armorPoints()*0.04); }            // each point turns away 4% of a blow, at most 80%
function equipArmor(id){
  const A = ARMOR[id]; if(!A || !(inv[id]>0)) return false;
  const old = armor[A.k];
  inv[id]--; if(inv[id]<=0) delete inv[id];
  armor[A.k] = { id, dur:A.dur, dye:-1 };
  if(old) unequipTo(old);
  vitalKey = ''; scheduleSave(); return true;
}
function unequipTo(a){ inv[a.id] = Math.min(999, (inv[a.id]||0)+1); autoFillHotbar(a.id); }     // a piece taken off goes back in the pack (as new: wear is kept only while worn)
function unequipArmor(k){ const a = armor[k]; if(!a) return; armor[k] = null; unequipTo(a); vitalKey = ''; scheduleSave(); }
function dyeArmor(k, d){ const a = armor[k]; if(!a || ARMOR[a.id].m!==0 || !(inv[DYE0+d]>0)) return; inv[DYE0+d]--; if(inv[DYE0+d]<=0) delete inv[DYE0+d]; a.dye = d; scheduleSave(); }
function armorWear(){
  for(let k=0;k<4;k++){ const a = armor[k]; if(!a) continue; a.dur--;
    if(a.dur<=0){ armor[k] = null; skillToast(NAMES[a.id]+' broke'); } }
}
// pure: harm that armor can't stop (falling, hunger, drowning, fire and lava, cactus)
function hurt(points, pure){
  if(dead || points <= 0) return;
  if(!pure && armorPoints()>0){ points = Math.max(0.5, Math.round(points*(1-armorCut())*2)/2); armorWear(); }
  health = Math.max(0, health - points);""")
rep("    if(drop > 3) hurt(Math.floor(drop - 3));", "    if(drop > 3) hurt(Math.floor(drop - 3), true);")
rep("drownT = 0; hurt(2); } }", "drownT = 0; hurt(2, true); } }")
rep("if(health > 1) hurt(1); }", "if(health > 1) hurt(1, true); }")
rep("if(lavaT<=0){ hurt(2); lavaT = 0.5; }", "if(lavaT<=0){ hurt(2, true); lavaT = 0.5; }")
i=s.index("  if(cactusT<=0 && !dead){"); j=s.index("\n",i); seg=s[i:j]
assert seg.count("hurt(")==1; seg=seg.replace("hurt(1)","hurt(1, true)") if "hurt(1)" in seg else seg
s=s[:i]+seg+s[j:]
# hearts can now be fractional halves: make the heart display round to halves (already uses health - i*2 clamp 0..2; use Math.round)
rep("    heartEls[i].style.backgroundImage = VITAL_URLS.heart[Math.max(0, Math.min(2, health - i*2))];", "    heartEls[i].style.backgroundImage = VITAL_URLS.heart[Math.max(0, Math.min(2, Math.ceil(health - i*2)))];")
# wear it: use an armor piece in your hand
rep("  { const fb = HOTBAR[sel]; if(FOOD_VAL[fb] && inv[fb]>0) return; }", "  { const fb = HOTBAR[sel]; if(FOOD_VAL[fb] && inv[fb]>0) return; }\n  { const ab = HOTBAR[sel]; if(ARMOR[ab] && inv[ab]>0){ equipArmor(ab); skillToast('wearing '+NAMES[ab]); swingT = 1; return; } }")
# death: worn armor goes in the sack too
rep("  for(const k in inv){ if(inv[k]>0){ items[k] = inv[k]; any = true; } }\n  if(!any) return;",
    "  for(const k in inv){ if(inv[k]>0){ items[k] = inv[k]; any = true; } }\n  const worn = armor.slice(); if(worn.some(a=>a)) any = true;\n  if(!any) return;")
rep("  deathSacks.push({ x:player.x, y, z:player.z, items, wear:w, day:dayNo });\n  for(const k in inv) delete inv[k];",
    "  deathSacks.push({ x:player.x, y, z:player.z, items, wear:w, armor:worn, day:dayNo });\n  armor = [null,null,null,null];\n  for(const k in inv) delete inv[k];")
rep("    for(const k in s.wear){ wear[k] = (wear[k]||[]).concat(s.wear[k]); }", "    for(const k in s.wear){ wear[k] = (wear[k]||[]).concat(s.wear[k]); }\n    if(s.armor) s.armor.forEach((a,k)=>{ if(!a) return; if(!armor[k]) armor[k] = a; else unequipTo(a); });")
# save / load
rep("gold, cls:playerClass,", "gold, armor, cls:playerClass,")
rep("  gold = meta.gold || 0; playerClass", "  armor = Array.isArray(meta.armor) ? meta.armor.slice(0,4) : [null,null,null,null]; while(armor.length<4) armor.push(null);\n  gold = meta.gold || 0; playerClass")
# ---------- seen on your character ----------
rep("function plPrep(){\n  const hid = IS_WORKER ? wkHeld : (inv[HOTBAR[sel]]>0 ? HOTBAR[sel] : 0);\n  const key = JSON.stringify(CHAR)+'|'+hid;\n  if(key!==plKey){\n    plKey = key; PLM = bodyModel(CHAR);",
"""// your character as others would see you: worn armor recolours the shirt, trousers and shoes (leather takes its dye)
function hexOf(c){ return '#'+c.map(v=>Math.max(0,Math.min(255,v|0)).toString(16).padStart(2,'0')).join(''); }
function dressedChar(){
  if(IS_WORKER || !armor.some(a=>a)) return CHAR;
  const ch = Object.assign({}, CHAR), col = a => hexOf(ARMOR[a.id].m===0 && a.dye>=0 ? scaleC(DYE_COL[a.dye],0.85) : ARMOR_MATS[ARMOR[a.id].m].col);
  if(armor[1]){ ch.topCol = col(armor[1]); ch.topTrim = hexOf(scaleC(ARMOR_MATS[ARMOR[armor[1].id].m].col,0.7)); }
  if(armor[2]){ ch.legsCol = col(armor[2]); ch.legsTrim = hexOf(scaleC(ARMOR_MATS[ARMOR[armor[2].id].m].col,0.7)); }
  if(armor[3]){ ch.feetCol = col(armor[3]); ch.feetTrim = hexOf(scaleC(ARMOR_MATS[ARMOR[armor[3].id].m].col,0.7)); }
  if(armor[0]){ ch.hairCol = col(armor[0]); }                    // a helm: the hair takes its colour, like a close-fitting coif
  return ch;
}
function plPrep(){
  const hid = IS_WORKER ? wkHeld : (inv[HOTBAR[sel]]>0 ? HOTBAR[sel] : 0);
  const CH = dressedChar(), key = JSON.stringify(CH)+'|'+hid;
  if(key!==plKey){
    plKey = key; PLM = bodyModel(CH);""")
rep("charKey:JSON.stringify(CHAR),", "charKey:JSON.stringify(dressedChar()),")
# ---------- icons ----------
rep("    case IRON_INGOT: case ADAM_INGOT: case MITH_INGOT: paintIcon(g,(P,E)=>{",
"""    default: if(ARMOR[id]){ const A = ARMOR[id], c = ARMOR_MATS[A.m].col, lt = scaleC(c,1.22), dk = scaleC(c,0.6), o = [40,32,28];
      paintIcon(g,(P,E)=>{
        const fill = (rows)=>rows.forEach((r,y)=>{ for(let x=0;x<16;x++){ const ch = r[x]; if(ch==='#') P(x,y+1,o); else if(ch==='a') P(x,y+1,lt); else if(ch==='b') P(x,y+1,c); else if(ch==='c') P(x,y+1,dk); } });
        if(A.k===0) fill(['....######......','...#aaaabb#.....','..#aabbbbbc#....','..#abbbbbbc#....','..#bbbbbbbc#....','..#bb####bc#....','..#bc#..#cc#....','..##.....##.....'].map(r=>'  '+r));
        else if(A.k===1) fill(['...##....##.....','..#ab#..#bc#....','.#aabb##bbcc#...','.#abbbbbbbbc#...','.#abbbbbbbbc#...','..#abbbbbbc#....','..#abbbbbbc#....','..#bbbbbbbc#....','..#bbbbbbcc#....','...#bbbbbc#.....','...########.....'].map(r=>' '+r));
        else if(A.k===2) fill(['..##########....','..#abbbbbbc#....','..#abbbbbbc#....','..#abbc#abbc#...','..#abc#.#abc#...','..#abc#.#abc#...','..#abc#.#abc#...','..#bbc#.#bbc#...','..#bcc#.#bcc#...','..#####.#####...'].map(r=>' '+r));
        else fill(['..####..####....','..#ab#..#ab#....','..#ab#..#ab#....','..#bb#..#bb#....','.#abbc##abbc#...','.#bbbcc#bbbcc#..','.#############..'].map(r=>'  '+r));
      }); return true; }
      break;
    case IRON_INGOT: case ADAM_INGOT: case MITH_INGOT: paintIcon(g,(P,E)=>{""")
# ---------- economy ----------
rep("  P(LEATHER, 12);", "  ARMOR_MATS.forEach((M,m)=>[5,8,7,4].forEach((n,k)=>{ PRICE[AR(m,k)] = Math.round((PRICE[M.mat]||10)*n*1.3 + 10); }));\n  P(LEATHER, 12);")
rep("IRON_PICK, IRON_AXE, IRON_SHOVEL, IRON_SWORD, IRON_INGOT, BARS0,", "IRON_PICK, IRON_AXE, IRON_SHOVEL, IRON_SWORD, IRON_INGOT, AR(0,0), AR(0,1), AR(0,2), AR(0,3), AR(2,0), AR(2,1), AR(2,2), AR(2,3), BARS0,")
rep("  add('BEAST DROPS + MEAT',", "  add('ARMOR', Object.keys(ARMOR).map(Number));\n  add('BEAST DROPS + MEAT',")
rep("SHORT[GOLD]='gold';", "for(const id in ARMOR){ const A = ARMOR[id]; SHORT[id] = ['lea.','chi.','iron','adam','mith'][A.m]+['helm','body','legs','boots'][A.k]; }\nSHORT[GOLD]='gold';")
# ---------- the GEAR tab on the character sheet ----------
rep("[['skills','SKILLS'],['quests','QUESTS'+(quests.length?' ('+quests.length+')':'')],['standing','STANDING']]",
    "[['skills','SKILLS'],['gear','GEAR'],['quests','QUESTS'+(quests.length?' ('+quests.length+')':'')],['standing','STANDING']]")
rep("  } else {\n    const [qh, sh] = questSheetParts();",
"""  } else if(sheetTab==='gear'){
    h += `<div class="skNote" style="color:#b8ae94">Armor ${armorPoints()} \\u00b7 turns away ${Math.round(armorCut()*100)}% of every blow. Armor can't stop falls, hunger, drowning or fire.</div>`;
    for(let k=0;k<4;k++){
      const a = armor[k], A = a && ARMOR[a.id];
      h += `<div class="skRow"><div class="skHead"><b>${['Head','Chest','Legs','Feet'][k]}</b><span>${a ? '+'+A.pts : ''}</span></div>`;
      if(a){
        h += `<div class="tkRow"><span class="tkIc" data-ic="${a.id}"></span><span class="tkNm">${NAMES[a.id]}${a.dye>=0 ? ' ('+NAMES[DYE0+a.dye]+')' : ''}</span><button data-unequip="${k}">TAKE OFF</button></div><div class="skBar thin"><i style="width:${a.dur/A.dur*100}%"></i></div>`;
        if(A.m===0){ const dyes = []; for(let d=0;d<11;d++) if(inv[DYE0+d]>0) dyes.push(d);
          if(dyes.length) h += `<div class="tkBtns" style="margin-top:4px">${dyes.map(d=>`<button data-dye="${k},${d}" style="border-left:8px solid ${hexOf(DYE_COL[d])}">${NAMES[DYE0+d].replace(' dye','')}</button>`).join('')}</div>`;
          else h += `<div class="skDesc">Carry dye to colour leather.</div>`; }
      } else h += `<div class="skDesc">nothing</div>`;
      const spare = Object.keys(inv).map(Number).filter(id=>ARMOR[id] && ARMOR[id].k===k && inv[id]>0);
      for(const id of spare) h += `<div class="tkRow"><span class="tkIc" data-ic="${id}"></span><span class="tkNm">${NAMES[id]} \\u00d7${inv[id]} <small style="color:#8f8a7a">+${ARMOR[id].pts}</small></span><button data-wear="${id}">WEAR</button></div>`;
      h += `</div>`;
    }
  } else {
    const [qh, sh] = questSheetParts();""")
rep("  document.getElementById('skillList').innerHTML = h;\n}\nfunction openSheet(tab){",
    "  const el = document.getElementById('skillList'); el.innerHTML = h;\n  el.querySelectorAll('[data-ic]').forEach(sp=>sp.appendChild(iconCanvas(+sp.dataset.ic)));\n}\nfunction openSheet(tab){")
rep("document.getElementById('skillList').addEventListener('click', e=>{ const b = e.target.closest('[data-tab]'); if(b){ sheetTab = b.dataset.tab; renderSheet(); } });",
"""document.getElementById('skillList').addEventListener('click', e=>{
  const b = e.target.closest('button'); if(!b) return;
  if(b.dataset.tab){ sheetTab = b.dataset.tab; }
  else if(b.dataset.wear) equipArmor(+b.dataset.wear);
  else if(b.dataset.unequip) unequipArmor(+b.dataset.unequip);
  else if(b.dataset.dye){ const [k,d] = b.dataset.dye.split(',').map(Number); dyeArmor(k,d); }
  renderSheet(); });""")
rep("  .shTabs { display:flex; gap:4px; margin:4px 0 8px; }", "  #skillList .tkRow button, #skillList .tkBtns button { font:11px monospace; padding:5px 8px; background:linear-gradient(#34372f,#1d1f1a); color:#e3cf95; border:2px solid #050605; box-shadow:inset 0 0 0 1px #8c7640; }\n  #skillList .tkBtns { display:flex; flex-wrap:wrap; gap:4px; }\n  .shTabs { display:flex; gap:4px; margin:4px 0 8px; }")
open(p,'w').write(s); print('ok')
