p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    a = a.replace('\\u201c','\u201c').replace('\\u201d','\u201d')
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# resident helper
rep("""      // the resident is always the same person: their looks come from the village seed and the house number
      const rnd = vRng(Math.floor(h3(rx*31+i, 77, rz*17+i, SEED+520)*4294967295));
      const job = h.job==='villager' && i===0 ? 'guard' : h.job;                    // every village has at least one guard
      const m = newNpc(at[0],at[1],at[2], npcGenerate(rnd, v.houses.some(q=>q.job==='guard') ? h.job : job));""",
"""      const m = newNpc(at[0],at[1],at[2], residentOf(rx,rz,i));""")
rep("function villageCentre(v){", """// the resident of a house is always the same person: looks and name come from the village seed and the house number
function residentOf(rx,rz,i){
  const v = villageAt(rx,rz), h = v.houses[i];
  const rnd = vRng(Math.floor(h3(rx*31+i, 77, rz*17+i, SEED+520)*4294967295));
  const job = h.job==='villager' && i===0 && !v.houses.some(q=>q.job==='guard') ? 'guard' : h.job;     // every village has at least one guard
  return npcGenerate(rnd, job);
}
function villageCentre(v){""")
# reputation on violence
rep("  if(m.job==='guard') m.angry = 30; else { m.fleeT = 5; m.path = null; m.replanT = 0; }",
    "  if(m.job==='guard') m.angry = 30; else { m.fleeT = 5; m.path = null; m.replanT = 0; }\n  if(m.village && !(m.angryRepT>0)){ addRep(m.village, -5); m.angryRepT = 20; }")
rep("  if(m.hp<=0){ m.dead = true; m.deadT = 0; m.path = null; }\n}\n// open a closed door",
    "  if(m.hp<=0){ m.dead = true; m.deadT = 0; m.path = null; if(m.village) addRep(m.village, -25); }\n}\n// open a closed door")
rep("  m.swing = Math.max(0, m.swing - dt*3);\n  const guard = m.job==='guard'", "  m.swing = Math.max(0, m.swing - dt*3); if(m.angryRepT>0) m.angryRepT -= dt;\n  const guard = m.job==='guard'")

mod = r'''
// ---------- quests and reputation (Daggerfall-style: villagers offer work with a deadline, paid in gold) ----------
// Three kinds of work: hunt a beast that troubles the village, carry a parcel to someone in another village, or bring goods.
// Each village remembers how you treat it: work done raises your standing (better prices), harming its people lowers it,
// and at -30 they will not deal with you at all. Days are counted at sunrise; work not done in time fails.
const PARCEL = 1088; NAMES[PARCEL] = 'sealed parcel'; COLORS[PARCEL] = [176,140,92]; FLAT_ITEMS.add(PARCEL); SHORT[PARCEL] = 'parcel';
const QUEST_MAX = 3;
let quests = [], villageRep = {}, dayNo = 0, questId = 1;
function vkey(v){ return v[0]+','+v[1]; }
function repOf(v){ return v ? (villageRep[vkey(v)]||0) : 0; }
function addRep(v, n){ if(!v) return; const k = vkey(v); villageRep[k] = Math.max(-100, Math.min(100, (villageRep[k]||0)+n)); scheduleSave(); }
function repWord(r){ return r>=60 ? 'revered' : r>=30 ? 'liked' : r>=10 ? 'welcome' : r>-10 ? 'a stranger' : r>-30 ? 'distrusted' : 'unwelcome'; }
function buyPrice(id){ return Math.max(1, Math.round((PRICE[id]||1)*(1 - repOf(talkNpc && talkNpc.village)/400))); }
function dirWord(fx,fz,tx,tz){ const ang = Math.atan2(tx-fx, -(tz-fz)); return DIR8[((Math.round(ang/(Math.PI/4))%8)+8)%8]; }
const FETCH_WANTS = { blacksmith:[LEATHER,CHITIN,COAL_ITEM], baker:[WHEAT,RAW_MEAT,CARROT], farmer:[BONE,WOOL0,HAY], miner:[COAL_ITEM,COBBLE], librarian:[SILK,GLOWMOSS,EMBER],
                      cleric:[GLOWMOSS,CANDLE,SILK], fisher:[RAW_MEAT,LEATHER], villager:[WOOL0,SILK,LEATHER] };
const BEAST_NAME = { bear:'grizzly bear', tiger:'sabertooth tiger', spider:'giant spider', scorpion:'giant scorpion' };
// make up a job for this villager to offer (the same villager offers the same job until it is taken or the day turns)
function questOffer(m){
  const rnd = vRng(Math.floor(h3(m.id, dayNo, (m.home||'').length*7+m.job.length, SEED+611)*4294967295));
  const kinds = m.job==='guard' ? ['hunt','hunt','deliver'] : ['hunt','deliver','fetch','fetch'];
  let kind = kinds[Math.floor(rnd()*kinds.length)];
  const vc = m.vc || [m.x,m.z];
  if(kind==='deliver'){
    const [rx,rz] = m.village; let best = null, bd = 1e9;
    for(let a=-3;a<=3;a++) for(let b=-3;b<=3;b++){ if(!a && !b) continue; const v = villageAt(rx+a, rz+b); if(!v || !v.houses) continue;
      const c = villageCentre(v), d = Math.hypot(c[0]-vc[0], c[1]-vc[1]); if(d<bd){ bd = d; best = [rx+a, rz+b, v, c]; } }
    if(!best) kind = 'hunt';
    else {
      const [tx,tz,v,c] = best, i = Math.floor(rnd()*v.houses.length), who = residentOf(tx,tz,i);
      const days = 2 + Math.ceil(bd/400), reward = 30 + Math.round(bd/8);
      return { kind, to:tx+','+tz+':'+i, toName:who.name, toJob:who.job, tvc:c, days, reward, rep:8,
               text:`I need a sealed parcel taken to ${who.name}, the ${(JOB_TITLE[who.job]||'villager').toLowerCase()}, in the village about ${Math.round(bd/10)*10} paces ${dirWord(vc[0],vc[1],c[0],c[1])} of here. Get it there within ${days} days and they will pay you ${reward} gold.` };
    }
  }
  if(kind==='fetch'){
    const opts = FETCH_WANTS[m.job] || FETCH_WANTS.villager, id = opts[Math.floor(rnd()*opts.length)];
    const n = Math.max(2, Math.min(12, Math.round(40/(PRICE[id]||3)))), reward = Math.round(n*(PRICE[id]||3)*1.6)+10, days = 4;
    return { kind, item:id, n, days, reward, rep:6, text:`I'm short of ${NAMES[id]}. Bring me ${n} within ${days} days and I'll pay you ${reward} gold.` };
  }
  // hunt: a beast has made its den out in the wild, somewhere 70-160 paces from the village
  for(let t=0;t<40;t++){
    const a = rnd()*6.283, d = 70+rnd()*90, x = Math.floor(vc[0]+Math.cos(a)*d), z = Math.floor(vc[1]+Math.sin(a)*d), b = biomeAt(x,z);
    const fit = Object.keys(BEAST).filter(k=>!BEAST[k].night && BEAST[k].where(b, colInfo(x,z).h+1));
    if(!fit.length || nearVillage(x,z)) continue;
    const beast = fit[Math.floor(rnd()*fit.length)], days = 3, reward = 50 + Math.round(BEAST[beast].hp*2.5);
    return { kind:'hunt', beast, at:[x,z], days, reward, rep:10,
             text:`A ${BEAST_NAME[beast]} has made its den about ${Math.round(d/10)*10} paces ${dirWord(vc[0],vc[1],x,z)} of here, and it is getting bolder. Kill it within ${days} days and come back to me. ${reward} gold for your trouble.` };
  }
  return { kind:'fetch', item:COAL_ITEM, n:6, days:4, reward:40, rep:6, text:`Bring me 6 coal within 4 days and I'll pay you 40 gold.` };
}
function acceptQuest(m, q){
  if(quests.length>=QUEST_MAX) return 'You already have as much work as you can carry.';
  Object.assign(q, { id:questId++, giver:m.home, giverName:m.name, giverJob:m.job, village:m.village, gvc:m.vc, due:dayNo+q.days, state:'active' });
  if(q.kind==='deliver'){ inv[PARCEL] = (inv[PARCEL]||0)+1; autoFillHotbar(PARCEL); }
  quests.push(q); scheduleSave();
  return q.kind==='deliver' ? 'Here is the parcel. Don\'t open it.' : q.kind==='hunt' ? 'Good luck. Bring me word when it is dead.' : 'I\'ll be waiting.';
}
function finishQuest(q, ok){
  quests.splice(quests.indexOf(q),1);
  if(ok){ gold += q.reward; addRep(q.village, q.rep); if(q.kind==='deliver') addRep(q.to.split(':')[0].split(',').map(Number), 4); skillToast('QUEST DONE<br><small>+'+q.reward+' gold</small>', true); }
  else { addRep(q.village, -5); if(q.kind==='deliver' && inv[PARCEL]>0) inv[PARCEL]--; skillToast('QUEST FAILED<br><small>'+q.giverName+' is disappointed</small>', true); }
  scheduleSave();
}
function questDawn(){ dayNo++; for(const q of quests.slice()) if(dayNo>q.due && q.state!=='done') finishQuest(q, false); }
// the hunted beast appears at its den when you come near, and is a little tougher than most
function questTick(){
  for(const q of quests){
    if(q.kind!=='hunt' || q.state!=='active') continue;
    if(mobs.some(m=>m.questId===q.id)) continue;
    if(Math.hypot(q.at[0]-player.x, q.at[1]-player.z) > 64) continue;
    for(let t=0;t<12;t++){
      const x = q.at[0]+Math.floor(Math.random()*7)-3, z = q.at[1]+Math.floor(Math.random()*7)-3, y = colInfo(x,z).h+1;
      if(!ratCanStand(x,y,z)) continue;
      const m = newBeast(q.beast,x,y,z); m.hp = Math.round(m.hp*1.5); m.questId = q.id; mobs.push(m); break;
    }
  }
}
function questKilled(m){ const q = quests.find(q=>q.id===m.questId); if(q && q.state==='active'){ q.state = 'done'; scheduleSave(); skillToast('The '+BEAST_NAME[q.beast]+' is dead<br><small>return to '+q.giverName+'</small>', true); } }
function renderQuests(){
  let h = '';
  if(!quests.length) h = '<div class="skNote">No work taken. Talk to villagers and ask for work.</div>';
  for(const q of quests){
    const left = q.due-dayNo, gv = q.gvc ? `${Math.round(Math.hypot(q.gvc[0]-player.x,q.gvc[1]-player.z)/10)*10} paces ${dirWord(player.x,player.z,q.gvc[0],q.gvc[1])}` : '';
    let goal = '';
    if(q.kind==='hunt') goal = q.state==='done' ? `The ${BEAST_NAME[q.beast]} is dead. Return to ${q.giverName} (${gv}).` : `Kill the ${BEAST_NAME[q.beast]}: its den is ${Math.round(Math.hypot(q.at[0]-player.x,q.at[1]-player.z)/10)*10} paces ${dirWord(player.x,player.z,q.at[0],q.at[1])}.`;
    else if(q.kind==='deliver') goal = `Take the parcel to ${q.toName} (${(JOB_TITLE[q.toJob]||'villager').toLowerCase()}), ${Math.round(Math.hypot(q.tvc[0]-player.x,q.tvc[1]-player.z)/10)*10} paces ${dirWord(player.x,player.z,q.tvc[0],q.tvc[1])}.`;
    else goal = `Bring ${q.n} ${NAMES[q.item]} to ${q.giverName} (${gv}). You have ${inv[q.item]||0}.`;
    h += `<div class="skRow"><div class="skHead"><b>${q.kind==='hunt'?'Hunt':q.kind==='deliver'?'Delivery':'Supplies'} for ${q.giverName}</b><span>${q.reward}g</span></div><div class="skDesc" style="color:#d8cfb8">${goal}</div><div class="skDesc">${left>0 ? left+(left===1?' day':' days')+' left' : 'due today'}</div></div>`;
  }
  const reps = Object.keys(villageRep).filter(k=>villageRep[k]);
  if(reps.length){ h += '<div class="tkHd" style="margin-top:14px">STANDING</div>'; for(const k of reps){ const [rx,rz] = k.split(',').map(Number), v = villageAt(rx,rz); if(!v) continue; const c = villageCentre(v);
    h += `<div class="skDesc" style="color:#d8cfb8">Village ${Math.round(Math.hypot(c[0]-player.x,c[1]-player.z)/10)*10} paces ${dirWord(player.x,player.z,c[0],c[1])}: ${repWord(villageRep[k])} (${villageRep[k]})</div>`; } }
  document.getElementById('questList').innerHTML = h;
}
function openQuests(){ renderQuests(); document.getElementById('questMenu').classList.add('show'); }
function closeQuests(){ document.getElementById('questMenu').classList.remove('show'); }
'''
rep("let talkNpc = null, talkView = 'talk', talkLine = '';", mod+"let talkNpc = null, talkView = 'talk', talkLine = '', talkOffer = null;")
# talk view: rep gate, work buttons, turn-ins
rep("""  if(talkView==='talk'){
    h += `<div class="tkLine">\\u201c${talkLine}\\u201d</div><div class="tkBtns">`;
    if(shop) h += `<button data-a="trade">TRADE</button>`;""", """  document.getElementById('talkGold').textContent = gold + ' gold \\u00b7 ' + repWord(repOf(m.village));
  const shunned = repOf(m.village) <= -30;
  if(talkView==='talk'){
    h += `<div class="tkLine">\\u201c${shunned ? 'We don\\'t deal with your kind here. Leave.' : talkLine}\\u201d</div><div class="tkBtns">`;
    if(talkOffer) h += `<button data-a="accept">ACCEPT</button><button data-a="decline">DECLINE</button>`;
    else if(!shunned){
    const del = quests.find(q=>q.kind==='deliver' && q.to===m.home && inv[PARCEL]>0), back = quests.find(q=>q.giver===m.home && (q.kind==='hunt' ? q.state==='done' : q.kind==='fetch' && (inv[q.item]||0)>=q.n));
    if(del) h += `<button data-a="deliver">GIVE PARCEL</button>`;
    if(back) h += `<button data-a="turnin">${back.kind==='hunt' ? 'REPORT THE KILL' : 'HAND OVER '+back.n+' '+NAMES[back.item].toUpperCase()}</button>`;
    h += `<button data-a="work">ASK FOR WORK</button>`;
    if(shop) h += `<button data-a="trade">TRADE</button>`;""")
rep("""    h += `<button data-a="news">ASK FOR NEWS</button><button data-a="bye">GOODBYE</button></div>`;""",
    """    h += `<button data-a="news">ASK FOR NEWS</button>`; }
    if(!talkOffer) h += `<button data-a="bye">GOODBYE</button>`;
    h += `</div>`;""")
rep("""      for(const id of shop.sell){ const pr = PRICE[id]||1;""", """      for(const id of shop.sell){ const pr = buyPrice(id);""")
rep("""  else if(a==='news'){ talkLine = talkNews(m); }""", """  else if(a==='news'){ talkLine = talkNews(m); }
  else if(a==='work'){
    const mine = quests.find(q=>q.giver===m.home);
    if(mine) talkLine = 'You already have work from me. ' + (mine.kind==='hunt' ? 'Is the beast dead yet?' : mine.kind==='deliver' ? 'Has my parcel reached ' + mine.toName + '?' : 'Where are my ' + NAMES[mine.item] + '?');
    else if(quests.length>=QUEST_MAX) talkLine = 'You look busy enough already. Come back when you have finished your other work.';
    else { talkOffer = questOffer(m); talkLine = talkOffer.text; }
  }
  else if(a==='accept' && talkOffer){ talkLine = acceptQuest(m, talkOffer); talkOffer = null; }
  else if(a==='decline'){ talkOffer = null; talkLine = 'Suit yourself.'; }
  else if(a==='deliver'){ const q = quests.find(q=>q.kind==='deliver' && q.to===m.home); if(q && inv[PARCEL]>0){ inv[PARCEL]--; finishQuest(q, true); talkLine = `Ah, from ${q.giverName}! Thank you. Here's ${q.reward} gold.`; } }
  else if(a==='turnin'){ const q = quests.find(q=>q.giver===m.home);
    if(q && q.kind==='hunt' && q.state==='done'){ finishQuest(q, true); talkLine = `You killed it? The village owes you. ${q.reward} gold, as promised.`; }
    else if(q && q.kind==='fetch' && (inv[q.item]||0)>=q.n){ inv[q.item] -= q.n; finishQuest(q, true); talkLine = `Just what I needed. ${q.reward} gold, as promised.`; } }""")
rep("""function talkBuy(id){
  const pr = PRICE[id]||1;""", """function talkBuy(id){
  const pr = buyPrice(id);""")
rep("function sellPrice(id){ return Math.max(1, Math.floor((PRICE[id]||1)*0.4)); }",
    "function sellPrice(id){ return Math.max(1, Math.floor((PRICE[id]||1)*0.4*(1 + repOf(talkNpc && talkNpc.village)/400))); }")
rep("  talkNpc = m; talkView = 'talk'; m.talkT = 0;", "  talkNpc = m; talkView = 'talk'; m.talkT = 0; talkOffer = null;")
# trade gated when shunned
rep("    if(closed) h += `<div class=\"tkLine\">\\u201cWe're closed for the night. Come back in the morning.\\u201d</div>`;",
    "    if(shunned) h += `<div class=\"tkLine\">\\u201cNo.\\u201d</div>`;\n    else if(closed) h += `<div class=\"tkLine\">\\u201cWe're closed for the night. Come back in the morning.\\u201d</div>`;")
# hooks: dawn, ticks, kills, save/load
rep("  if(wrapped) villagerDawn();", "  if(wrapped){ villagerDawn(); questDawn(); }")
rep("  if(NPCS_IN_WORLD){ npcSpawnT -= dt; if(npcSpawnT<=0){ npcSpawnT = 3; trySpawnNpcs(); } }", "  if(NPCS_IN_WORLD){ npcSpawnT -= dt; if(npcSpawnT<=0){ npcSpawnT = 3; trySpawnNpcs(); questTick(); } }")
rep("    if(m.dead){ if(m.home && !m.noted){", "    if(m.dead){ if(m.questId && !m.noted){ m.noted = true; questKilled(m); }\n      if(m.home && !m.noted){")
rep("gold, villagers:villagerState,", "gold, villagers:villagerState, quests, rep:villageRep, dayNo, questId,")
rep("  gold = meta.gold || 0; villagerState = meta.villagers || {};", "  gold = meta.gold || 0; villagerState = meta.villagers || {}; quests = meta.quests || []; villageRep = meta.rep || {}; dayNo = meta.dayNo || 0; questId = meta.questId || 1;")
# parcel icon
rep("    case GOLD: paintIcon(g,(P,E)=>{", """    case PARCEL: paintIcon(g,(P,E)=>{ for(let y=4;y<=12;y++) for(let x=3;x<=12;x++) P(x,y, y===4||x===3 ? [206,170,118] : y===12||x===12 ? [130,98,60] : [176,140,92]);
              for(let x=3;x<=12;x++) P(x,8,[110,80,50]); for(let y=4;y<=12;y++) P(8,y,[110,80,50]); for(const [x,y] of [[7,7],[8,7],[9,7],[7,9],[8,9],[9,9],[7,8],[9,8]]) P(x,y,[176,40,36]); P(8,8,[214,70,60]); }); return true;
    case GOLD: paintIcon(g,(P,E)=>{""")
# quest menu UI
rep('    <button id="skillBtn">SKILLS</button>', '    <button id="skillBtn">SKILLS</button>\n    <button id="questBtn">QUESTS</button>')
rep('<div id="skillToast"></div>', '<div id="questMenu"><div id="skillPanel" class="qPanel"><div id="skillTop"><h2>Quests</h2><button id="questClose">DONE</button></div><div id="questList"></div></div></div>\n<div id="skillToast"></div>')
rep("  #skillMenu.show { display:flex; }", "  #skillMenu.show { display:flex; }\n  #questMenu { position:fixed; inset:0; z-index:21; display:none; align-items:center; justify-content:center; color:#d8cfb8; font-family:monospace; background:rgba(0,0,0,.92); }\n  #questMenu.show { display:flex; }\n  #questMenu #skillTop button { font:13px monospace; letter-spacing:2px; padding:8px 16px; background:linear-gradient(#34372f,#1d1f1a); color:#e3cf95; border:2px solid #050605; box-shadow:inset 0 0 0 1px #8c7640; }")
rep("document.getElementById('skillBtn').addEventListener('click', openSkills);", "document.getElementById('skillBtn').addEventListener('click', openSkills);\ndocument.getElementById('questBtn').addEventListener('click', openQuests);\ndocument.getElementById('questClose').addEventListener('click', closeQuests);")
open(p,'w').write(s); print('ok')
