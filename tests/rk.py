from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':780}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','rk'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    r=pg.evaluate("""()=>{ const out={}; for(const [n,id] of [['and',ANDESITE],['gra',GRANITE],['dio',DIORITE],['tuf',TUFF],['mos',MOSSROCK]]){ out[n]=[NAMES[id],DROP[id]||id,HARD[id],KIND[id],REQ_TIER[id],typeof texColor==='function']; }
      out.recipes=RECIPES.filter(r=>/from (andesite|granite|diorite|tuff)/.test(r.name)).length; out.tex=[TILES.andesite.length,TILES.mossrock[0].length];
      // icons render?
      let ic=null; try{ ic=blockIcon(ANDESITE)?1:0 }catch(e){ ic='err '+e.message } out.icon=ic; return out; }""")
    print(r,errs); b.close()
