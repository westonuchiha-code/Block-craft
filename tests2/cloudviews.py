# Pictures of clouds: from the ground at midday and at sunset, from a mountain, and flying just above them.
from common import *
from PIL import Image
import io
S='/tmp/claude-0/-home-user-Block-craft/49148b77-0114-5300-b5b9-1304725e4d54/scratchpad/'
with sync_playwright() as p:
    b, page, errors = open_game(p, 1280, 720)
    start_world(page, 12345)
    page.evaluate("()=>{ game.input.update = ()=>{}; game.input.state = game.input.emptyState(); game.settings.renderDistance=12; }")
    shots = []
    def settle():
        for _ in range(90):
            page.wait_for_timeout(1000)
            if page.evaluate("()=>game.world.isAreaLoaded(game.player.x, game.player.z, 5) && game.renderer.isAreaMeshed(Math.floor(game.player.x/16), Math.floor(game.player.z/16), 4) && !game.world.arrived.length"): break
        page.wait_for_timeout(1500)
    def view(js):
        page.evaluate("()=>{ const p=game.player, g=game.world.generator; " + js + " }"); settle(); shots.append(Image.open(io.BytesIO(page.screenshot())))
    view("p.y=g.column(Math.floor(p.x),Math.floor(p.z)).h+2; p.flying=true; p.yaw=0.5; p.pitch=0.35; game.time=0.25;")
    view("p.yaw=-1.4; p.pitch=0.15; game.time=0.49;")
    view("p.x=2587.5; p.z=-256.5; p.y=g.column(2587,-257).h+3; p.flying=true; p.yaw=2.2; p.pitch=0.05; game.time=0.28;")
    view("p.x=0.5; p.z=0.5; p.y=192; p.flying=true; p.yaw=0.8; p.pitch=-0.25; game.time=0.25;")
    W, H = shots[0].size
    sheet = Image.new('RGB', (W * 2, H * 2)); [sheet.paste(im, ((i % 2) * W, (i // 2) * H)) for i, im in enumerate(shots)]
    sheet.save(S + 'clouds.png'); print('errors', errors[:3]); b.close()
