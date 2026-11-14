p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
rep("""    <button id="skillBtn">CHARACTER</button>
    <button id="mapBtn">MAP</button>
    <button id="charBtn">APPEARANCE</button>
    <button id="resBtn">SHARPNESS</button>
    <button id="mcBtn">MULTI-CORE</button>
    <button id="rainBtn">WEATHER: AUTO</button>
    <button id="wxNowBtn">WEATHER NOW</button>
    <button id="hallBtn" style="display:none">GO TO TEST HALL</button>
    <button id="dbgBtn">DEBUG INFO: OFF</button>
    <button id="resumeBtn">BACK TO GAME</button>""",
"""    <div class="mSec">ADVENTURE</div>
    <div class="mRow"><button id="resumeBtn" class="mMain">BACK TO GAME</button><button id="skillBtn">CHARACTER</button><button id="mapBtn">MAP</button><button id="charBtn">APPEARANCE</button></div>
    <details id="mSettings"><summary class="mSec">SETTINGS</summary>
      <div class="mRow"><button id="resBtn">SHARPNESS</button><button id="mcBtn">MULTI-CORE</button><button id="rainBtn">WEATHER: AUTO</button><button id="dbgBtn">DEBUG INFO: OFF</button></div>
    </details>
    <details id="mDev"><summary class="mSec">BUILDER TOOLS</summary>
      <div class="mRow"><button id="testBtn">TEST ROOM</button><button id="hallBtn" style="display:none">GO TO TEST HALL</button><button id="wxNowBtn">WEATHER NOW</button><button id="importBtn">IMPORT WORLD FILE</button>
      <input type="file" id="importFile" accept=".json,application/json" style="display:none"></div>
    </details>""")
rep("""    <div>
      <input id="newName" placeholder="world name">
      <input id="newSeed" placeholder="seed (optional)">
      <button id="newBtn">NEW WORLD</button>
      <button id="testBtn">TEST ROOM</button>
    </div>
    <div>
      <button id="importBtn">IMPORT WORLD FILE</button>
      <input type="file" id="importFile" accept=".json,application/json" style="display:none">
    </div>""", """    <div class="mSec">WORLDS</div>
    <div class="mRow">
      <input id="newName" placeholder="world name">
      <input id="newSeed" placeholder="seed (optional)">
      <button id="newBtn">NEW WORLD</button>
    </div>""")
rep("  #menuBox h2 { color:#e3cf95;", """  #menuBox .mSec { font-size:11px; letter-spacing:3px; color:#8c7640; margin:12px 0 2px; border-bottom:1px solid #2a2c26; padding-bottom:3px; cursor:default; }
  #menuBox details > summary.mSec { cursor:pointer; list-style:none; } #menuBox details > summary.mSec::before { content:'\\25B8  '; } #menuBox details[open] > summary.mSec::before { content:'\\25BE  '; }
  #menuBox .mRow { display:flex; flex-wrap:wrap; gap:6px; align-items:center; } #menuBox .mRow button { margin:3px 0; }
  #menuBox .mMain { box-shadow:inset 0 0 0 1px #e3cf95 !important; }
  #menuBox h2 { color:#e3cf95;""")
# death screen: where your things are, where you'll wake
rep('<div id="death"><div id="deathBox"><h2>You died</h2><button id="respawnBtn">RESPAWN</button></div></div>',
    '<div id="death"><div id="deathBox"><h2>You died</h2><div id="deathInfo" style="font:12px monospace;color:#d8cfb8;max-width:300px;margin:0 auto 10px;line-height:1.5"></div><button id="respawnBtn">RISE AGAIN</button></div></div>')
rep("function die(){\n  dropSack();\n  dead = true; health = 0;", """function die(){
  const hadThings = Object.keys(inv).some(k=>inv[k]>0) || armor.some(a=>a);
  dropSack();
  dead = true; health = 0;
  { const bedOk = bedSpawn && IS_BED[getB(bedSpawn[0],bedSpawn[1],bedSpawn[2])];
    document.getElementById('deathInfo').innerHTML = (hadThings ? 'Everything you carried lies where you fell, under a beam of light.<br>' : '') + (bedOk ? 'You will wake in your bed.' : 'You have no bed: you will wake in the open.') + (gold ? '<br>Your purse is safe: '+gold+' gold.' : ''); }""")
# bed and sleep messages
rep("  if(Math.sin(tod*Math.PI*2) > -0.05){ sleepMsg('Spawn point set. You can only sleep at night.'); return; }", "  if(Math.sin(tod*Math.PI*2) > -0.05){ sleepMsg('This bed is yours now: you will wake here if you fall. You can only sleep at night.'); return; }")
rep("  if(el){ el.textContent = 'Sleeping...'; el.classList.add('dark'); el.style.opacity = '1'; }\n  clearTimeout(sleepMsg.t);\n  sleepMsg.t = setTimeout(()=>{ tod = 0.02;",
    "  if(el){ el.textContent = 'You sleep...'; el.classList.add('dark'); el.style.opacity = '1'; }\n  clearTimeout(sleepMsg.t);\n  sleepMsg.t = setTimeout(()=>{ advanceHours(((1.02-tod)%1)*24); tod = 0.02;")
rep("if(el){ el.textContent = 'Good morning'; el.style.opacity = '0'; } }, 1300);\n}", "if(el){ el.textContent = 'Dawn breaks'; el.style.opacity = '0'; } }, 1300);\n}")
# the pistol is gone for good: unreachable everywhere, name kept only for old saves
rep("NAMES[PISTOL] = 'flintlock pistol';", "NAMES[PISTOL] = 'old pistol (removed)';")
open(p,'w').write(s); print('ok')
