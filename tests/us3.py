from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','u3'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    info=pg.evaluate("""()=>{ mobs.length=0; trySpawnOgre=function(){}; paused=false; update=function(){};
      const out=[]; for(let gx=-3;gx<=3;gx++) for(let gz=-3;gz<=3;gz++){ const I=underIsland(gx,gz); if(I) out.push(I); }
      out.sort((a,b)=>a.ix*a.ix+(a.iz-UNDER_Z)**2-b.ix*b.ix-(b.iz-UNDER_Z)**2); window.IS=out; return [out.length, out[0]]; }""")
    print(info)
    I=info[1]
    pg.evaluate("""()=>{ const I=IS[0]; player.x=I.ix+0.5; player.z=I.iz+0.5-6; player.y=I.y+1.01; lastPCX=null; updateChunks(); }""")
    pg.wait_for_timeout(2500)
    print(pg.evaluate("""()=>{ const I=IS[0]; let chests=0, shelves=0, lamps=0, ember=0, dw=0;
      for(let a=-12;a<=12;a++) for(let c=-12;c<=12;c++) for(let y=I.y-14;y<=I.y+8;y++){ const b=getB(I.ix+a,y,I.iz+c); if(b===CHEST)chests++; if(b===BOOKSHELF)shelves++; if(b===LAMP)lamps++; if(b===EMBER)ember++; if(b===DARKWOOD)dw++; }
      return {chests,shelves,lamps,ember,dw,top:getB(I.ix,I.y,I.iz)===DARKWOOD,ramp:I.ramp,rlen:I.rlen}; }"""))
    for i,yaw in enumerate([3.14,1.6,4.7]):
        pg.evaluate("y=>{ player.yaw=y; player.pitch=0.0; }",yaw); pg.wait_for_timeout(1200); pg.screenshot(path='/tmp/u3_%d.png'%i,clip={'x':0,'y':60,'width':390,'height':330})
    # chest loot + inside a house
    print(pg.evaluate("""()=>{ const I=IS[0]; for(let a=-12;a<=12;a++) for(let c=-12;c<=12;c++){ if(getB(I.ix+a,I.y+1,I.iz+c)===CHEST){ const it=chestItems(I.ix+a,I.y+1,I.iz+c); return [a,c,JSON.stringify(it)]; } } return null; }"""))
    # pipes + ember anywhere nearby
    print(pg.evaluate("""()=>{ let n=0,e=0; const X=Math.floor(player.x), Z=Math.floor(player.z); for(let a=-60;a<=60;a++) for(let c=-60;c<=60;c++) for(let y=3;y<110;y++){ const b=getB(X+a,y,Z+c); if(b===EMBER) e++; } return {ember:e}; }"""))
    print(pg.evaluate("[WK.on, WK.err||null]"), errs); b.close()
