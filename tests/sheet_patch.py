p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# --- one character sheet with tabs ---
i=s.index("function renderSkills(){"); j=s.index("// running, swimming and jumping train Athletics")
s=s[:i]+r'''// ---------- the character sheet: one place for who you are (class, level, skills), what you're doing (quests) and where you stand ----------
let sheetTab = 'skills', sheetPaused = false;
function renderSkills(){ renderSheet(); }
function renderSheet(){
  const L = playerLevel(), cur = Math.max(0,(L-1)*12-4), nxt = L*12-4, frac = L>=LEVEL_MAX ? 1 : Math.max(0,Math.min(1,(skillGained-cur)/(nxt-cur)));
  const c = cls();
  let h = `<div class="skLvl">${c ? c.name.toUpperCase()+' · ' : ''}LEVEL ${L}<span>${maxHP()/2} hearts &nbsp;<b style="color:#ecc440">${gold} gold</b></span></div><div class="skBar"><i style="width:${frac*100}%"></i></div>`;
  h += `<div class="skNote">${L>=LEVEL_MAX ? 'highest level' : (nxt-skillGained)+' more skill points to level '+(L+1)} · day ${dayNo+1}</div>`;
  h += `<div class="shTabs">${[['skills','SKILLS'],['quests','QUESTS'+(quests.length?' ('+quests.length+')':'')],['standing','STANDING']].map(([t,n])=>`<button data-tab="${t}" class="${sheetTab===t?'on':''}">${n}</button>`).join('')}</div>`;
  if(sheetTab==='skills'){
    if(c) h += `<div class="skNote" style="color:#b8ae94">${c.perk} ★ skills are learned faster.</div>`;
    for(const k of SKILLS){
      const v = skills[k.id], f = v>=100 ? 1 : skillUses[k.id]/skillUsesFor(k.id);
      h += `<div class="skRow"><div class="skHead"><b>${k.name}${c && c.fav.includes(k.id) ? ' <small style="color:#8fbf6a">★</small>' : ''}</b><span>${v}</span></div><div class="skBar"><i style="width:${v}%"></i></div><div class="skBar thin"><i style="width:${f*100}%"></i></div><div class="skDesc">${k.desc}</div></div>`;
    }
  } else {
    const [qh, sh] = questSheetParts();
    h += sheetTab==='quests' ? qh : (sh || '<div class="skNote">No village knows you yet. Their opinion of you changes with the work you do for them, and with how you treat their people.</div>');
  }
  document.getElementById('skillList').innerHTML = h;
}
function openSheet(tab){
  sheetTab = tab || sheetTab; renderSheet();
  document.getElementById('skillMenu').classList.add('show');
  if(!paused && !craftOpen){ craftOpen = true; sheetPaused = true; if(document.pointerLockElement) document.exitPointerLock(); }
}
function openSkills(){ openSheet('skills'); }
function closeSkills(){ document.getElementById('skillMenu').classList.remove('show'); if(sheetPaused){ craftOpen = false; sheetPaused = false; } }
'''+s[j:]
rep("  document.getElementById('questList').innerHTML = h;\n}\nfunction openQuests(){ renderQuests(); document.getElementById('questMenu').classList.add('show'); }",
    "  return h;\n}\nfunction questSheetParts(){ const h = renderQuests(), k = h.indexOf('<div class=\"tkHd\" style=\"margin-top:14px\">STANDING</div>'); return k<0 ? [h, ''] : [h.slice(0,k), h.slice(k).replace('<div class=\"tkHd\" style=\"margin-top:14px\">STANDING</div>','')]; }\nfunction openQuests(){ openSheet('quests'); }")
rep("  if(!quests.length) h = '<div class=\"skNote\">No work taken. Talk to villagers and ask for work.</div>';", "  if(!quests.length) h = '<div class=\"skNote\">No work taken. Talk to villagers and ask them for work.</div>';")
# menu buttons: APPEARANCE + CHARACTER (sheet); drop separate QUESTS
rep('    <button id="charBtn">CHARACTER</button>\n    <button id="skillBtn">SKILLS</button>\n    <button id="questBtn">QUESTS</button>', '    <button id="skillBtn">CHARACTER</button>\n    <button id="charBtn">APPEARANCE</button>')
rep("document.getElementById('questBtn').addEventListener('click', openQuests);\n", "")
rep('<div id="skillMenu"><div id="skillPanel"><div id="skillTop"><h2>Skills</h2>', '<div id="skillMenu"><div id="skillPanel"><div id="skillTop"><h2>Character</h2>')
rep("document.getElementById('skillClose').addEventListener('click', closeSkills);", "document.getElementById('skillClose').addEventListener('click', closeSkills);\ndocument.getElementById('skillList').addEventListener('click', e=>{ const b = e.target.closest('[data-tab]'); if(b){ sheetTab = b.dataset.tab; renderSheet(); } });")
rep("  .skRow { padding:8px 0; border-top:1px solid #2a2c26; }", """  .skRow { padding:8px 0; border-top:1px solid #2a2c26; }
  .shTabs { display:flex; gap:4px; margin:4px 0 8px; } .shTabs button { flex:1; font:12px monospace; letter-spacing:1px; padding:7px 4px; background:#151612; color:#8f8a7a; border:2px solid #050605; box-shadow:inset 0 0 0 1px #2a2c26; }
  .shTabs button.on { background:linear-gradient(#34372f,#1d1f1a); color:#e3cf95; box-shadow:inset 0 0 0 1px #8c7640; }
  #vLeft { display:flex; flex-direction:column; align-items:flex-start; gap:2px; }
  #hudStat { font:bold 10px monospace; letter-spacing:1px; color:#e3cf95; text-shadow:1px 1px 0 #000, 0 0 3px #000; opacity:.85; }
  #hudStat b { color:#ecc440; font-weight:bold; }""")
# Escape closes the sheet; J opens it
rep("function closeCraft(){\n  if(document.getElementById('classMenu')", "function closeCraft(){\n  if(document.getElementById('skillMenu').classList.contains('show')){ closeSkills(); return; }\n  if(document.getElementById('classMenu')")
rep("addEventListener('keydown', e=>{\n  keys[e.code]=true;\n", "addEventListener('keydown', e=>{\n  keys[e.code]=true;\n  if(e.code==='KeyJ' && !e.repeat && !paused && document.activeElement.tagName!=='INPUT'){ if(document.getElementById('skillMenu').classList.contains('show')) closeSkills(); else if(!craftOpen) openSheet(); return; }\n")
# quiet HUD: level and gold above the hearts
rep('<div id="vitals"><div id="hearts"></div>', '<div id="vitals"><div id="vLeft"><div id="hudStat"></div><div id="hearts"></div></div>')
rep("  const mh = maxHP(), key = health + ',' + food + ',' + mh;\n  if(key === vitalKey) return;\n  vitalKey = key;",
    "  const mh = maxHP(), key = health + ',' + food + ',' + mh + ',' + gold + ',' + skillGained;\n  if(key === vitalKey) return;\n  vitalKey = key;\n  document.getElementById('hudStat').innerHTML = `LV ${playerLevel()} \\u00b7 <b>${gold}g</b>`;")
open(p,'w').write(s); print('ok')
