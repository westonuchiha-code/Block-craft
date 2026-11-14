from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','y'); pg.fill('#newSeed','3'); pg.click('#newBtn'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    print(pg.evaluate("""()=>{ const out={}; const X=Math.floor(player.x)+40, Y=5, Z=Math.floor(player.z);
      for(const lv of [5,50,100]){ for(const [nm,b,t] of [['stone',STONE,STONE_PICK],['coal',COAL,STONE_PICK],['log',LOG,STONE_AXE]]){
        const sk = t===STONE_AXE?'woodcut':'mining'; skills[sk]=lv; const n0=itemDrops.length; const cnt={};
        for(let i=0;i<200;i++){ setB(X,Y,Z,b); placedDel(X,Y,Z); const k=itemDrops.length; breakNow({x:X,y:Y,z:Z,b},t); for(const d of itemDrops.slice(k)) cnt[NAMES[d.id]]=(cnt[NAMES[d.id]]||0)+1; itemDrops.length=k; }
        for(const k in cnt) cnt[k]=+(cnt[k]/200).toFixed(2); out[nm+'@'+lv]=JSON.stringify(cnt); } }
      return out; }"""))
    print(errs); b.close()
