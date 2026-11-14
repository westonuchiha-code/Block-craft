from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','rt'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    r=pg.evaluate("""async ()=>{
      const out={};
      // --- night: surface rats appear; crop beside a rat gets eaten
      tod=0.75; mobs.length=0; ratSpawnT=0;
      for(let i=0;i<6;i++){ ratSpawnT=0; updateMobs(); }
      out.nightRats=mobs.filter(m=>m.kind==='rat').length;
      out.surface=mobs.filter(m=>m.kind==='rat').filter(m=>m.y>=ratTop(Math.floor(m.x),Math.floor(m.z))-1).length;
      // plant crop next to a rat and let it nibble
      const m=mobs.find(m=>m.kind==='rat'); const cx=Math.floor(m.x)+1, cz=Math.floor(m.z), cy=Math.round(m.y);
      setB(cx,cy-1,cz,TILLED_WET); setB(cx,cy,cz,CROPDEFS[1].base+3); m.tgt=null; m.forageT=0;
      for(let i=0;i<400;i++){ ratNight=true; updateMobs(); }
      out.cropLeft=getB(cx,cy,cz)===CROPDEFS[1].base+3;
      // far crop untouched
      const fx=cx+12; setB(fx,cy-1,cz,TILLED_WET); setB(fx,cy,cz,CROPDEFS[1].base+3);
      const keep=getB(fx,cy,cz);
      // --- catnip boost
      mobs.length=0; catnipHere=false; scanCatnip(); out.catnipBefore=catnipHere;
      const px=Math.floor(player.x), pz=Math.floor(player.z), py=ratTop(px+2,pz);
      setB(px+2,py-1,pz,TILLED_WET); setB(px+2,py,pz,CATNIP_B0); scanCatnip(); out.catnipAfter=catnipHere; out.spots=catnipSpots.length;
      return out;}""")
    print(r, errs); b.close()
