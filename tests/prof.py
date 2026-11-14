import json,sys,collections
from playwright.sync_api import sync_playwright
f=sys.argv[1] if len(sys.argv)>1 else 'blockcraft_prototype.html'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/'+f); pg.wait_for_timeout(1000)
    pg.fill('#newName','prof'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    pg.evaluate("()=>{ tod=0.2; player.pitch=-0.1; window.__n=0; const of=render; }")
    cdp=ctx.new_cdp_session(pg)
    cdp.send('Profiler.enable'); cdp.send('Profiler.setSamplingInterval',{'interval':200}); cdp.send('Profiler.start')
    # walk and turn
    pg.keyboard.down('w')
    t0=pg.evaluate("performance.now()")
    fr0=pg.evaluate("()=>new Promise(r=>{let n=0;const t=performance.now();function f(){n++; player.yaw+=0.01; if(performance.now()-t<6000) requestAnimationFrame(f); else r(n);} requestAnimationFrame(f);})")
    pg.keyboard.up('w')
    prof=cdp.send('Profiler.stop')['profile']
    print('frames in 6s:',fr0, 'fps', fr0/6.0)
    nodes={n['id']:n for n in prof['nodes']}
    self=collections.Counter()
    dts=prof['timeDeltas']; 
    for s,d in zip(prof['samples'],dts):
        n=nodes[s]; cf=n['callFrame']; self[cf['functionName'] or '(anon)'+str(cf['lineNumber'])]+=d
    tot=sum(self.values())
    for k,v in self.most_common(28): print(f'{v/tot*100:5.1f}%  {k}')
    print(errs)
    b.close()
