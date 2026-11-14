from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','vil'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    print(pg.evaluate("""()=>{ const o={site:0,plan:0,n:0, why:{}}; 
      for(let i=0;i<400;i++){ const cx=Math.floor((Math.random()-0.5)*3000), cz=Math.floor((Math.random()-0.5)*3000); o.n++;
        let lo=999,hi=-999,bad=null;
        for(const r of [0,9,18,27]) for(let a=0;a<8;a++){ const ci=colInfo(Math.round(cx+Math.cos(a*0.785)*r), Math.round(cz+Math.sin(a*0.785)*r));
          if(ci.top!==GRASS) bad=bad||('top'+ci.top); else if(ci.h<=SEA+1) bad=bad||'low'; else if(ci.open) bad=bad||'open'; lo=Math.min(lo,ci.h); hi=Math.max(hi,ci.h); if(r===0) break; }
        if(!bad && hi-lo>7) bad='spread';
        o.why[bad||'ok']=(o.why[bad||'ok']||0)+1;
        if(villageSiteOk(cx,cz)){ o.site++; const v=planVillage(cx,cz,vRng(i)); if(v){ o.plan++; o.h=(o.h||0)+v.houses.length; } }
      } return o; }"""), errs)
    b.close()
