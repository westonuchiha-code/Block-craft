from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for lvl in (1,3,5):
        ctx=b.new_context(viewport={'width':1100,'height':560}); pg=ctx.new_page()
        pg.add_init_script("localStorage.setItem('bc_res','%d')"%lvl)
        pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
        pg.fill('#newName','rb'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
        pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } beastSpawnT=1e9; player.pitch=-0.05; }")
        pg.wait_for_timeout(4000)
        r=pg.evaluate("""()=>{ const on=WK.on; WK.on=false; R_Y0=0; R_STEP=1; for(let i=0;i<3;i++) render(); const t0=performance.now(); for(let i=0;i<10;i++) render(); const ms=(performance.now()-t0)/10; WK.on=on; return {RW,RH,pixels:RW*RH, ms_per_frame_one_core:+ms.toFixed(1), cores:navigator.hardwareConcurrency}; }""")
        print(json.dumps(r)); ctx.close()
