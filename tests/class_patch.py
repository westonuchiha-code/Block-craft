p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
mod = r'''// ---------- classes: six of them, Final Fantasy style. Picked once per world; they set where your skills start, which ones
// you learn faster (half again as fast), and one perk. Nothing is ever locked away by class.
const CLASSES = [
  { id:'warrior',  name:'Warrior',     col:'#c8463c', start:{weapons:25, unarmed:10, athletics:15}, fav:['weapons','athletics'],
    perk:'Tough: starts with two extra hearts.', blurb:'Steel and stamina. Hits hard, takes a beating.' },
  { id:'monk',     name:'Monk',        col:'#e0a040', start:{unarmed:25, athletics:20, stealth:10}, fav:['unarmed','athletics'],
    perk:'Iron fists: bare-handed blows do +1 damage.', blurb:'Fights with fists and feet. Quick on the ground.' },
  { id:'thief',    name:'Thief',       col:'#7a8c9c', start:{stealth:25, athletics:20, weapons:10}, fav:['stealth','athletics'],
    perk:'Silver tongue: buys 15% cheaper, sells 15% dearer.', blurb:'Unseen, unheard, and always gets a good price.' },
  { id:'ranger',   name:'Ranger',      col:'#5a9a4a', start:{weapons:20, stealth:15, athletics:15}, fav:['weapons','stealth'],
    perk:'Hunter: beasts give one extra of every drop.', blurb:'At home in the wilds. Tracks, hunts and skins.' },
  { id:'blackmage',name:'Black Mage',  col:'#6a5ac8', start:{magic:25, weapons:5, stealth:10}, fav:['magic'],
    perk:'Arcane: a cast keeps its charge 20% more often. Starts with fire and lightning potions.', blurb:'Fire and lightning. Fragile up close.' },
  { id:'whitemage',name:'White Mage',  col:'#e8e2d0', start:{magic:20, unarmed:10, athletics:10}, fav:['magic','unarmed'],
    perk:'Blessed: heals on a lighter stomach (food 6+, not 18+) and temple healing costs half.', blurb:'A healer who can still hold their own.' }
];
let playerClass = null;
function cls(){ return CLASSES.find(c=>c.id===playerClass) || null; }
function isClass(id){ return playerClass===id; }
let classPick = null;
function openClassPick(){
  classPick = null; craftOpen = true;
  const el = document.getElementById('classList'); el.innerHTML = '';
  for(const c of CLASSES){
    const d = document.createElement('div'); d.className = 'clCard'; d.dataset.id = c.id;
    const st = SKILLS.map(k=>`<span class="${c.fav.includes(k.id)?'fav':''}">${k.name} ${c.start[k.id]||SKILL_START}</span>`).join('');
    d.innerHTML = `<div class="clName" style="border-color:${c.col}"><i style="background:${c.col}"></i>${c.name}</div><div class="clBlurb">${c.blurb}</div><div class="clSk">${st}</div><div class="clPerk">${c.perk}</div>`;
    d.addEventListener('click', ()=>{ classPick = c.id; el.querySelectorAll('.clCard').forEach(x=>x.classList.toggle('sel', x.dataset.id===c.id)); document.getElementById('classGo').disabled = false; });
    el.appendChild(d);
  }
  document.getElementById('classGo').disabled = true;
  document.getElementById('classMenu').classList.add('show');
  if(document.pointerLockElement) document.exitPointerLock();
}
function confirmClass(){
  if(!classPick) return;
  playerClass = classPick; const c = cls();
  if(skillGained===0) for(const k of SKILLS){ skills[k.id] = c.start[k.id] || SKILL_START; skillUses[k.id] = 0; }    // a fresh character starts where the class says
  if(playerClass==='blackmage'){ inv[FIRE_POTION] = (inv[FIRE_POTION]||0)+2; inv[BOLT_POTION] = (inv[BOLT_POTION]||0)+2; autoFillHotbar(FIRE_POTION); }
  health = maxHP(); vitalKey = '';
  document.getElementById('classMenu').classList.remove('show'); craftOpen = false;
  skillToast(c.name.toUpperCase(), true); scheduleSave();
}
'''
rep("// ---------- skills and levels (Daggerfall's idea", mod+"// ---------- skills and levels (Daggerfall's idea")
# effects
rep("function maxHP(){ return Math.min(40, 20 + 2*Math.floor((playerLevel()-1)/2)); }", "function maxHP(){ return Math.min(40, 20 + 2*Math.floor((playerLevel()-1)/2)) + (isClass('warrior') ? 4 : 0); }")
rep("function skillUsesFor(id){ const K = SKILLS.find(k=>k.id===id); return Math.round(K.base*(1+Math.floor(skills[id]/15)*0.6)); }",
    "function skillUsesFor(id){ const K = SKILLS.find(k=>k.id===id), c = cls(); return Math.max(1, Math.round(K.base*(1+Math.floor(skills[id]/15)*0.6)*(c && c.fav.includes(id) ? 0.67 : 1))); }")
rep("  return 1 + skills.unarmed/20;              // a fist: 1.25 at the start, 6 at mastery", "  return 1 + skills.unarmed/20 + (isClass('monk') ? 1 : 0);              // a fist: 1.25 at the start, 6 at mastery")
rep("  if(Math.random() < skills.magic/300){", "  if(Math.random() < skills.magic/300 + (isClass('blackmage') ? 0.2 : 0)){")
rep("    for(const [id,lo,hi] of K.drops) for(let n=roll(lo,hi); n>0; n--) spawnDrop(x,y,z,id);", "    for(const [id,lo,hi] of K.drops) for(let n=roll(lo,hi)+(isClass('ranger')?1:0); n>0; n--) spawnDrop(x,y,z,id);")
rep("  if(food >= 18 && health < maxHP() && health > 0){", "  if(food >= (isClass('whitemage') ? 6 : 18) && health < maxHP() && health > 0){")
rep("function buyPrice(id){ return Math.max(1, Math.round((PRICE[id]||1)*(1 - repOf(talkNpc && talkNpc.village)/400))); }",
    "function buyPrice(id){ return Math.max(1, Math.round((PRICE[id]||1)*(1 - repOf(talkNpc && talkNpc.village)/400)*(isClass('thief') ? 0.85 : 1))); }")
rep("function sellPrice(id){ return Math.max(1, Math.floor((PRICE[id]||1)*0.4*(1 + repOf(talkNpc && talkNpc.village)/400))); }",
    "function sellPrice(id){ return Math.max(1, Math.floor((PRICE[id]||1)*0.4*(1 + repOf(talkNpc && talkNpc.village)/400)*(isClass('thief') ? 1.15 : 1))); }")
rep("    const need = maxHP()-health, cost = need*3;", "    const need = maxHP()-health, cost = need*(isClass('whitemage') ? 1.5 : 3) | 0;")
# skills screen shows class
rep("  let h = `<div class=\"skLvl\">LEVEL ${L}<span>", "  const c = cls();\n  let h = `<div class=\"skLvl\">${c ? c.name.toUpperCase()+' \\u00b7 ' : ''}LEVEL ${L}<span>")
rep("    h += `<div class=\"skRow\"><div class=\"skHead\"><b>${k.name}</b>", "    h += `<div class=\"skRow\"><div class=\"skHead\"><b>${k.name}${c && c.fav.includes(k.id) ? ' <small style=\"color:#8fbf6a\">\\u2605</small>' : ''}</b>")
rep("  for(const k of SKILLS){\n    const v = skills[k.id], f = v>=100", "  if(c) h += `<div class=\"skNote\" style=\"color:#b8ae94\">${c.perk} \\u2605 skills are learned faster.</div>`;\n  for(const k of SKILLS){\n    const v = skills[k.id], f = v>=100")
# save / load / first pick
rep("gold, villagers:villagerState, quests,", "gold, cls:playerClass, villagers:villagerState, quests,")
rep("  gold = meta.gold || 0; villagerState", "  gold = meta.gold || 0; playerClass = meta.cls || null; villagerState")
rep("  paused = false;\n  closeMenu();\n}\n\nfunction openMenu(){", "  paused = false;\n  closeMenu();\n  if(!playerClass && !testWorld) setTimeout(openClassPick, 300);       // a new character chooses a class first\n}\n\nfunction openMenu(){")
# UI
rep('<div id="skillToast"></div>', '''<div id="classMenu"><div id="classPanel"><h2>Choose your class</h2><div class="clSub">It sets where your skills start and which you learn faster. Anyone can still do anything.</div><div id="classList"></div><button id="classGo" disabled>BEGIN</button></div></div>
<div id="skillToast"></div>''')
rep("  #skillMenu.show { display:flex; }", """  #skillMenu.show { display:flex; }
  #classMenu { position:fixed; inset:0; z-index:22; display:none; align-items:center; justify-content:center; color:#d8cfb8; font-family:monospace; background:rgba(0,0,0,.94); }
  #classMenu.show { display:flex; }
  #classPanel { width:min(96vw,720px); max-height:94vh; overflow-y:auto; padding:12px; box-sizing:border-box; text-align:center; }
  #classPanel h2 { margin:4px 0; color:#e3cf95; letter-spacing:3px; font-size:18px; } .clSub { font-size:11px; color:#8f8a7a; margin-bottom:10px; }
  #classList { display:grid; grid-template-columns:repeat(auto-fill,minmax(210px,1fr)); gap:8px; text-align:left; }
  .clCard { padding:9px 10px; background:linear-gradient(#1b1d18,#0f100e); border:2px solid #050605; box-shadow:inset 0 0 0 1px #3a3d35; cursor:pointer; }
  .clCard.sel { box-shadow:inset 0 0 0 2px #e3cf95, 0 0 12px rgba(227,207,149,.35); }
  .clName { font-size:15px; color:#e3cf95; letter-spacing:2px; display:flex; align-items:center; gap:8px; } .clName i { width:10px; height:10px; display:inline-block; border:1px solid #000; }
  .clBlurb { font-size:11px; color:#b8ae94; margin:4px 0 6px; }
  .clSk { display:flex; flex-wrap:wrap; gap:3px 8px; font-size:11px; color:#8f8a7a; } .clSk .fav { color:#8fbf6a; }
  .clPerk { font-size:11px; color:#d8cfb8; margin-top:6px; border-top:1px solid #2a2c26; padding-top:5px; }
  #classGo { margin-top:12px; font:14px monospace; letter-spacing:3px; padding:10px 28px; background:linear-gradient(#34372f,#1d1f1a); color:#e3cf95; border:2px solid #050605; box-shadow:inset 0 0 0 1px #8c7640; }
  #classGo:disabled { opacity:.35; }""")
rep("document.getElementById('skillBtn').addEventListener('click', openSkills);", "document.getElementById('skillBtn').addEventListener('click', openSkills);\ndocument.getElementById('classGo').addEventListener('click', confirmClass);")
# Escape must not dismiss the picker
rep("function closeCraft(){\n  if(talkNpc){ closeTalk(); return; }", "function closeCraft(){\n  if(document.getElementById('classMenu').classList.contains('show')) return;      // a class must be chosen\n  if(talkNpc){ closeTalk(); return; }")
open(p,'w').write(s); print('ok')
