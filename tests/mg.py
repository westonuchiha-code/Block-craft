from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','mg'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='blackmage'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={}; beastSpawnT=1e9;
      out.recipe=(()=>{ const m=matchGrid([CANDLE,BOOKSHELF,CANDLE,STONE_BRICK,STONE_BRICK,STONE_BRICK,0,0,0],3); return m?NAMES[(m.out||m)[0]]:null; })();
      out.mp=[mp, mpMax()];
      // make spells at a spellmaker
      inv[EMBER]=5; inv[CANDLE]=3; inv[CHITIN]=2; gold=500;
      openSpellmaker(); smFx='fire'; smPow=1; smMake(); smFx='heal'; smPow=0; smMake(); smFx='ward'; smPow=0; smMake(); out.screenOpen=document.getElementById('smMenu').classList.contains('show');
      out.book=book.map(bookName); out.goldLeft=gold; out.ember=inv[EMBER];
      closeSpellmaker();
      // the black mage's potions: drink one, F uses the potion first; use up, then the book
      spell=null; spellCharges=0; bookSel=0; mp=mpMax();
      const m=newBeast('bear',Math.floor(player.x)+4,Math.floor(player.y),Math.floor(player.z)); m.hp=1e4; m.iframe=0; mobs.push(m);
      let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; const v=camVectors().f; if(v[0]>bd){bd=v[0];ba=a;} } player.yaw=ba; player.pitch=0;
      const mp0=mp, hp0=m.hp; castCool=0; castSpell(); await sleep(1200); out.fire=[mp0-mp, Math.round(hp0-m.hp)];
      bookSel=1; health=6; castCool=0; castSpell(); out.heal=health;
      bookSel=2; castCool=0; castSpell(); out.ward=[wardPts, armorPoints()]; health=20; hurt(10); out.hit10=health;
      mp=1; castCool=0; bookSel=0; castSpell(); out.noMp=document.getElementById('skillToast').textContent;
      const t0=mp; await sleep(4000); out.regen=mp-t0;
      return out; }""")
    print(json.dumps(r))
    pg.evaluate("()=>{ openSpellmaker(); smFx='bolt'; smPow=2; renderSpellmaker(); }"); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/mg_sm.png')
    pg.evaluate("()=>{ closeSpellmaker(); openSheet('magic'); }"); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/mg_sheet.png')
    print(errs[:3]); b.close()
