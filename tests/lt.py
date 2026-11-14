from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m: errs.append('C:'+m.text) if m.type=='error' else None)
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    print(pg.evaluate("""()=>{ const r={};
      const id=STW0+(3*2+1)*2+1; r.win=[NAMES[id], DROP[id], IS_WINDOW[id], SH_TINT[id]]; r.winTile=!!tintWin(3,1)[5][5]!==undefined;
      r.recipes=[RECIPES.filter(x=>/stained (lattice )?window/.test(x.name)).length, RECIPES.filter(x=>/^Dye wool teal/.test(x.name)).length, RECIPES.filter(x=>/Candles/.test(x.name)).length];
      r.candle=[NAMES[CANDLE], IS_EMIT[CANDLE], LIGHT_PASS[CANDLE], DROP[CANDLE]]; r.icons=[id,CANDLE,STW0].every(i=>!!iconCanvas(i));
      return r; }"""))
    # sit / stand
    print(pg.evaluate("""()=>{ health=20; paused=false; const o=testPlan().rooms[6]; const X=o.x0+3, Z=TEST_Z+o.side*(4+6), Y=TEST_FY+1;
      player.x=X+0.5; player.z=Z+3.5; player.y=Y; lastPCX=null; updateChunks(); setB(X,Y,Z,chairId(0,2)); window.C={X,Y,Z}; return getB(X,Y,Z); }"""))
    pg.wait_for_timeout(1500)
    print(pg.evaluate("""()=>{ sitDown(C.X,C.Y,C.Z,2); return [!!sit, player.y.toFixed(2)]; }"""))
    pg.wait_for_timeout(1200)
    print('still sitting after 1s', pg.evaluate("[!!sit, player.y.toFixed(2), player.x.toFixed(2)]"))
    pg.screenshot(path='/tmp/lt1.png',clip={'x':0,'y':60,'width':390,'height':330})
    pg.evaluate("jumpQueued=true"); pg.wait_for_timeout(600)
    print('stood', pg.evaluate("[!!sit, player.y.toFixed(2), collides(player.x,player.y,player.z)]"))
    # candle light: dark enclosed spot? just compare light level next to candle
    print(pg.evaluate("""()=>{ setB(C.X+2,C.Y,C.Z,CANDLE); return 'placed'; }"""))
    # rain watering: tilled soil outdoors in a normal world
    print(errs); b.close()
