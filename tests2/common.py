# Shared helpers for the rebuild's browser tests: open the built game in headless Chrome with a software GPU,
# start a world with a fixed seed, and wait until the player is standing in it.
from playwright.sync_api import sync_playwright
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = 'file://' + os.path.join(ROOT, 'game', 'blockcraft.html')
ARGS = ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']

def open_game(p, width=1280, height=720, settings=None):
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=ARGS)
    page = b.new_page(viewport={'width': width, 'height': height})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)[:400]))
    page.on('console', lambda m: errors.append('console: ' + m.text[:300]) if m.type == 'error' else None)
    if settings:
        page.goto(GAME); page.evaluate("(s)=>localStorage.setItem('blockcraft.settings', JSON.stringify(s))", settings)
    page.goto(GAME)
    page.wait_for_timeout(800)
    return b, page, errors

def start_world(page, seed=12345, timeout_s=90):
    page.evaluate(f"()=>game.newWorld({seed})")
    for _ in range(timeout_s * 2):
        page.wait_for_timeout(500)
        if page.evaluate("()=>game.state") == 'playing':
            return True
    return False
