p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
rep("function newBeast(kind,x,y,z){\n  return { id:mobId++, kind, x:x+0.5, y, z:z+0.5, yaw:Math.random()*6.28, hp:BEAST[kind].hp, variant:0,",
r"""// ---------- danger: the world grows harsher the further you go from where you began, and the deeper you dig ----------
// Six bands of land around the world's centre, each about 450 paces wide; going deep (below 14) or into the underworld adds more.
// Every creature carries the danger of the place it was born: more health, harder blows, better spoils. Quest beasts and Crypt
// Lords also grow with you, so the work villagers give you keeps pace as you level.
const DANGER_NAMES = ['the Heartlands','the Borderlands','the Wildlands','the Darklands','the Deep Wilds','the Forsaken Reaches'];
function dangerAt(x,y,z){
  if(testWorld || isTestZ(z)) return 0;
  if(isUnder(z)) return 4;
  let t = Math.min(5, Math.floor(Math.hypot(x,z)/450));
  if(y<14) t++;
  return Math.min(5, t);
}
function lvlHp(base, lvl){ return Math.round(base*(1 + 0.35*lvl)); }
function lvlDmg(base, lvl){ return Math.round(base*(1 + 0.25*(lvl||0))*2)/2; }
function newBeast(kind,x,y,z,lvl){
  if(lvl===undefined) lvl = dangerAt(x,y,z);
  return { id:mobId++, kind, lvl, x:x+0.5, y, z:z+0.5, yaw:Math.random()*6.28, hp:lvlHp(BEAST[kind].hp, lvl), variant:0,""")
rep("      if(m.atkCd<=0){ hurt(K.bite); m.atkCd = K.cd; m.atkA = 1; }", "      if(m.atkCd<=0){ hurt(lvlDmg(K.bite, m.lvl)); m.atkCd = K.cd; m.atkA = 1; }")
rep("if(m.atkCd<=0){ mobDamage(o, K.bite, m); m.atkCd = K.cd; m.atkA = 1; } return; }", "if(m.atkCd<=0){ mobDamage(o, lvlDmg(K.bite, m.lvl), m); m.atkCd = K.cd; m.atkA = 1; } return; }")
rep("    for(const [id,lo,hi] of K.drops) for(let n=roll(lo,hi)+(isClass('ranger') && !K.undead ? 1 : 0); n>0; n--) spawnDrop(x,y,z,id);\n    if(K.gold) spawnGold(x,y,z,roll(K.gold[0],K.gold[1]));",
    "    const L = m.lvl||0;\n    for(const [id,lo,hi] of K.drops) for(let n=roll(lo,hi)+(isClass('ranger') && !K.undead ? 1 : 0)+(Math.random() < L*0.2 ? 1 : 0); n>0; n--) spawnDrop(x,y,z,id);     // tougher beasts, richer spoils\n    if(K.gold) spawnGold(x,y,z,Math.round(roll(K.gold[0],K.gold[1])*(1+0.25*L)));")
# brutes and rats
rep("  return { id:mobId++, kind, x:x+0.5, y, z:z+0.5, yaw:Math.random()*6.28, hp:BRUTE[kind].hp, age:0,",
    "  const lvl = dangerAt(x,y,z);\n  return { id:mobId++, kind, lvl, x:x+0.5, y, z:z+0.5, yaw:Math.random()*6.28, hp:lvlHp(BRUTE[kind].hp, Math.max(0,lvl-1)), age:0,")
rep("if(!dead && dist<K.hitR && dy<4.5){ hurt(K.dmg);", "if(!dead && dist<K.hitR && dy<4.5){ hurt(lvlDmg(K.dmg, Math.max(0,(m.lvl||0)-1)));")
rep("  return { id:mobId++, kind:'rat', x:x+0.5, y, z:z+0.5, yaw:Math.random()*6.28, hp:RAT_HP,", "  const lvl = Math.floor(dangerAt(x,y,z)/2);\n  return { id:mobId++, kind:'rat', lvl, x:x+0.5, y, z:z+0.5, yaw:Math.random()*6.28, hp:lvlHp(RAT_HP, lvl),")
rep("        if(m.atkCd<=0){ hurt(RAT_BITE); m.atkCd = 0.8; }", "        if(m.atkCd<=0){ hurt(lvlDmg(RAT_BITE, m.lvl)); m.atkCd = 0.8; }")
# more creatures in wilder lands
rep("  if(total>=BEAST_TOTAL || Math.random()>0.6) return;", "  const dl = dangerAt(player.x, player.y, player.z);\n  if(total>=BEAST_TOTAL + Math.min(3, dl) || Math.random()>0.6 + dl*0.06) return;")
# quests keep pace with you: dens and crypt lords scale with your level, rewards too
rep("      const m = newBeast(q.beast,x,y,z); m.hp = Math.round(m.hp*1.5); m.questId = q.id; mobs.push(m); break;",
    "      const m = newBeast(q.beast,x,y,z, Math.max(dangerAt(x,y,z), Math.floor(playerLevel()/5))); m.hp = Math.round(m.hp*1.5); m.questId = q.id; mobs.push(m); break;")
rep("    if(!cleared){ const L = newBeast('cryptlord', P.boss[0], P.boss[1], P.boss[2]); L.crypt = P.key; mobs.push(L); }",
    "    if(!cleared){ const L = newBeast('cryptlord', P.boss[0], P.boss[1], P.boss[2], Math.max(dangerAt(P.ex,P.h,P.ez), Math.floor(playerLevel()/4))); L.crypt = P.key; mobs.push(L); }")
rep("function acceptQuest(m, q){\n  if(quests.length>=QUEST_MAX) return 'You already have as much work as you can carry.';",
    "function acceptQuest(m, q){\n  if(quests.length>=QUEST_MAX) return 'You already have as much work as you can carry.';\n  if(!q.scaled){ q.reward = Math.round(q.reward*(1 + 0.08*(playerLevel()-1))); q.scaled = 1; }        // seasoned adventurers get paid more")
rep("    const a = rnd()*6.283, d = 70+rnd()*90,", "    const a = rnd()*6.283, d = 70+rnd()*90 + Math.min(250, (playerLevel()-1)*15),")
# offers show the scaled reward
rep("    else { talkOffer = questOffer(m); talkLine = talkOffer.text; }", "    else { talkOffer = questOffer(m); const r0 = talkOffer.reward; talkOffer.reward = Math.round(r0*(1 + 0.08*(playerLevel()-1))); talkOffer.scaled = 1; talkLine = talkOffer.text.replace(r0+' gold', talkOffer.reward+' gold'); }")
# entering a wilder band: a quiet warning; the map and sheet name the land
rep("function exploreTick(){\n  if(testWorld || isUnder(player.z) || isTestZ(player.z)) return;", """let lastDanger = -1;
function exploreTick(){
  if(testWorld || isUnder(player.z) || isTestZ(player.z)) return;
  { const d = Math.min(5, Math.floor(Math.hypot(player.x,player.z)/450));
    if(lastDanger>=0 && d>lastDanger) skillToast(DANGER_NAMES[d].toUpperCase()+'<br><small>the land grows more dangerous</small>', true);
    else if(lastDanger>=0 && d<lastDanger) skillToast(DANGER_NAMES[d].toUpperCase()+'<br><small>safer country</small>', true);
    lastDanger = d; }""")
rep("  let h = `<div class=\"skNote\">${here ? 'You are at '+here.name+'.' : 'Wagons leave from villages and homesteads.'} Tap a place to travel there.</div>`;",
    "  const dz = dangerAt(player.x, player.y, player.z);\n  let h = `<div class=\"skNote\">You are in ${DANGER_NAMES[Math.min(5,Math.floor(Math.hypot(player.x,player.z)/450))]} (danger ${dz}). ${here ? 'You are at '+here.name+'.' : 'Wagons leave from villages and homesteads.'} Tap a place to travel there.</div>`;")
# map: faint rings marking the bands
rep("  g.font = 'bold 11px monospace'; g.textAlign = 'center';\n  const mark =", """  g.strokeStyle = 'rgba(224,80,64,0.35)'; g.lineWidth = 1; g.setLineDash([4,4]);
  for(let k=1;k<=5;k++){ const [cx0,cy0] = toS(0,0); g.beginPath(); g.arc(cx0, cy0, k*450*S, 0, Math.PI*2); g.stroke(); }
  g.setLineDash([]);
  g.font = 'bold 11px monospace'; g.textAlign = 'center';
  const mark =""")
open(p,'w').write(s); print('ok')
