from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page()
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','og'); pg.fill('#newSeed','777'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    print(pg.evaluate("""()=>{ paused=true; const why={}; const add=k=>why[k]=(why[k]||0)+1;
      for(let i=0;i<3000;i++){ const x=Math.floor((Math.random()-0.5)*1600), z=Math.floor((Math.random()-0.5)*1600); const ci=colInfo(x,z);
        if(ci.top!==GRASS && ci.top!==SAND){ add('top'+ci.top); continue; } if(ci.h<=SEA+1){ add('low'); continue; }
        const v=villageAt(Math.floor(x/VREG),Math.floor(z/VREG)); if(v && Math.hypot(x-v.cx,z-v.cz)<60){ add('village'); continue; }
        let lo=ci.h, hi=ci.h, bad=null;
        for(const rr of [5,10,15]) for(let k=0;k<8&&!bad;k++){ const sx=x+Math.round(Math.cos(k*0.785)*rr), sz=z+Math.round(Math.sin(k*0.785)*rr), c2=colInfo(sx,sz);
          if(c2.h<=SEA || (c2.top!==GRASS && c2.top!==SAND)){ bad='edge'+rr; break; } lo=Math.min(lo,c2.h); hi=Math.max(hi,c2.h); }
        if(bad){ add(bad); continue; } if(hi-lo>4){ add('slope'); continue; } add('OK(before tree check)'); }
      return why; }"""))
    b.close()
