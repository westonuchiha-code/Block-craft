p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
# ===== pistol out =====
rep("[CROSSBOW,1,1,.15],[PISTOL,1,1,.1],", "[CROSSBOW,1,1,.2],")
rep("[PISTOL]:1,[CROSSBOW", "[CROSSBOW")
rep("Object.keys(TOOLS).map(Number), PISTOL, CROSSBOW,", "Object.keys(TOOLS).map(Number), CROSSBOW,")
rep("drop(Math.random()<0.5 ? PISTOL : CROSSBOW,1);", "drop(CROSSBOW,1);", 2)
rep("STONE_SWORD, BARS0, LANTERN0+1, WOOD_BUCKET, CROSSBOW, PISTOL],", "STONE_SWORD, BARS0, LANTERN0+1, WOOD_BUCKET, CROSSBOW],")
i=s.index("  { name:'Flintlock pistol',"); j=s.index("\n",i); s=s[:i]+s[j+1:]
rep("desc:'damage with swords, axes, tools, pistols and crossbows' }", "desc:'damage with swords, axes, tools and crossbows' }")
# ===== new skills =====
rep("  { id:'stealth',   name:'Stealth',      base:5, desc:'while sneaking, creatures notice you later' }\n];",
"""  { id:'stealth',   name:'Stealth',      base:5, desc:'while sneaking, creatures notice you later' },
  { id:'mining',    name:'Mining',       base:10, desc:'faster pickaxe work on stone and ore, and sometimes extra ore. Only rock that was already in the world counts' },
  { id:'woodcut',   name:'Woodcutting',  base:8, desc:'faster chopping, and sometimes an extra log. Only trees that grew in the world count' },
  { id:'farming',   name:'Farming',      base:4, desc:'bigger harvests from ripe crops and woolbloom plants' },
  { id:'alchemy',   name:'Cooking & Alchemy', base:3, desc:'cooked food fills you more; a brew sometimes makes two' }
];""")
# placed-by-player memory
rep("let skills = {}, skillUses = {}, skillGained = 0,", "let placedSet = new Set();                 // blocks you put there yourself: breaking them teaches nothing\nlet skills = {}, skillUses = {}, skillGained = 0,")
rep("  setB(x,y,z,placeId);\n  if(placeId===CHEST) chests.set(", "  setB(x,y,z,placeId); placedSet.add(x+','+y+','+z);\n  if(placeId===CHEST) chests.set(")
# mining / woodcutting speed
rep("""  const speed = tool ? TOOLS[tool].speed : 1;
  return Math.max(1, Math.ceil(h * (canHarvest(b, tool) ? 2 : 5) / speed));""",
"""  let speed = tool ? TOOLS[tool].speed : 1;
  if(tool && TOOLS[tool].kind==='pick' && REQ_TIER[b]!==undefined) speed *= 1 + skills.mining/100*0.6;        // Mining: up to 60% quicker
  if(IS_LOG[b] && tool && TOOLS[tool].kind==='axe') speed *= 1 + skills.woodcut/100*0.6;                      // Woodcutting
  return Math.max(1, Math.ceil(h * (canHarvest(b, tool) ? 2 : 5) / speed));""")
# breaking: training + bonuses
rep("function breakNow(hit, tool){\n  if(hit.b===CHEST) spillChest(hit.x,hit.y,hit.z);",
"""function breakNow(hit, tool){
  const pk = hit.x+','+hit.y+','+hit.z, natural = !placedSet.delete(pk);
  if(natural && tool && TOOLS[tool].kind==='pick' && REQ_TIER[hit.b]!==undefined){
    trainSkill('mining');
    const d = (hit.b in DROP) ? DROP[hit.b] : hit.b;
    if(d && d!==hit.b && d!==COBBLE && Math.random() < skills.mining/250) spawnDrop(hit.x,hit.y,hit.z,d);      // a skilled miner finds a little more ore
  }
  if(natural && IS_LOG[hit.b]){ trainSkill('woodcut'); if(Math.random() < skills.woodcut/250) spawnDrop(hit.x,hit.y,hit.z,hit.b); }
  if(hit.b===CHEST) spillChest(hit.x,hit.y,hit.z);""")
# farming
rep("""    if(d.produce){ const n = roll(d.produce[1],d.produce[2]); for(let i=0;i<n;i++) spawnDrop(x,y,z,d.produce[0]); }""",
"""    if(d.produce){ const n = roll(d.produce[1],d.produce[2]) + (Math.random() < skills.farming/200 ? 1 : 0); for(let i=0;i<n;i++) spawnDrop(x,y,z,d.produce[0]); }
    if(m===0) trainSkill('farming');""")
rep("  if(hit.b===WBP0+2) for(let n=roll(1,3);n>0;n--) spawnDrop(hit.x,hit.y,hit.z,WOOL0);", "  if(hit.b===WBP0+2){ trainSkill('farming'); for(let n=roll(1,3)+(Math.random()<skills.farming/200?1:0);n>0;n--) spawnDrop(hit.x,hit.y,hit.z,WOOL0); }")
# cooking & alchemy: cooking trains it; potions can be brewed at the cooking table
rep("""  inv[out[0]] = Math.min(99, (inv[out[0]]||0) + out[1]);
  grid2 = new Array(9).fill(0);          // the ingredients are used up""",
"""  let n = out[1];
  if(craftMode==='cook'){ trainSkill('alchemy'); if((out[0]===FIRE_POTION || out[0]===BOLT_POTION) && Math.random() < skills.alchemy/200) n++; }
  inv[out[0]] = Math.min(99, (inv[out[0]]||0) + n);
  grid2 = new Array(9).fill(0);          // the ingredients are used up""")
rep("COOK_RECIPES.push({ name:'steak', out:[STEAK,1], ing:{[RAW_MEAT]:1}, list:[RAW_MEAT], back:null });",
"""COOK_RECIPES.push({ name:'steak', out:[STEAK,1], ing:{[RAW_MEAT]:1}, list:[RAW_MEAT], back:null });
// brewing: the cooking table doubles as an alchemist's bench
COOK_RECIPES.push({ name:'fire potion', out:[FIRE_POTION,1], ing:{[EMBER]:1,[WATER_BUCKET]:1}, list:[EMBER,WATER_BUCKET].sort((a,b)=>a-b), back:[WOOD_BUCKET,1] });
COOK_RECIPES.push({ name:'lightning potion', out:[BOLT_POTION,1], ing:{[GLOWMOSS]:2,[WATER_BUCKET]:1}, list:[GLOWMOSS,GLOWMOSS,WATER_BUCKET].sort((a,b)=>a-b), back:[WOOD_BUCKET,1] });""")
rep("      food = Math.min(20, food + FOOD_VAL[id]);", "      const cooked = DISHES.some(d=>d.id===id) || id===STEAK || id===MEAT_STEW;\n      food = Math.min(20, food + Math.round(FOOD_VAL[id]*(cooked ? 1 + skills.alchemy/200 : 1)));      // Cooking & Alchemy: cooked food fills you more")
# flat items are never drawn as cubes when dropped
rep("    if(COLORS[e.id] && !IS_SHAPED[e.id]){\n      drawSpinningBlock(", "    if(COLORS[e.id] && !IS_SHAPED[e.id] && !FLAT_ITEMS.has(e.id)){\n      drawSpinningBlock(")
# ===== death sack =====
rep("function die(){\n  dead = true; health = 0;", """// ---------- dying: everything you carry goes into a sack that floats where you fell, under a beam of light you can see from afar ----------
let deathSacks = [];
function dropSack(){
  const items = {}; let any = false;
  for(const k in inv){ if(inv[k]>0){ items[k] = inv[k]; any = true; } }
  if(!any) return;
  syncWear();
  const w = {}; for(const k in wear) w[k] = wear[k].slice();
  let y = player.y + 0.5; if(y<1) y = 1;
  deathSacks.push({ x:player.x, y, z:player.z, items, wear:w, day:dayNo });
  for(const k in inv) delete inv[k];
  for(const k in wear) delete wear[k];
  scheduleSave();
}
function updateSacks(){
  for(let i=deathSacks.length-1;i>=0;i--){
    const s = deathSacks[i];
    if(dead || Math.hypot(player.x-s.x, player.z-s.z)>1.6 || Math.abs(player.y+0.9-s.y)>2.2) continue;
    for(const k in s.items){ inv[k] = Math.min(999, (inv[k]||0)+s.items[k]); autoFillHotbar(+k); }
    for(const k in s.wear){ wear[k] = (wear[k]||[]).concat(s.wear[k]); }
    syncWear(); deathSacks.splice(i,1);
    skillToast('BELONGINGS RECOVERED', true); scheduleSave();
  }
}
// the sack itself (a bobbing icon) and its beam: a tall column of light, hidden only where something stands in front of it
function drawSacks(){
  if(!deathSacks.length) return;
  const f=CAM.f, r=CAM.r, u=CAM.u, ex=CAM.x, ey=CAM.y, ez=CAM.z, t = performance.now()/1000;
  for(const s of deathSacks){
    const by = s.y + Math.sin(t*2)*0.08;
    const b0 = projectPt([s.x,by,s.z], f, r, u, ex, ey, ez), b1 = projectPt([s.x,by+64,s.z], f, r, u, ex, ey, ez);
    if(b0.zc>0.3 && b1.zc>0.3){
      const wpx = Math.max(1.5, 0.5*(RH/2)/(b0.zc*TAN)), steps = Math.ceil(Math.hypot(b1.px-b0.px, b1.py-b0.py));
      const pulse = 0.55 + 0.2*Math.sin(t*3);
      for(let k=0;k<=steps;k++){
        const a = k/Math.max(1,steps), px = b0.px+(b1.px-b0.px)*a, py = b0.py+(b1.py-b0.py)*a, zc = b0.zc+(b1.zc-b0.zc)*a;
        const ix = Math.floor(px), iy = Math.floor(py);
        if(ix<0 || iy<0 || ix>=RW || iy>=RH) continue;
        if(depthBuf[iy*RW+ix] < zc-0.3) continue;
        const fade = (1-a)*pulse, w = Math.max(1, wpx*(1-a*0.5));
        ctx.fillStyle = `rgba(255,226,140,${(fade*0.55).toFixed(3)})`; ctx.fillRect(px-w, py, w*2, 1.2);
        ctx.fillStyle = `rgba(255,250,220,${(fade*0.8).toFixed(3)})`; ctx.fillRect(px-w*0.35, py, w*0.7, 1.2);
      }
    }
    if(b0.zc>0.3 && b0.zc<60){
      const ix = Math.floor(b0.px), iy = Math.floor(b0.py);
      if(ix>=0 && iy>=0 && ix<RW && iy<RH && depthBuf[iy*RW+ix] >= b0.zc-0.3){
        const size = Math.max(3, 0.6*(RH/2)/(b0.zc*TAN));
        ctx.imageSmoothingEnabled = false; ctx.drawImage(iconSrc(SACK), b0.px-size/2, b0.py-size/2, size, size);
      }
    }
  }
}
function die(){
  dropSack();
  dead = true; health = 0;""")
rep("  drawItems();\n", "  drawItems();\n  drawSacks();\n", 1)
rep("function updateItems(){\n", "function updateItems(){\n  updateSacks();\n")
rep("const LEATHER = 1081, RAW_MEAT = 1082,", "const SACK = 1089;  // a dead adventurer's belongings (never in the inventory)\nconst LEATHER = 1081, RAW_MEAT = 1082,")
rep("    case PARCEL: paintIcon(g,(P,E)=>{", """    case SACK: paintIcon(g,(P,E)=>{ E(8,10,5.6,4.6,null,(x,y,dx,dy)=>dx<-0.3&&dy<-0.1 ? [178,140,92] : dy>0.55 ? [104,76,46] : [146,110,70]);
              for(let x=6;x<=10;x++){ P(x,4,[146,110,70]); P(x,5,[120,90,56]); } P(7,3,[146,110,70]); P(9,3,[146,110,70]); for(let x=5;x<=11;x++) P(x,6,[196,160,70]); P(8,10,[90,64,38]); }); return true;
    case PARCEL: paintIcon(g,(P,E)=>{""")
# where your belongings are, in the character sheet
rep("  if(!quests.length) h = '<div class=\"skNote\">No work taken. Talk to villagers and ask them for work.</div>';",
    "  for(const sk of deathSacks) h += `<div class=\"skRow\"><div class=\"skHead\"><b style=\"color:#ffe28c\">Your lost belongings</b></div><div class=\"skDesc\" style=\"color:#d8cfb8\">A sack of everything you carried lies ${far(sk.x,sk.z)}. Look for the beam of light.</div></div>`;\n  if(!quests.length) h += '<div class=\"skNote\">No work taken. Talk to villagers and ask them for work.</div>';")
# save / load
rep("gold, cls:playerClass,", "gold, cls:playerClass, sacks:deathSacks, placed:[...placedSet],")
rep("  gold = meta.gold || 0; playerClass = meta.cls || null;", "  gold = meta.gold || 0; playerClass = meta.cls || null; deathSacks = meta.sacks || []; placedSet = new Set(meta.placed || []);\n  if(meta.inv && meta.inv[PISTOL]) delete inv[PISTOL];          // the pistol is gone from the world")
open(p,'w').write(s); print('ok')
