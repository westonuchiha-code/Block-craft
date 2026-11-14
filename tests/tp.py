from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','tp'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    pg.evaluate("player.pitch=-0.15; CHAR=Object.assign(ccDefault(),{hairStyle:11,hairCol:'#6b4423',top:1,topCol:'#c93d3d',legsCol:'#2f4f9e'}); ")
    clip={'x':0,'y':60,'width':390,'height':330}
    pg.evaluate("camMode=1"); pg.wait_for_timeout(600); pg.screenshot(path='/tmp/tp_back.png',clip=clip)
    pg.evaluate("camMode=2"); pg.wait_for_timeout(600); pg.screenshot(path='/tmp/tp_front.png',clip=clip)
    # walking pose
    pg.evaluate("camMode=1; limbAmp=1; walkPhase=0.9"); pg.wait_for_timeout(100); 
    pg.evaluate("swingT=0.5")
    pg.wait_for_timeout(30); pg.screenshot(path='/tmp/tp_walk.png',clip=clip)
    print(pg.evaluate("[camMode, performance.now()]"), errs)
    t=pg.evaluate("""()=>{ const t0=performance.now(); let n=0; return new Promise(r=>{ function f(){ n++; if(performance.now()-t0>2000) r(n/2); else requestAnimationFrame(f);} f(); }); }""")
    print('fps in 3rd person (headless)',t)
    pg.evaluate("camMode=0"); pg.wait_for_timeout(300)
    t=pg.evaluate("""()=>{ const t0=performance.now(); let n=0; return new Promise(r=>{ function f(){ n++; if(performance.now()-t0>2000) r(n/2); else requestAnimationFrame(f);} f(); }); }""")
    print('fps in 1st person',t)
    b.close()
