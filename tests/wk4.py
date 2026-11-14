from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for lvl in [1,5]:
      for mode in ['workers','single']:
        ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.add_init_script("try{localStorage.setItem('bc_res','%d')}catch(e){}"%lvl)
        pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2500)
        if mode=='single': pg.evaluate("wkFail()")
        pg.fill('#newName','wk'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
        pg.evaluate("()=>{ window.__c=0; const o=renderOverlay; renderOverlay=function(){ __c++; o(); }; window.__u=0; const u=update; update=function(){ __u++; u(); }; }")
        pg.keyboard.down('w'); pg.wait_for_timeout(8000); pg.keyboard.up('w')
        print(lvl, mode, pg.evaluate("({res:RW+'x'+RH, shown:__c/8, updates:__u/8, on:WK.on, err:WK.err||null})"), errs)
        ctx.close()
    b.close()
