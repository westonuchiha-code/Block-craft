from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':780})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','rn2'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    # statistics of the dawn roll
    print(pg.evaluate("""()=>{ let n=0, c={0.25:0,0.5:0,1:0}, N=20000; for(let i=0;i<N;i++){ rainOn=false; rainLeftT=0; rainDawn(false); if(rainOn){ n++; c[rainLeftT]++; } } rainOn=false; rainLeftT=0; return [(n/N).toFixed(3), c[0.25]/n, c[0.5]/n, c[1]/n]; }"""))
    print('start', pg.evaluate("[rainOn, rainLeftT]"))
    # run a whole day: force sunrise by setting tod just before wrap, with a forced roll via Math.random stub
    pg.evaluate("Math.random=()=>0.01; tod=0.001; rainPrevTod=0.999")
    pg.wait_for_timeout(1500)
    print('after dawn (forced roll)', pg.evaluate("[rainOn, rainLeftT]"))
    pg.evaluate('tod=0.2; rainPrevTod=0.1'); pg.wait_for_timeout(500)
    print('mid morning', pg.evaluate("[rainOn, rainLeftT.toFixed(3)]"))
    pg.evaluate("tod=0.3; rainPrevTod=0.29"); pg.wait_for_timeout(500)
    pg.evaluate("rainLeftT=0.01; tod=0.40; rainPrevTod=0.35"); pg.wait_for_timeout(500)
    print('ends', pg.evaluate("[rainOn, rainLeftT]"), errs); b.close()
