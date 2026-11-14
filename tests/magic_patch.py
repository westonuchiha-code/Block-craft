p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    a2 = a.replace('\\u00b7','\u00b7')
    if s.count(a)!=cnt and s.count(a2)==cnt: a = a2
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# ---------- the spellmaker block ----------
rep("const SIGNPOST = 1131;", "const SIGNPOST = 1131, SPELLMAKER = 1132;")
rep("  // a signpost: a post with a board;", "  NAMES[SPELLMAKER] = 'spellmaker'; COLORS[SPELLMAKER] = [110,96,140];\n  // a signpost: a post with a board;")
rep("    case CARVED: return TILES.carved[yy][tx];", "    case CARVED: return TILES.carved[yy][tx];\n    case SPELLMAKER: return top ? TILES.glow[yy][tx] : bottom ? TILES.carved[yy][tx] : TILES.books[yy][tx];")
rep("S(COAL, 11); S(SIGNPOST, 4);", "S(COAL, 11); S(SIGNPOST, 4); S(SPELLMAKER, 10);")
rep("const KIND = { [SIGNPOST]:'axe', ", "const KIND = { [SIGNPOST]:'axe', [SPELLMAKER]:'pick', ")
rep("const REQ_TIER = { ", "const REQ_TIER = { [SPELLMAKER]:1, ")
rep("  { out:[CUTTER,1],       pat:['SSS','PPP'],           key:{S:STONE, P:PLANKS} },", "  { out:[CUTTER,1],       pat:['SSS','PPP'],           key:{S:STONE, P:PLANKS} },\n  { out:[SPELLMAKER,1],   pat:['CBC','SSS'],           key:{C:CANDLE, B:BOOKSHELF, S:STONE_BRICK} },")
rep("  { name:'Furnace',            out:[FURNACE,1],      ing:{[COBBLE]:8} },", "  { name:'Furnace',            out:[FURNACE,1],      ing:{[COBBLE]:8} },\n  { name:'Spellmaker',         out:[SPELLMAKER,1],   ing:{[CANDLE]:2, [BOOKSHELF]:1, [STONE_BRICK]:3} },")
rep("  if(hit.b === FURNACE){ openCraft(3,'smelt'); return; }", "  if(hit.b === FURNACE){ openCraft(3,'smelt'); return; }\n  if(hit.b === SPELLMAKER){ openSpellmaker(); return; }")
# ---------- magicka, the spellbook ----------
rep("let spell = null, spellCharges = 0, swordSpell = false, castCool = 0, fxClock = 0;", r"""let spell = null, spellCharges = 0, swordSpell = false, castCool = 0, fxClock = 0;
// ---- magicka and the spellbook (Daggerfall's spellmaker, kept simple) ----
// Spells you make at a spellmaker are yours for good. Each cast costs magicka, which refills by itself (faster with a high Magic
// skill). Potions still work as before: while a potion's charges last, F casts the potion's spell.
const SPELL_FX = {
  fire:  { name:'Firebolt',  mat:EMBER,    matN:[1,2,3], mp:[6,10,15], desc:'a ball of fire that bursts on impact' },
  bolt:  { name:'Lightning', mat:GLOWMOSS, matN:[2,4,6], mp:[7,11,16], desc:'a bolt that leaps from foe to foe' },
  heal:  { name:'Heal',      mat:CANDLE,   matN:[1,2,3], mp:[6,11,18], desc:'mends 4 / 8 / 14 health' },
  ward:  { name:'Ward',      mat:CHITIN,   matN:[1,2,3], mp:[8,12,16], desc:'magical armor: +4 / +7 / +10 for 30 / 45 / 60 seconds' },
  swift: { name:'Swiftness', mat:LEATHER,  matN:[1,2,3], mp:[6,9,12],  desc:'run 25 / 40 / 55% faster for 30 seconds' } };
const SPELL_POW = [1, 1.6, 2.2], ROMAN = ['I','II','III'];
let book = [], bookSel = 0, mp = 10, mpT = 0, castPow = 1, wardT = 0, wardPts = 0, swiftT = 0, swiftK = 0;
function mpMax(){ return 10 + Math.floor(skills.magic*0.4) + (isClass('blackmage') ? 10 : isClass('whitemage') ? 6 : 0); }
function mpTick(dt){
  mpT += dt; const per = Math.max(0.8, 4 - skills.magic/35);
  while(mpT>=per){ mpT -= per; if(mp<mpMax()){ mp++; vitalKey = ''; } }
  if(wardT>0){ wardT -= dt; if(wardT<=0){ wardPts = 0; vitalKey = ''; } }
  if(swiftT>0){ swiftT -= dt; if(swiftT<=0) swiftK = 0; }
}
function bookSpell(){ return book[bookSel] || null; }
function bookName(sp){ return SPELL_FX[sp.fx].name+' '+ROMAN[sp.pow]; }
function castBook(){
  const sp = bookSpell(); if(!sp) return false;
  const cost = SPELL_FX[sp.fx].mp[sp.pow];
  if(mp<cost){ skillToast('not enough magicka'); return true; }
  mp -= cost; vitalKey = ''; castCool = 0.45; swingT = 1; trainSkill('magic');
  if(sp.fx==='fire' || sp.fx==='bolt'){ castPow = SPELL_POW[sp.pow]; castEffect(sp.fx); castPow = 1; }
  else if(sp.fx==='heal'){ health = Math.min(maxHP(), health + [4,8,14][sp.pow]*(1+skills.magic/200)); vitalKey = ''; const p = [player.x, player.y+1, player.z]; fx.push({ kind:'boom', x:p[0], y:p[1], z:p[2], age:0, seed:Math.random()*1000, size:0.3 }); }
  else if(sp.fx==='ward'){ wardPts = [4,7,10][sp.pow]; wardT = [30,45,60][sp.pow]; skillToast('warded'); }
  else if(sp.fx==='swift'){ swiftK = [0.25,0.4,0.55][sp.pow]; swiftT = 30; skillToast('swift'); }
  spellHud(); scheduleSave(); return true;
}
// the spellmaker: pick an effect and a strength, pay its reagents and some gold, and the spell is yours
let smFx = 'fire', smPow = 0;
function smCost(){ const F = SPELL_FX[smFx]; return { mat:F.mat, n:F.matN[smPow], gold:30*(smPow+1)*(smPow+1) }; }
function renderSpellmaker(){
  const F = SPELL_FX[smFx], c = smCost(), have = inv[c.mat]||0, known = book.some(b=>b.fx===smFx && b.pow===smPow);
  let h = `<div class="skNote">Make a spell of your own. It costs reagents and gold once; casting it costs magicka. You have ${mp}/${mpMax()} magicka.</div><div class="tkBtns">`;
  for(const k in SPELL_FX) h += `<button data-fx="${k}" class="${k===smFx?'on':''}">${SPELL_FX[k].name.toUpperCase()}</button>`;
  h += `</div><div class="tkBtns" style="margin-top:6px">${ROMAN.map((r,i)=>`<button data-pow="${i}" class="${i===smPow?'on':''}">${r}</button>`).join('')}</div>`;
  h += `<div class="skRow"><div class="skHead"><b>${F.name} ${ROMAN[smPow]}</b><span>${F.mp[smPow]} magicka a cast</span></div><div class="skDesc" style="color:#d8cfb8">${F.desc}</div>`;
  h += `<div class="tkRow"><span class="tkIc" data-ic="${c.mat}"></span><span class="tkNm">${c.n} ${NAMES[c.mat]} <small style="color:${have>=c.n?'#8fbf6a':'#e06050'}">(you have ${have})</small></span><span class="tkPr">${c.gold}g</span></div></div>`;
  h += `<div class="tkBtns"><button data-make="1" ${known || have<c.n || gold<c.gold || book.length>=8 ? 'disabled' : ''}>${known ? 'ALREADY KNOWN' : book.length>=8 ? 'SPELLBOOK FULL' : 'CREATE SPELL'}</button><button data-close="1">DONE</button></div>`;
  const el = document.getElementById('smBody'); el.innerHTML = h; el.querySelectorAll('[data-ic]').forEach(sp=>sp.appendChild(iconCanvas(+sp.dataset.ic)));
}
function openSpellmaker(){ if(paused || craftOpen) return; craftOpen = true; renderSpellmaker(); document.getElementById('smMenu').classList.add('show'); if(document.pointerLockElement) document.exitPointerLock(); }
function closeSpellmaker(){ document.getElementById('smMenu').classList.remove('show'); craftOpen = false; scheduleSave(); }
function smMake(){
  const c = smCost(); if((inv[c.mat]||0)<c.n || gold<c.gold || book.some(b=>b.fx===smFx && b.pow===smPow) || book.length>=8) return;
  inv[c.mat] -= c.n; if(inv[c.mat]<=0) delete inv[c.mat]; gold -= c.gold;
  book.push({ fx:smFx, pow:smPow }); bookSel = book.length-1; trainSkill('magic', 3);
  skillToast(bookName(book[bookSel]).toUpperCase()+'<br><small>added to your spellbook</small>', true); spellHud(); renderSpellmaker(); scheduleSave();
}""")
# casting entry: potion first, then the book; split the effect out
rep("""function castSpell(){
  if(dead || paused || craftOpen || !currentWorld || !spell || spellCharges<=0 || castCool>0) return;
  const id = HOTBAR[sel], T = TOOLS[id];
  if(T && T.kind==='sword' && inv[id]>0){ if(!swordSpell){ swordSpell = true; swingT = 1; spellHud(); scheduleSave(); } return; }
  castCool = 0.4; swingT = 1;""", """function castSpell(){
  if(dead || paused || craftOpen || !currentWorld || castCool>0) return;
  if(!spell || spellCharges<=0){ castBook(); return; }                    // no potion running: cast from your spellbook
  const id = HOTBAR[sel], T = TOOLS[id];
  if(T && T.kind==='sword' && inv[id]>0){ if(!swordSpell){ swordSpell = true; swingT = 1; spellHud(); scheduleSave(); } return; }
  castCool = 0.4; swingT = 1;
  castEffect(spell);
  spendCast();
}
function castEffect(kind){""")
rep("""  if(spell==='fire'){
    const dx = aim[0]-hand[0], dy = aim[1]-hand[1], dz = aim[2]-hand[2], d = Math.hypot(dx,dy,dz)||1;
    fx.push({ kind:'ball', x:hand[0], y:hand[1], z:hand[2], vx:dx/d*20, vy:dy/d*20, vz:dz/d*20, age:0, trail:[] });""",
"""  if(kind==='fire'){
    const dx = aim[0]-hand[0], dy = aim[1]-hand[1], dz = aim[2]-hand[2], d = Math.hypot(dx,dy,dz)||1;
    fx.push({ kind:'ball', x:hand[0], y:hand[1], z:hand[2], vx:dx/d*20, vy:dy/d*20, vz:dz/d*20, age:0, trail:[], pow:castPow });""")
rep("    fx.push({ kind:'bolt', pts, age:0, hand:true });\n  }\n  spendCast();\n}", "    fx.push({ kind:'bolt', pts, age:0, hand:true });\n  }\n}")
rep("spellDamage(cur, SPELL_DMG.bolt*skillMul('magic'));", "spellDamage(cur, SPELL_DMG.bolt*skillMul('magic')*castPow);")
rep("spellDamage(best, SPELL_DMG.boltChain*skillMul('magic'));", "spellDamage(best, SPELL_DMG.boltChain*skillMul('magic')*castPow);")
rep("    if(m===direct) spellDamage(m, SPELL_DMG.fire*skillMul('magic'));\n    else if(Math.hypot(p[0]-b.x, p[1]-b.y, p[2]-b.z) < 2.6) spellDamage(m, SPELL_DMG.fireSplash*skillMul('magic'));",
    "    if(m===direct) spellDamage(m, SPELL_DMG.fire*skillMul('magic')*(b.pow||1));\n    else if(Math.hypot(p[0]-b.x, p[1]-b.y, p[2]-b.z) < 2.6) spellDamage(m, SPELL_DMG.fireSplash*skillMul('magic')*(b.pow||1));")
# HUD: the spell readout shows the book spell when no potion is running
rep("""  if(!spell || spellCharges<=0){ el.style.display = 'none'; return; }""", """  if(!spell || spellCharges<=0){ const sp = bookSpell();
    if(!sp){ el.style.display = 'none'; return; }
    el.style.display = 'block'; el.className = sp.fx==='fire' ? 'fire' : sp.fx==='bolt' ? 'bolt' : 'book'; el.textContent = bookName(sp).toUpperCase()+' \\u00b7 '+SPELL_FX[sp.fx].mp[sp.pow]+' MP'; return; }""")
rep("  document.getElementById('hudStat').innerHTML = `LV ${playerLevel()} \\u00b7 <b>${gold}g</b>`;", "  document.getElementById('hudStat').innerHTML = `LV ${playerLevel()} \\u00b7 <b>${gold}g</b> \\u00b7 <span style=\"color:#7ab4f0\">${mp}/${mpMax()} MP</span>`;")
rep("  const mh = maxHP(), key = health + ',' + food + ',' + mh + ',' + gold + ',' + skillGained;", "  const mh = maxHP(), key = health + ',' + food + ',' + mh + ',' + gold + ',' + skillGained + ',' + mp;")
rep("#spellHud { position:absolute;", "#spellHud.book { color:#c8a8ff; border-color:#8a6ad0; }\n#spellHud { position:absolute;")
# ward and swiftness take effect
rep("function armorPoints(){ let p = 0; for(const a of armor) if(a) p += ARMOR[a.id].pts; return p; }", "function armorPoints(){ let p = wardPts; for(const a of armor) if(a) p += ARMOR[a.id].pts; return p; }")
rep("  if(!pure && armorPoints()>0){ points = Math.max(0.5, Math.round(points*(1-armorCut())*2)/2); armorWear(); }", "  if(!pure && armorPoints()>0){ points = Math.max(0.5, Math.round(points*(1-armorCut())*2)/2); if(armor.some(a=>a)) armorWear(); }")
rep("* (1 + skills.athletics/500) * frameScale;", "* (1 + skills.athletics/500) * (1 + swiftK) * frameScale;")
# tick magicka in the frame (in updateMobs, which runs every frame)
rep("function updateMobs(){\n  const dt = frameScale/60;", "function updateMobs(){\n  const dt = frameScale/60;\n  mpTick(dt);")
# G picks the next spell
rep("  if(e.code==='KeyF' && !e.repeat) castSpell();", "  if(e.code==='KeyF' && !e.repeat) castSpell();\n  if(e.code==='KeyG' && !e.repeat && book.length){ bookSel = (bookSel+1)%book.length; spellHud(); skillToast(bookName(book[bookSel])); }")
# MAGIC tab on the character sheet
rep("[['skills','SKILLS'],['gear','GEAR'],", "[['skills','SKILLS'],['gear','GEAR'],['magic','MAGIC'],")
rep("  } else if(sheetTab==='gear'){", """  } else if(sheetTab==='magic'){
    h += `<div class="skNote" style="color:#b8ae94">Magicka ${mp}/${mpMax()} \\u00b7 refills one every ${Math.max(0.8, 4 - skills.magic/35).toFixed(1)}s. Cast your chosen spell with F (Y on a controller); G picks the next one. A potion's charges are used first.</div>`;
    if(!book.length) h += `<div class="skNote">Your spellbook is empty. Build a spellmaker (2 candles, a bookshelf, 3 stone bricks) and make your first spell there.</div>`;
    book.forEach((sp,i)=>{ const F = SPELL_FX[sp.fx];
      h += `<div class="skRow"><div class="skHead"><b>${bookName(sp)}</b><span>${F.mp[sp.pow]} MP</span></div><div class="skDesc">${F.desc}</div>${i===bookSel ? '<div class="skDesc" style="color:#8fbf6a">ready to cast</div>' : `<div class="tkBtns"><button data-spell="${i}">CHOOSE</button></div>`}</div>`; });
  } else if(sheetTab==='gear'){""")
rep("  else if(b.dataset.wear) equipArmor(+b.dataset.wear);", "  else if(b.dataset.spell){ bookSel = +b.dataset.spell; spellHud(); }\n  else if(b.dataset.wear) equipArmor(+b.dataset.wear);")
rep(".shTabs button { flex:1; font:12px monospace; letter-spacing:1px; padding:7px 4px;", ".shTabs button { flex:1; font:11px monospace; letter-spacing:0; padding:7px 2px;")
# spellmaker UI
rep('<div id="skillToast"></div>', '<div id="smMenu"><div id="smPanel" class="tkPanelX"><div id="skillTop"><h2>Spellmaker</h2></div><div id="smBody"></div></div></div>\n<div id="skillToast"></div>')
rep("  #skillMenu.show { display:flex; }", """  #skillMenu.show { display:flex; }
  #smMenu { position:fixed; inset:0; z-index:21; display:none; align-items:center; justify-content:center; color:#d8cfb8; font-family:monospace; background:rgba(0,0,0,.85); }
  #smMenu.show { display:flex; }
  #smPanel { width:min(94vw,470px); max-height:92vh; overflow-y:auto; padding:12px 14px; box-sizing:border-box; background:linear-gradient(#1d1a24,#100e14); border:2px solid #050605; box-shadow:inset 0 0 0 1px #8a6ad0, 0 0 24px #000; }
  #smPanel h2 { margin:0 0 6px; color:#c8a8ff; letter-spacing:3px; font-size:18px; }
  #smBody .tkBtns { display:flex; flex-wrap:wrap; gap:5px; } #smBody button { font:11px monospace; padding:6px 9px; background:linear-gradient(#34303f,#1d1a24); color:#e3d8ff; border:2px solid #050605; box-shadow:inset 0 0 0 1px #6a5aa0; }
  #smBody button.on { box-shadow:inset 0 0 0 2px #c8a8ff; } #smBody button:disabled { opacity:.35; }
  #smBody .skRow { margin-top:8px; }""")
rep("document.getElementById('skillBtn').addEventListener('click', openSkills);", """document.getElementById('skillBtn').addEventListener('click', openSkills);
document.getElementById('smBody').addEventListener('click', e=>{ const b = e.target.closest('button'); if(!b || b.disabled) return;
  if(b.dataset.fx){ smFx = b.dataset.fx; } else if(b.dataset.pow){ smPow = +b.dataset.pow; } else if(b.dataset.make){ smMake(); return; } else if(b.dataset.close){ closeSpellmaker(); return; }
  renderSpellmaker(); });""")
rep("function closeCraft(){\n  if(document.getElementById('mapMenu')", "function closeCraft(){\n  if(document.getElementById('smMenu').classList.contains('show')){ closeSpellmaker(); return; }\n  if(document.getElementById('mapMenu')")
# economy: the scholar sells a spellmaker
rep("  librarian:  { title:'Scholar\\'s wares', sell:[BOOKSHELF, CANDLE,", "  librarian:  { title:'Scholar\\'s wares', sell:[SPELLMAKER, BOOKSHELF, CANDLE,")
rep("  P(LEATHER, 12);", "  P(SPELLMAKER, 120);\n  P(LEATHER, 12);")
# save / load
rep("gold, armor, crypts:cryptState,", "gold, armor, book, bookSel, mp, crypts:cryptState,")
rep("  cryptState = meta.crypts || {};", "  book = meta.book || []; bookSel = meta.bookSel || 0; mp = meta.mp===undefined ? 10 : meta.mp; wardT = wardPts = swiftT = swiftK = 0;\n  cryptState = meta.crypts || {};")
rep("  add('ARMOR', Object.keys(ARMOR).map(Number));", "  add('ARMOR', Object.keys(ARMOR).map(Number));\n  add('MAGIC', [SPELLMAKER, EMBER, GLOWMOSS, CANDLE, CHITIN, LEATHER]);")
open(p,'w').write(s); print('ok')
