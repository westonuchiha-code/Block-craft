from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for f in ['before_perf.html','blockcraft_prototype.html']:
        ctx=b.new_context(viewport={'width':390,'height':780}); pg=ctx.new_page()
        pg.goto('file:///home/claude/'+f); pg.wait_for_timeout(1000)
        pg.fill('#newName','h'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
        pg.evaluate("()=>{ window.__u=[]; const of=update; update=function(){ const t=performance.now(); of(); __u.push(performance.now()-t); }; window.__f=[]; let l=performance.now(); (function g(){ const n=performance.now(); __f.push(n-l); l=n; requestAnimationFrame(g); })(); toggleRun&&toggleRun(); }")
        pg.keyboard.down('w'); pg.wait_for_timeout(10000); pg.keyboard.up('w')
        print(f, pg.evaluate("()=>{ const a=__u.slice().sort((x,y)=>x-y), g=__f.slice(5).sort((x,y)=>x-y); return {frames:a.length, updMax:a[a.length-1].toFixed(1), upd99:a[Math.floor(a.length*0.99)].toFixed(1), frameMed:g[g.length>>1].toFixed(1), frame99:g[Math.floor(g.length*0.99)].toFixed(1), frameMax:g[g.length-1].toFixed(1)}; }"))
        ctx.close()
    b.close()
