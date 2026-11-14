from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':360,'height':225}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.add_init_script("localStorage.setItem('bc_gpu','1')")
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','cl'); pg.fill('#newSeed','12345'); pg.click('#newBtn', no_wait_after=True); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    pg.wait_for_timeout(4000)
    st=lambda: pg.evaluate("()=>({gpu:GPU.on, ok:GPU.ok, frames:GPU.frames, workers:WK.on, label:document.getElementById('gpuBtn').textContent})")
    print('start', st())
    pg.evaluate("()=>{ window.__lc = GPU.gl.getExtension('WEBGL_lose_context'); __lc.loseContext(); }"); pg.wait_for_timeout(3000)
    print('lost', st())
    pg.evaluate("()=>{ __lc.restoreContext(); }"); pg.wait_for_timeout(6000)
    print('restored', st())
    print(errs)
