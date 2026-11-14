p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    a = a.replace('\\u201c','\u201c').replace('\\u201d','\u201d')
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# ---- prices for things you build ----
rep("  P(LEATHER, 12);", """  for(let w=0;w<4;w++){ P(tableId(w), 12); P(chairId(w,0), 8); P(benchId(w,0), 10); P(doorId(w,0,0,0), 10); P(fenceId(w,0), 3); P(gateId(w,0,0), 6); }
  P(CHEST, 12); P([WIN0, WIN0+2], 3); P(STAINED0, 6); for(let i=0;i<12;i++) PRICE[RUG0+i] = 10; P([STONE_BRICK, FLAGSTONE, MOSSY_BRICK], 3); P([PILLAR, CARVED], 5);
  P(LEATHER, 12);""")
# ---- villagers buy what you make ----
rep("  villager:   { title:'Odds and ends', sell:[STICK, PLANKS, CRAFT_TABLE, BED0, WOOL0, CANDLE], buy:[SILK, WOOL0, LEATHER, LITTER, HAY] }",
    "  villager:   { title:'Odds and ends', sell:[STICK, PLANKS, CRAFT_TABLE, BED0, WOOL0, CANDLE], buy:[SILK, WOOL0, LEATHER, LITTER, HAY, BED0, CHEST, ...[0,1,2,3].flatMap(w=>[tableId(w), chairId(w,0), benchId(w,0), doorId(w,0,0,0)]), ...Array.from({length:12},(_,i)=>RUG0+i)] }")
rep("buy:[GLOWMOSS, EMBER, SILK, BONE] },", "buy:[GLOWMOSS, EMBER, SILK, BONE, BOOKSHELF, GLASS, WIN0, WIN0+2, CANDLE] },")
rep("                buy:[COAL_ITEM, IRON_ORE, IRON_INGOT,", "                buy:[...Object.keys(ARMOR).map(Number), IRON_PICK, IRON_AXE, IRON_SWORD, ADAM_SWORD, MITH_SWORD, BARS0, COAL_ITEM, IRON_ORE, IRON_INGOT,")
rep("buy:[...CROPS_SOLD, HAY] },", "buy:[...CROPS_SOLD, HAY, ...[0,1,2,3].map(w=>fenceId(w,0)), WOOD_BUCKET] },")
rep("buy:[COAL_ITEM, IRON_ORE, ADAM_ORE, MITH_ORE,", "buy:[STONE_BRICK, FLAGSTONE, PILLAR, CARVED, COAL_ITEM, IRON_ORE, ADAM_ORE, MITH_ORE,")
# ---- work orders and building jobs ----
rep("const BEAST_NAME = {", """// things a villager will order from you, by trade (you make them; they pay well over the shop price)
const ORDER_WANTS = { blacksmith:[IRON_SWORD, IRON_PICK, BARS0, LANTERN0+1, AR(2,0), AR(0,1)], baker:[...DISHES.slice(0,4).map(d=>d.id), STEAK, MEAT_STEW, FLOUR],
  farmer:[fenceId(0,0), gateId(0,0,0), WOOD_BUCKET, WOOD_HOE, IRON_HOE], miner:[STONE_PICK, IRON_PICK, LANTERN0+1, STONE_BRICK],
  librarian:[BOOKSHELF, CANDLE, GLASS, WIN0+2, chairId(1,0)], cleric:[CANDLE, LANTERN0+1, BOOKSHELF, benchId(2,0)], fisher:[WOOD_BUCKET, CHEST, fenceId(1,0)],
  villager:[chairId(0,0), tableId(0), BED0, doorId(0,0,0,0), CHEST, benchId(0,0), RUG0+2], guard:[IRON_SWORD, AR(0,1), AR(2,1), AR(2,0), CROSSBOW] };
// building jobs: put blocks down inside the village (counted as you place them)
const BUILD_JOBS = [
  { key:'light',  text:n=>`The lanes are pitch black at night. Hang ${n} lanterns about the village`, n:[3,5], test:b=>IS_LANTERN[b], what:'lanterns' },
  { key:'walls',  text:n=>`Our walls are crumbling. Lay ${n} stone bricks or cobblestone to mend them`, n:[12,20], test:b=>b===STONE_BRICK || b===COBBLE || b===MOSSY_BRICK, what:'stone bricks or cobblestone' },
  { key:'fence',  text:n=>`The beasts keep getting into the fields. Put up ${n} fence posts around them`, n:[10,16], test:b=>IS_FENCE[b] || IS_GATE[b], what:'fence posts' },
  { key:'pave',   text:n=>`The square turns to mud every time it rains. Pave it with ${n} flagstones`, n:[10,16], test:b=>b===FLAGSTONE, what:'flagstones' },
  { key:'trees',  text:n=>`We need shade and timber for the years ahead. Plant ${n} saplings in the village`, n:[3,5], test:b=>IS_SAP[b], what:'saplings' } ];
function questPlaced(b, x, z){
  for(const q of quests){
    if(q.kind!=='build' || q.state!=='active') continue;
    const J = BUILD_JOBS.find(j=>j.key===q.job);
    if(!J.test(b) || Math.hypot(x+0.5-q.gvc[0], z+0.5-q.gvc[1]) > 48) continue;
    q.got = (q.got||0)+1;
    if(q.got>=q.n){ q.state = 'done'; skillToast('BUILDING DONE<br><small>tell '+q.giverName+'</small>', true); }
    scheduleSave();
  }
}
const BEAST_NAME = {""")
rep("  const kinds = m.job==='guard' ? ['hunt','hunt','deliver'] : ['hunt','deliver','fetch','fetch'];",
    "  const kinds = m.job==='guard' ? ['hunt','hunt','deliver','order','build'] : ['hunt','deliver','fetch','order','order','build'];")
rep("  if(kind==='fetch'){\n    const opts = FETCH_WANTS[m.job]", """  if(kind==='order'){
    const opts = ORDER_WANTS[m.job] || ORDER_WANTS.villager, id = opts[Math.floor(rnd()*opts.length)];
    const pr = PRICE[id]||8, n = Math.max(1, Math.min(6, Math.round(60/pr))), reward = Math.round(n*pr*1.8)+10, days = 5;
    return { kind:'fetch', order:true, item:id, n, days, reward, rep:8, text:`I'd pay good coin for ${n===1 ? 'a well-made '+NAMES[id] : n+' '+NAMES[id]+(NAMES[id].endsWith('s')?'':'s')}. Make ${n===1?'it':'them'} for me within ${days} days and I'll give you ${reward} gold.` };
  }
  if(kind==='build'){
    const J = BUILD_JOBS[Math.floor(rnd()*BUILD_JOBS.length)], n = J.n[0] + Math.floor(rnd()*(J.n[1]-J.n[0]+1)), reward = 30 + n*6, days = 4;
    return { kind:'build', job:J.key, n, got:0, days, reward, rep:12, text:`${J.text(n)}, and come tell me when it's done. ${reward} gold, and the village won't forget it.` };
  }
  if(kind==='fetch'){
    const opts = FETCH_WANTS[m.job]""")
rep("  setB(x,y,z,placeId); placedSet.add(x+','+y+','+z);", "  setB(x,y,z,placeId); placedSet.add(x+','+y+','+z); if(quests.length) questPlaced(placeId, x, z);")
# turn in a building job; quest log text
rep("    if(q && q.kind==='hunt' && q.state==='done'){ finishQuest(q, true); talkLine = `You killed it? The village owes you. ${q.reward} gold, as promised.`; }",
    "    if(q && q.kind==='hunt' && q.state==='done'){ finishQuest(q, true); talkLine = `You killed it? The village owes you. ${q.reward} gold, as promised.`; }\n    else if(q && q.kind==='build' && q.state==='done'){ finishQuest(q, true); talkLine = `I saw it with my own eyes. Fine work! ${q.reward} gold, as promised.`; }")
rep("back = quests.find(q=>q.giver===m.home && (q.kind==='hunt' ? q.state==='done' :", "back = quests.find(q=>q.giver===m.home && (q.kind==='hunt' || q.kind==='build' ? q.state==='done' :")
rep("    if(back) h += `<button data-a=\"turnin\">${back.kind==='hunt' ? 'REPORT THE KILL' :", "    if(back) h += `<button data-a=\"turnin\">${back.kind==='build' ? 'REPORT THE WORK' : back.kind==='hunt' ? 'REPORT THE KILL' :")
rep("    else goal = `Bring ${q.n} ${NAMES[q.item]} to ${q.giverName} (${gv}). You have ${inv[q.item]||0}.`;",
    "    else if(q.kind==='build'){ const J = BUILD_JOBS.find(j=>j.key===q.job); goal = q.state==='done' ? `Done. Tell ${q.giverName} (${gv}).` : `Place ${q.n} ${J.what} in ${q.giverName}'s village (${gv}). ${q.got||0} of ${q.n} so far.`; }\n    else goal = `${q.order ? 'Make' : 'Bring'} ${q.n} ${NAMES[q.item]} for ${q.giverName} (${gv}). You have ${inv[q.item]||0}.`;")
rep("<b>${q.kind==='hunt'?'Hunt':q.kind==='deliver'?'Delivery':'Supplies'} for ${q.giverName}</b>", "<b>${q.kind==='hunt'?'Hunt':q.kind==='deliver'?'Delivery':q.kind==='build'?'Building':q.order?'Order':'Supplies'} for ${q.giverName}</b>")
rep("    if(mine) talkLine = 'You already have work from me. ' + (mine.kind==='hunt' ? 'Is the beast dead yet?' : mine.kind==='deliver' ? 'Has my parcel reached ' + mine.toName + '?' : 'Where are my ' + NAMES[mine.item] + '?');",
    "    if(mine) talkLine = 'You already have work from me. ' + (mine.kind==='hunt' ? 'Is the beast dead yet?' : mine.kind==='deliver' ? 'Has my parcel reached ' + mine.toName + '?' : mine.kind==='build' ? 'How is the building coming along?' : 'Where are my ' + NAMES[mine.item] + '?');")
# ---- training and repair: what gold buys that you can't make ----
rep("let talkNpc = null, talkView = 'talk', talkLine = '', talkOffer = null;", """// training (Daggerfall-style): each trade can teach one skill, one lesson a day, and only up to 50 (past that you learn by doing)
const TRAINS = { guard:'weapons', villager:'stealth', miner:'mining', farmer:'farming', baker:'alchemy', cleric:'magic', librarian:'magic', fisher:'athletics', blacksmith:'woodcut' };
const TRAIN_CAP = 50;
let trainedDay = {};                                          // trainer -> the day of their last lesson
function trainCost(id){ return 15 + skills[id]*4; }
// repairs: the smith mends what you're wearing and the tool in your hand, for gold
function repairCost(){
  let c = 0;
  for(const a of armor) if(a){ const A = ARMOR[a.id]; c += (1 - a.dur/A.dur) * (PRICE[a.id]||20) * 0.5; }
  const t = HOTBAR[sel]; if(TOOLS[t] && inv[t]>0 && wear[t]){ syncWear(); for(const d of wear[t]) c += (1 - d/TOOLS[t].dur) * (PRICE[t]||15) * 0.5; }
  return Math.ceil(c);
}
function doRepair(){
  for(const a of armor) if(a) a.dur = ARMOR[a.id].dur;
  const t = HOTBAR[sel]; if(TOOLS[t] && wear[t]) wear[t] = wear[t].map(()=>TOOLS[t].dur);
}
let talkNpc = null, talkView = 'talk', talkLine = '', talkOffer = null;""")
rep("    h += `<button data-a=\"work\">ASK FOR WORK</button>`;", """    h += `<button data-a="work">ASK FOR WORK</button>`;
    if(TRAINS[m.job]) h += `<button data-a="train">TRAIN ${SKILLS.find(k=>k.id===TRAINS[m.job]).name.toUpperCase()} (${trainCost(TRAINS[m.job])}g)</button>`;
    if(m.job==='blacksmith'){ const rc = repairCost(); if(rc>0) h += `<button data-a="repair">REPAIR (${rc}g)</button>`; }""")
rep("  else if(a==='news'){ talkLine = talkNews(m); }", """  else if(a==='news'){ talkLine = talkNews(m); }
  else if(a==='train'){
    const id = TRAINS[m.job], K = SKILLS.find(k=>k.id===id), cost = trainCost(id);
    if(skills[id]>=TRAIN_CAP) talkLine = `You know as much of ${K.name.toLowerCase()} as I can teach. The rest you'll learn by doing.`;
    else if(trainedDay[m.home]===dayNo) talkLine = 'That\\'s enough for one day. Come back tomorrow.';
    else if(gold<cost) talkLine = `A lesson costs ${cost} gold. You have ${gold}.`;
    else { gold -= cost; trainedDay[m.home] = dayNo; skillUses[id] = skillUsesFor(id); trainSkill(id, 0); talkLine = `An afternoon's practice. Your ${K.name.toLowerCase()} is now ${skills[id]}. (${cost} gold)`; }
  }
  else if(a==='repair'){ const rc = repairCost(); if(gold<rc) talkLine = `That'll be ${rc} gold. You have ${gold}.`; else { gold -= rc; doRepair(); talkLine = `Good as new. (${rc} gold)`; } }""")
rep("gold, armor, cls:playerClass,", "gold, armor, trained:trainedDay, cls:playerClass,")
rep("  gold = meta.gold || 0; playerClass", "  trainedDay = meta.trained || {};\n  gold = meta.gold || 0; playerClass")
open(p,'w').write(s); print('ok')
