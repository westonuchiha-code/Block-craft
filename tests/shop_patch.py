p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
mod = r'''
// ---------- talking and trading (Daggerfall-style: gold, shopkeepers by trade, a temple that heals) ----------
// Use a villager to talk. What they sell and buy comes from their job; they sell at full price and buy at 40%.
// Shops shut at night. A cleric heals you for gold. Anyone can tell you where the next village lies.
const PRICE = {};
{ const P = (ids,v)=>{ for(const id of [].concat(ids)) PRICE[id] = v; };
  P([SEEDS, ...CROPDEFS.map(d=>d.seed).filter(Boolean)], 2); P([WHEAT,CARROT,POTATO,ONION,TOMATO,PEPPER], 3); P([CORN_EAR,GRAPES,MELON_SLICE], 4); P(PUMPKIN, 6);
  P(FLOUR, 5); P(HAY, 6); P(STICK, 1); P(PLANKS, 2); P(COAL_ITEM, 4); P([COBBLE, SAND], 1); P([STONE, ANDESITE, GRANITE, DIORITE, TUFF], 2); P(GLASS, 4);
  P(BOOKSHELF, 30); P(CANDLE, 6); P(LANTERN0+1, 20); P(BARS0, 8); P(WOOD_BUCKET, 10); P(WATER_BUCKET, 12); P(BED0, 40); P(WOOL0, 6); P(LITTER, 1); P(BONE, 3);
  P(CATNIP_SEED, 20); P(CRAFT_TABLE, 8); P(COOK_TABLE, 25); P([FIRE_POTION, BOLT_POTION], 40); P(EMBER, 60); P(CROSSBOW, 150); P(PISTOL, 220);
  P([WOOD_PICK,WOOD_AXE,WOOD_SHOVEL,WOOD_HOE], 15); P(WOOD_SWORD, 20); P([STONE_PICK,STONE_AXE,STONE_SHOVEL,STONE_HOE], 35); P(STONE_SWORD, 45);
  P(LEATHER, 12); P(RAW_MEAT, 6); P(STEAK, 12); P(MEAT_STEW, 30); P(SILK, 4); P(CHITIN, 15); P(GLOWMOSS, 10);
  for(let i=0;i<11;i++) PRICE[DYE0+i] = 5;
  for(const d of DISHES) PRICE[d.id] = 8 + FOOD_VAL[d.id]*2; }
const CROPS_SOLD = [WHEAT,CARROT,POTATO,ONION,TOMATO,PEPPER,CORN_EAR,GRAPES,MELON_SLICE,PUMPKIN];
const SHOPS = {
  farmer:     { title:'Farm goods', sell:[SEEDS, ...CROPDEFS.map(d=>d.seed).filter(Boolean).slice(0,6), WHEAT, CARROT, POTATO, HAY, WOOD_HOE, STONE_HOE], buy:[...CROPS_SOLD, HAY] },
  baker:      { title:'Bakery', sell:[FLOUR, ...DISHES.map(d=>d.id), STEAK, MEAT_STEW], buy:[...CROPS_SOLD, FLOUR, RAW_MEAT] },
  blacksmith: { title:'Smithy', sell:[WOOD_PICK, WOOD_AXE, WOOD_SWORD, STONE_PICK, STONE_AXE, STONE_SHOVEL, STONE_SWORD, BARS0, LANTERN0+1, WOOD_BUCKET, CROSSBOW, PISTOL],
                buy:[COAL_ITEM, LEATHER, CHITIN, BONE, WOOD_PICK, WOOD_AXE, WOOD_SWORD, STONE_PICK, STONE_AXE, STONE_SWORD] },
  miner:      { title:'Quarry goods', sell:[COAL_ITEM, COBBLE, STONE, ANDESITE, GRANITE, DIORITE, STONE_PICK], buy:[COAL_ITEM, COBBLE, STONE, ANDESITE, GRANITE, DIORITE, TUFF, EMBER] },
  librarian:  { title:'Scholar\'s wares', sell:[BOOKSHELF, CANDLE, GLASS, FIRE_POTION, BOLT_POTION, ...[0,1,2,3,4,5].map(i=>DYE0+i)], buy:[GLOWMOSS, EMBER, SILK, BONE] },
  cleric:     { title:'Temple offerings', sell:[FIRE_POTION, BOLT_POTION, CANDLE, LANTERN0+1], buy:[GLOWMOSS, EMBER, BONE, CANDLE], heal:true },
  fisher:     { title:'Fisher\'s stall', sell:[WOOD_BUCKET, WATER_BUCKET, RAW_MEAT, STEAK], buy:[RAW_MEAT, LEATHER, SILK] },
  villager:   { title:'Odds and ends', sell:[STICK, PLANKS, CRAFT_TABLE, BED0, WOOL0, CANDLE], buy:[SILK, WOOL0, LEATHER, LITTER, HAY] }
};
const JOB_TITLE = { farmer:'Farmer', baker:'Baker', blacksmith:'Smith', miner:'Miner', librarian:'Scholar', cleric:'Cleric', fisher:'Fisher', villager:'Villager', guard:'Guard' };
const GREET = {
  guard:['Keep your blade sheathed inside the walls.','Move along, traveller.','The beasts grow bold near the woods. Stay sharp.'],
  cleric:['The gods keep watch over this place.','Wounded? The temple can mend you, for a donation.'],
  blacksmith:['Need a sharper edge?','Mind the forge, it bites.'],
  baker:['Fresh from the oven this morning.','Hungry? I have just the thing.'],
  farmer:['Good soil this year.','The crows have been at my seeds again.'],
  miner:['There\'s coal in every hill, if you dig deep enough.','Watch for rats down in the tunnels.'],
  librarian:['Knowledge is the sharpest weapon.','Mind the books. They are older than you.'],
  fisher:['The water\'s calm today.','I trade in whatever the hunt brings in.'],
  villager:['Fine day, isn\'t it?','Welcome, stranger.','Not many travellers come through here.']
};
const DIR8 = ['north','north-east','east','south-east','south','south-west','west','north-west'];
function talkNews(m){
  const [rx,rz] = m.village || [Math.floor(m.x/VREG), Math.floor(m.z/VREG)], here = villageAt(rx,rz), hc = here ? villageCentre(here) : [m.x,m.z];
  let best = null, bd = 1e9;
  for(let a=-3;a<=3;a++) for(let b=-3;b<=3;b++){ if(!a && !b) continue; const v = villageAt(rx+a, rz+b); if(!v || !v.houses) continue;
    const c = villageCentre(v), d = Math.hypot(c[0]-hc[0], c[1]-hc[1]); if(d<bd){ bd = d; best = c; } }
  const lines = [];
  if(best){ const ang = Math.atan2(best[0]-hc[0], -(best[1]-hc[1])), k = ((Math.round(ang/(Math.PI/4))%8)+8)%8;          // -z is north
    lines.push(`The nearest village lies about ${Math.round(bd/10)*10} paces to the ${DIR8[k]}.`); }
  else lines.push('No other village for many days\' walk, they say.');
  const kinds = new Set(); for(const o of mobs) if(BEAST[o.kind] && Math.hypot(o.x-m.x,o.z-m.z)<70) kinds.add(o.kind);
  const nm = { bear:'a grizzly bear', tiger:'a sabertooth', spider:'giant spiders', scorpion:'a giant scorpion' };
  if(kinds.size) lines.push(`Folk have seen ${[...kinds].map(k=>nm[k]).join(' and ')} close by. Be careful out there.`);
  const b = biomeAt(Math.floor(m.x), Math.floor(m.z));
  lines.push(b===3 ? 'Tigers hunt the frozen lands. They will not wait for you to strike first.' : b===4 ? 'Scorpions lurk in the sands. Their sting will drop a grown man.' : 'Bears roam these woods. Leave them be and they will leave you be, mostly.');
  return lines.join(' ');
}
let talkNpc = null, talkView = 'talk', talkLine = '';
function openTalk(m){
  if(paused || craftOpen || m.angry>0 || m.dead) return false;
  talkNpc = m; talkView = 'talk'; m.talkT = 0;
  const g = GREET[m.job] || GREET.villager; talkLine = g[Math.floor(Math.random()*g.length)];
  craftOpen = true;
  m.yaw = Math.atan2(player.x-m.x, -(player.z-m.z)); m.path = null; m.state = 'idle'; m.idleT = 6;
  renderTalk(); document.getElementById('talkMenu').classList.add('show');
  if(document.pointerLockElement) document.exitPointerLock();
  return true;
}
function closeTalk(){ talkNpc = null; craftOpen = false; document.getElementById('talkMenu').classList.remove('show'); scheduleSave(); }
function sellPrice(id){ return Math.max(1, Math.floor((PRICE[id]||1)*0.4)); }
function renderTalk(){
  const m = talkNpc; if(!m) return;
  const shop = SHOPS[m.job], el = document.getElementById('talkBody');
  document.getElementById('talkName').textContent = m.name + ' — ' + (JOB_TITLE[m.job]||'Villager');
  document.getElementById('talkGold').textContent = gold + ' gold';
  let h = '';
  if(talkView==='talk'){
    h += `<div class="tkLine">“${talkLine}”</div><div class="tkBtns">`;
    if(shop) h += `<button data-a="trade">TRADE</button>`;
    if(shop && shop.heal) h += `<button data-a="heal">HEALING</button>`;
    h += `<button data-a="news">ASK FOR NEWS</button><button data-a="bye">GOODBYE</button></div>`;
  } else {
    const closed = ratNight;
    h += `<div class="tkTabs"><button data-a="back">← TALK</button><b>${shop.title}</b></div>`;
    if(closed) h += `<div class="tkLine">“We're closed for the night. Come back in the morning.”</div>`;
    else {
      h += `<div class="tkHd">THEY SELL</div>`;
      for(const id of shop.sell){ const pr = PRICE[id]||1;
        h += `<div class="tkRow"><span class="tkIc" data-ic="${id}"></span><span class="tkNm">${NAMES[id]}</span><span class="tkPr">${pr}g</span><button data-buy="${id}" ${gold<pr?'disabled':''}>BUY</button></div>`; }
      const mine = shop.buy.filter(id=>(inv[id]||0)>0);
      h += `<div class="tkHd">THEY BUY FROM YOU</div>`;
      if(!mine.length) h += `<div class="tkNote">You have nothing they want. They buy: ${shop.buy.slice(0,6).map(id=>NAMES[id]).join(', ')}…</div>`;
      for(const id of mine) h += `<div class="tkRow"><span class="tkIc" data-ic="${id}"></span><span class="tkNm">${NAMES[id]} ×${inv[id]}</span><span class="tkPr">${sellPrice(id)}g</span><button data-sell="${id}">SELL</button></div>`;
    }
  }
  el.innerHTML = h;
  el.querySelectorAll('[data-ic]').forEach(sp=>sp.appendChild(iconCanvas(+sp.dataset.ic)));
}
function talkAction(a){
  const m = talkNpc; if(!m) return;
  if(a==='bye'){ closeTalk(); return; }
  if(a==='trade'){ talkView = 'trade'; }
  else if(a==='back'){ talkView = 'talk'; }
  else if(a==='news'){ talkLine = talkNews(m); }
  else if(a==='heal'){
    const need = maxHP()-health, cost = need*3;
    if(need<=0) talkLine = 'You are whole. Go with the gods.';
    else if(gold<cost) talkLine = `Healing your wounds asks a donation of ${cost} gold. You have ${gold}.`;
    else { gold -= cost; health = maxHP(); vitalKey = ''; talkLine = `The light mends you. (${cost} gold)`; }
  }
  renderTalk();
}
function talkBuy(id){
  const pr = PRICE[id]||1; if(gold<pr || ratNight) return;
  gold -= pr; inv[id] = Math.min(999, (inv[id]||0)+1); autoFillHotbar(id); scheduleSave(); renderTalk();
}
function talkSell(id){
  if(!(inv[id]>0) || ratNight) return;
  inv[id]--; gold += sellPrice(id); trainSkill('speech', 0); scheduleSave(); renderTalk();
}
'''
rep("// ---------- villagers: everyone in a village lives", mod+"// ---------- villagers: everyone in a village lives")
# no 'speech' skill: remove that call
s = s.replace(" trainSkill('speech', 0);", "")
# open talk with the use button, before anything else
rep("function placeBlock(){\n  if(dead) return;\n", """function placeBlock(){
  if(dead) return;
  { const {f} = camVectors(), mh = ratRay(player.x, player.y+1.6, player.z, f[0],f[1],f[2], 3.6), hit = target();
    if(mh && mh.m.kind==='npc' && (!hit || mh.t < Math.hypot(hit.x+0.5-player.x, hit.y+0.5-player.y-1.6, hit.z+0.5-player.z)) && openTalk(mh.m)) return; }   // use on a villager: talk
""")
rep("function closeCraft(){\n  if(chestOpen){ closeChest(); return; }", "function closeCraft(){\n  if(talkNpc){ closeTalk(); return; }\n  if(chestOpen){ closeChest(); return; }")
rep('<div id="skillToast"></div>', '''<div id="skillToast"></div>
<div id="talkMenu"><div id="talkPanel"><div id="talkTop"><h2 id="talkName"></h2><span id="talkGold"></span></div><div id="talkBody"></div></div></div>''')
rep("  #skillMenu.show { display:flex; }", """  #skillMenu.show { display:flex; }
  #talkMenu { position:fixed; inset:0; z-index:21; display:none; align-items:center; justify-content:center; color:#d8cfb8; font-family:monospace; background:rgba(0,0,0,.6); }
  #talkMenu.show { display:flex; }
  #talkPanel { width:min(94vw,480px); max-height:90vh; overflow-y:auto; padding:12px 14px; box-sizing:border-box; background:linear-gradient(#1b1d18,#0f100e); border:2px solid #050605; box-shadow:inset 0 0 0 1px #8c7640, 0 0 24px #000; }
  #talkTop { display:flex; align-items:baseline; justify-content:space-between; gap:8px; margin-bottom:8px; }
  #talkTop h2 { margin:0; color:#e3cf95; letter-spacing:2px; font-size:16px; } #talkGold { color:#ecc440; font-size:13px; white-space:nowrap; }
  .tkLine { font-size:14px; line-height:1.45; padding:8px 4px 12px; color:#e8e0cc; }
  .tkBtns { display:flex; flex-wrap:wrap; gap:6px; }
  #talkBody button { font:12px monospace; letter-spacing:1px; padding:8px 10px; background:linear-gradient(#34372f,#1d1f1a); color:#e3cf95; border:2px solid #050605; box-shadow:inset 0 0 0 1px #8c7640; }
  #talkBody button:disabled { opacity:.35; }
  .tkTabs { display:flex; align-items:center; gap:10px; margin-bottom:6px; } .tkTabs b { color:#e3cf95; letter-spacing:1px; }
  .tkHd { font-size:11px; color:#8f8a7a; letter-spacing:2px; margin:10px 0 4px; border-bottom:1px solid #2a2c26; padding-bottom:3px; }
  .tkRow { display:flex; align-items:center; gap:8px; padding:3px 0; } .tkIc canvas { width:24px; height:24px; image-rendering:pixelated; display:block; }
  .tkNm { flex:1; font-size:13px; } .tkPr { color:#ecc440; font-size:13px; min-width:42px; text-align:right; }
  #talkBody .tkRow button { padding:5px 10px; }
  .tkNote { font-size:11px; color:#8f8a7a; }""")
rep("document.getElementById('skillBtn').addEventListener('click', openSkills);", """document.getElementById('skillBtn').addEventListener('click', openSkills);
document.getElementById('talkBody').addEventListener('click', e=>{ const b = e.target.closest('button'); if(!b || b.disabled) return;
  if(b.dataset.a) talkAction(b.dataset.a); else if(b.dataset.buy) talkBuy(+b.dataset.buy); else if(b.dataset.sell) talkSell(+b.dataset.sell); });""")
# villager being talked to stays still
rep("function updateNpc(m, dt){\n  let walking = false;", "function updateNpc(m, dt){\n  let walking = false;\n  if(talkNpc===m){ m.moving = false; m.path = null; m.yaw = Math.atan2(player.x-m.x, -(player.z-m.z)); m.limb *= 0.8; const P = m.pose; P.c = Math.cos(m.yaw); P.s = Math.sin(m.yaw); P.ra=P.la=P.rl=P.ll=0; return; }")
open(p,'w').write(s); print('ok')
