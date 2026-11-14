p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# --- module ---
rep("let dead = false, fallPeakY = 0, safeT = 2, vitalT = 0, starveT = 0;\n", r'''let dead = false, fallPeakY = 0, safeT = 2, vitalT = 0, starveT = 0;
// ---------- skills and levels (Daggerfall's idea, kept simple): you get better at what you actually do ----------
// Five skills, 5 to 100. Each use counts toward the next point; higher skills need more uses. Every skill point gained also counts
// toward your level, and levels add hearts. Skills never lock anything away: anyone can do anything, they just get better at it.
const SKILLS = [
  { id:'weapons',   name:'Weapons',      base:6, desc:'damage with swords, axes, tools, pistols and crossbows' },
  { id:'unarmed',   name:'Hand-to-Hand', base:5, desc:'damage with your bare fists' },
  { id:'magic',     name:'Magic',        base:3, desc:'spell damage, and a chance a cast costs no charge' },
  { id:'athletics', name:'Athletics',    base:8, desc:'running and swimming speed' },
  { id:'stealth',   name:'Stealth',      base:5, desc:'while sneaking, creatures notice you later' }
];
const SKILL_START = 5, LEVEL_MAX = 30;
let skills = {}, skillUses = {}, skillGained = 0, athDist = 0, stealthT = 0;
function resetSkills(){ for(const k of SKILLS){ skills[k.id] = SKILL_START; skillUses[k.id] = 0; } skillGained = 0; }
resetSkills();
function playerLevel(){ return Math.min(LEVEL_MAX, 1 + Math.floor((skillGained+4)/12)); }          // the first level comes after 8 points, then every 12
function maxHP(){ return Math.min(40, 20 + 2*Math.floor((playerLevel()-1)/2)); }                   // a heart every other level, up to 20 hearts
function skillUsesFor(id){ const K = SKILLS.find(k=>k.id===id); return Math.round(K.base*(1+Math.floor(skills[id]/15)*0.6)); }
function skillMul(id){ return 1 + skills[id]/100; }
function stealthMul(){ return sneaking ? Math.max(0.2, 0.6 - skills.stealth/250) : 1; }
let skillToastT = 0;
function skillToast(html, big){
  const el = document.getElementById('skillToast'); if(!el) return;
  el.innerHTML = html; el.className = big ? 'show big' : 'show'; clearTimeout(skillToastT);
  skillToastT = setTimeout(()=>{ el.className = ''; }, big ? 3200 : 1800);
}
function trainSkill(id, n){
  if(dead || skills[id]>=100) return;
  skillUses[id] += (n===undefined ? 1 : n);
  let up = false;
  while(skills[id]<100 && skillUses[id] >= skillUsesFor(id)){ skillUses[id] -= skillUsesFor(id); skills[id]++; skillGained++; up = true;
    const L0 = Math.min(LEVEL_MAX, 1 + Math.floor((skillGained-1+4)/12)), hp0 = maxHP(), L = playerLevel();
    if(L>L0){ const hp = Math.min(40, 20 + 2*Math.floor((L0-1)/2)); if(maxHP()>hp) health = Math.min(maxHP(), health+2); vitalKey = '';
      skillToast('LEVEL '+L+(maxHP()>hp ? '<br><small>+1 heart</small>' : ''), true); }
    else skillToast(SKILLS.find(k=>k.id===id).name+' '+skills[id]);
  }
  if(up){ scheduleSave(); if(document.getElementById('skillMenu').classList.contains('show')) renderSkills(); }
}
function renderSkills(){
  const L = playerLevel(), cur = Math.max(0,(L-1)*12-4), nxt = L*12-4, frac = L>=LEVEL_MAX ? 1 : Math.max(0,Math.min(1,(skillGained-cur)/(nxt-cur)));
  let h = `<div class="skLvl">LEVEL ${L}<span>${maxHP()/2} hearts</span></div><div class="skBar"><i style="width:${frac*100}%"></i></div>`;
  h += `<div class="skNote">${L>=LEVEL_MAX ? 'highest level' : (nxt-skillGained)+' more skill points to level '+(L+1)}</div>`;
  for(const k of SKILLS){
    const v = skills[k.id], f = v>=100 ? 1 : skillUses[k.id]/skillUsesFor(k.id);
    h += `<div class="skRow"><div class="skHead"><b>${k.name}</b><span>${v}</span></div><div class="skBar"><i style="width:${v}%"></i></div><div class="skBar thin"><i style="width:${f*100}%"></i></div><div class="skDesc">${k.desc}</div></div>`;
  }
  document.getElementById('skillList').innerHTML = h;
}
function openSkills(){ renderSkills(); document.getElementById('skillMenu').classList.add('show'); }
function closeSkills(){ document.getElementById('skillMenu').classList.remove('show'); }
// running, swimming and jumping train Athletics; sneaking near a creature that hasn't noticed you trains Stealth
function skillMoveTick(dist, jumped){
  if((running || bodyInWater) && dist>0){ athDist += dist; if(athDist>=24){ athDist -= 24; trainSkill('athletics'); } }
  if(jumped) trainSkill('athletics', 0.15);
  stealthT -= frameScale/60;
  if(sneaking && stealthT<=0){
    stealthT = 2;
    for(const m of mobs){ if(m.dead) continue; const calm = BEAST[m.kind] ? m.angry<=0 : IS_BRUTE(m.kind) ? !m.hostile : false;
      if(calm && Math.hypot(m.x-player.x,m.z-player.z)<16 && Math.abs(m.y-player.y)<6){ trainSkill('stealth'); break; } }
  }
}
''')
# --- hooks: damage and training ---
rep("    return base + (T.tier-1);\n  }\n  return 1;\n}", "    return (base + (T.tier-1))*skillMul('weapons');\n  }\n  return 1 + skills.unarmed/20;              // a fist: 1.25 at the start, 6 at mastery\n}")
rep("      mobHit(mh.m, playerAttackDamage() + swordSpellHit(mh.m)); crack = null; return;",
    "      { const armed = !!(TOOLS[HOTBAR[sel]] && inv[HOTBAR[sel]]>0); mobHit(mh.m, playerAttackDamage() + swordSpellHit(mh.m)); trainSkill(armed ? 'weapons' : 'unarmed'); } crack = null; return;")
rep("    if(mh && mh.m.kind) spellDamage(mh.m, G.dmg);", "    if(mh && mh.m.kind){ spellDamage(mh.m, G.dmg*skillMul('weapons')); trainSkill('weapons'); }")
rep("        if(hitM) spellDamage(hitM, e.dmg);", "        if(hitM){ spellDamage(hitM, e.dmg*skillMul('weapons')); trainSkill('weapons'); }")
rep("spellDamage(cur, SPELL_DMG.bolt);", "spellDamage(cur, SPELL_DMG.bolt*skillMul('magic'));")
rep("spellDamage(best, SPELL_DMG.boltChain)", "spellDamage(best, SPELL_DMG.boltChain*skillMul('magic'))")
rep("spellDamage(m, SPELL_DMG.fire);", "spellDamage(m, SPELL_DMG.fire*skillMul('magic'));")
rep("spellDamage(m, SPELL_DMG.fireSplash)", "spellDamage(m, SPELL_DMG.fireSplash*skillMul('magic'))")
rep("  return s==='fire' ? SPELL_DMG.swordFire : SPELL_DMG.swordBolt;", "  return (s==='fire' ? SPELL_DMG.swordFire : SPELL_DMG.swordBolt)*skillMul('magic');")
rep("function spendCast(){\n  spellCharges--;", "function spendCast(){\n  trainSkill('magic');\n  if(Math.random() < skills.magic/300){ spellHud(); scheduleSave(); return; }      // a practised caster sometimes keeps the charge\n  spellCharges--;")
rep("  const speed = (running ? 0.1 : 0.075) * (sneaking && onGroundLast ? 0.3 : 1) * frameScale;",
    "  const speed = (running ? 0.1 : 0.075) * (sneaking && onGroundLast ? 0.3 : 1) * (1 + skills.athletics/500) * frameScale;     // Athletics: up to 20% faster")
rep("  survivalTick(Math.hypot(mx,mz), jumped);", "  survivalTick(Math.hypot(mx,mz), jumped); skillMoveTick(Math.hypot(mx,mz), jumped);")
rep("  else if(m.angry<=0 && dist<K.aggro && Math.abs(dyp)<4) m.angry = K.memory;", "  else if(m.angry<=0 && dist<K.aggro*stealthMul() && Math.abs(dyp)<4) m.angry = K.memory;")
rep("  if(!m.hostile && !dead && dist<K.aggro && dy<5) m.hostile = true;", "  if(!m.hostile && !dead && dist<K.aggro*stealthMul() && dy<5) m.hostile = true;")
# --- max health ---
rep("  if(food >= 18 && health < 20 && health > 0){", "  if(food >= 18 && health < maxHP() && health > 0){")
rep("  health = 20; food = 20; saturation = 5; exhaustion = 0; starveT = 0; vitalT = 0;", "  health = maxHP(); food = 20; saturation = 5; exhaustion = 0; starveT = 0; vitalT = 0;")
rep("  health = (meta.health === undefined ? 20 : meta.health);",
    "  resetSkills(); if(meta.skills){ Object.assign(skills, meta.skills.v||{}); Object.assign(skillUses, meta.skills.u||{}); skillGained = meta.skills.g||0; }\n  health = (meta.health === undefined ? maxHP() : meta.health);")
rep("tod, health, food, saturation, bed: bedSpawn,", "tod, health, food, saturation, skills:{ v:skills, u:skillUses, g:skillGained }, bed: bedSpawn,")
rep("""  const key = health + ',' + food;
  if(key === vitalKey) return;
  vitalKey = key;
  for(let i=0;i<10;i++){
    const h = Math.max(0, Math.min(2, health - i*2));     // 0 empty, 1 half, 2 full
    const f = Math.max(0, Math.min(2, food - i*2));
    // hearts fill from the left; food fills from the right, like Minecraft
    heartEls[i].style.backgroundImage = VITAL_URLS.heart[h];
    foodEls[9-i].style.backgroundImage = VITAL_URLS.food[f];
  }""", """  const mh = maxHP(), key = health + ',' + food + ',' + mh;
  if(key === vitalKey) return;
  vitalKey = key;
  for(let i=0;i<20;i++){                                   // levels add hearts: past ten they start a second row above
    heartEls[i].style.display = i*2 < mh ? 'block' : 'none';
    heartEls[i].style.backgroundImage = VITAL_URLS.heart[Math.max(0, Math.min(2, health - i*2))];     // 0 empty, 1 half, 2 full
  }
  for(let i=0;i<10;i++){
    const f = Math.max(0, Math.min(2, food - i*2));
    foodEls[9-i].style.backgroundImage = VITAL_URLS.food[f];      // food fills from the right, like Minecraft
  }""")
rep("""for(let i=0;i<10;i++){
  for(const [arr,id] of [[heartEls,'hearts'],[foodEls,'food']]){""", """for(let i=0;i<20;i++){
  for(const [arr,id] of (i<10 ? [[heartEls,'hearts'],[foodEls,'food']] : [[heartEls,'hearts']])){""")
rep("  #hearts, #food { display:flex; gap:1px; }", "  #hearts, #food { display:flex; gap:1px; }\n  #hearts { flex-wrap:wrap-reverse; width:170px; align-content:flex-start; }")
# --- UI ---
rep('    <button id="charBtn">CHARACTER</button>', '    <button id="charBtn">CHARACTER</button>\n    <button id="skillBtn">SKILLS</button>')
rep('<div id="gpHint"></div><div id="gpCursor"></div>', '''<div id="skillMenu"><div id="skillPanel"><div id="skillTop"><h2>Skills</h2><button id="skillClose">DONE</button></div><div id="skillList"></div></div></div>
<div id="skillToast"></div>
<div id="gpHint"></div><div id="gpCursor"></div>''')
rep("  #charMenu.show { display:flex; }", """  #charMenu.show { display:flex; }
  #skillMenu { position:fixed; inset:0; z-index:21; display:none; align-items:center; justify-content:center; color:#d8cfb8; font-family:monospace; background:rgba(0,0,0,.92); }
  #skillMenu.show { display:flex; }
  #skillPanel { width:min(94vw,460px); max-height:92vh; overflow-y:auto; padding:12px 14px; box-sizing:border-box; background:linear-gradient(#1b1d18,#0f100e); border:2px solid #050605; box-shadow:inset 0 0 0 1px #8c7640, 0 0 24px #000; }
  #skillTop { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
  #skillTop h2 { margin:0; color:#e3cf95; letter-spacing:3px; font-size:18px; }
  #skillClose { font:13px monospace; letter-spacing:2px; padding:8px 16px; background:linear-gradient(#34372f,#1d1f1a); color:#e3cf95; border:2px solid #050605; box-shadow:inset 0 0 0 1px #8c7640; }
  .skLvl { display:flex; justify-content:space-between; align-items:baseline; color:#e3cf95; font-size:16px; letter-spacing:2px; }
  .skLvl span { font-size:12px; color:#d63a34; letter-spacing:0; }
  .skNote { font-size:11px; color:#8f8a7a; margin:3px 0 10px; }
  .skBar { height:8px; background:#0a0b09; border:1px solid #3a3d35; margin-top:3px; }
  .skBar i { display:block; height:100%; background:linear-gradient(#e3cf95,#9c7f3c); }
  .skBar.thin { height:3px; border-color:#24261f; } .skBar.thin i { background:#6aa0c8; }
  .skRow { padding:8px 0; border-top:1px solid #2a2c26; }
  .skHead { display:flex; justify-content:space-between; font-size:14px; } .skHead span { color:#e3cf95; }
  .skDesc { font-size:11px; color:#8f8a7a; margin-top:4px; }
  #skillToast { position:fixed; left:50%; top:18%; transform:translateX(-50%); z-index:6; pointer-events:none; font:bold 14px monospace; letter-spacing:2px; color:#e3cf95;
    text-shadow:0 0 4px #000, 2px 2px 0 #000; opacity:0; transition:opacity .4s; text-align:center; }
  #skillToast.show { opacity:1; } #skillToast.big { font-size:22px; } #skillToast small { font-size:13px; color:#ff9a90; }""")
rep("document.getElementById('resumeBtn').addEventListener('click', ()=>{",
    "document.getElementById('skillBtn').addEventListener('click', openSkills);\ndocument.getElementById('skillClose').addEventListener('click', closeSkills);\ndocument.getElementById('resumeBtn').addEventListener('click', ()=>{")
open(p,'w').write(s); print('ok')
