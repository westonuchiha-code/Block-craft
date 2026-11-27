# The interface on a 4K screen, driven by a (simulated) controller: the title, settings changed with the D-pad, the pause menu.
from common import *
import sys
from PIL import Image
import io
S='/tmp/claude-0/-home-user-Block-craft/49148b77-0114-5300-b5b9-1304725e4d54/scratchpad/'
FAKE_PAD = """(()=>{ window.__pad={ buttons:Array.from({length:17},()=>({pressed:false,value:0})), axes:[0,0,0,0], mapping:'standard', connected:true, id:'test pad' };
  navigator.getGamepads=()=>[window.__pad]; window.press=(i,ms)=>{ __pad.buttons[i].pressed=true; setTimeout(()=>__pad.buttons[i].pressed=false, ms||200); }; })()"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=ARGS)
    ctx = b.new_context(viewport={'width': 1920, 'height': 1080}, device_scale_factor=2)   # a 3840 x 2160 screen
    ctx.add_init_script(FAKE_PAD)
    page = ctx.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)[:300]))
    page.goto(GAME); page.wait_for_timeout(1500)
    shots = [Image.open(io.BytesIO(page.screenshot()))]
    focus = lambda: page.evaluate("()=>document.querySelector('.screen.open .item.focus')?.textContent")
    page.evaluate("()=>press(13)"); page.wait_for_timeout(450)          # D-pad down
    f1 = focus()
    page.evaluate("()=>press(0)"); page.wait_for_timeout(400)           # A: open Settings
    heading = page.evaluate("()=>document.querySelector('.screen.open .heading')?.textContent")
    page.evaluate("()=>press(13)"); page.wait_for_timeout(450)          # down to Resolution
    before = page.evaluate("()=>game.settings.renderScale")
    page.evaluate("()=>press(15)"); page.wait_for_timeout(450)          # right: raise it a step
    after = page.evaluate("()=>game.settings.renderScale")
    page.evaluate("()=>press(14)"); page.wait_for_timeout(450)          # left: back
    shots.append(Image.open(io.BytesIO(page.screenshot())))
    page.evaluate("()=>press(1)"); page.wait_for_timeout(300)           # B: back to the title
    back = page.evaluate("()=>document.querySelector('.screen.open .title')?.textContent")
    font = page.evaluate("()=>getComputedStyle(document.body).fontSize")
    print('focus after down:', f1, '| A opened:', heading, '| resolution', before, '->', after, '| B back to:', back, '| text size', font, 'css px (x2 device pixels)')
    ok = f1 == 'Settings' and heading == 'Settings' and after == before + 0.125 and back == 'BLOCKCRAFT'
    # into a world, then Start pauses
    page.evaluate("()=>game.newWorld(12345)")
    for _ in range(120):
        page.wait_for_timeout(500)
        if page.evaluate("()=>game.state") == 'playing': break
    page.wait_for_timeout(1500)
    page.evaluate("()=>press(9, 2500)"); page.wait_for_timeout(3500)    # Start (held long: frames are slow in this software renderer at 4K)
    paused = page.evaluate("()=>game.state")
    shots.append(Image.open(io.BytesIO(page.screenshot())))
    page.evaluate("()=>press(0, 2500)"); page.wait_for_timeout(3500)    # A on Resume
    resumed = page.evaluate("()=>game.state")
    print('start ->', paused, '| A ->', resumed, '| errors', errors[:3])
    ok = ok and paused == 'paused' and resumed == 'playing' and not errors
    W, H = shots[0].size
    sheet = Image.new('RGB', (W, H * 3)); [sheet.paste(im, (0, i * H)) for i, im in enumerate(shots)]
    sheet.resize((W // 2, H * 3 // 2)).save(S + 'v2_ui4k.png')
    b.close(); print('UI OK' if ok else 'UI FAILED'); sys.exit(0 if ok else 1)
