from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context().new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','cs2'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    r=pg.evaluate("""()=>{ const t={}, f={}; for(let x=-200;x<200;x+=3)for(let z=-200;z<200;z+=3){ const c=colInfo(x,z); for(let y=2;y<=c.h;y+=2){ const b=blockAt(x,y,z); const n=NAMES[b]||b; t[n]=(t[n]||0)+1; }
        if(c.steep) for(let y=Math.max(2,c.h-14);y<=c.h;y++){ const b=blockAt(x,y,z); const n=NAMES[b]||b; f[n]=(f[n]||0)+1; } }
      const pct=o=>{ const s=Object.values(o).reduce((a,b)=>a+b,0); return Object.fromEntries(Object.entries(o).sort((a,b)=>b[1]-a[1]).slice(0,10).map(([k,v])=>[k,(100*v/s).toFixed(1)])); };
      return {all:pct(t),cliffFaces:pct(f)}; }""")
    print(r,errs); b.close()
