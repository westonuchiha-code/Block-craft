# Pictures of mountain country: the highest highland ground near spawn and an ordinary mountain, seen from a distance, from the ground and from above,
# to check that slopes are walkable and nothing floats. Pass "old" to save under a different name.
import sys
from common import *
from PIL import Image
import io
S='/tmp/claude-0/-home-user-Block-craft/49148b77-0114-5300-b5b9-1304725e4d54/scratchpad/'
NAME = sys.argv[1] if len(sys.argv) > 1 else 'mountains'
with sync_playwright() as p:
    b, page, errors = open_game(p, 1280, 720)
    start_world(page, 12345)
    page.evaluate("()=>{ game.input.update = ()=>{}; game.input.state = game.input.emptyState(); game.settings.renderDistance=16; }")
    peak = page.evaluate("""()=>{ const g=game.world.generator; let best=null; for(let r=200;r<5000;r+=100) for(let a=0;a<48;a++){ const x=Math.round(Math.cos(a/7.6)*r), z=Math.round(Math.sin(a/7.6)*r), c=g.column(x,z);
        if(c.biome===2 && (!best || c.h>best[2])) best=[x,z,c.h]; } return best; }""")
    typical = page.evaluate("""()=>{ const g=game.world.generator; for(let r=300;r<5000;r+=100) for(let a=0;a<48;a++){ const x=Math.round(Math.cos(a/7.6)*r), z=Math.round(Math.sin(a/7.6)*r), c=g.column(x,z);
        if(c.biome===2 && c.h>=98 && c.h<=112) return [x,z,c.h]; } return null; }""")
    print('highest highland', peak, 'typical mountain', typical)
    shots = []
    def view(dx, dz, up, yaw, pitch, at=None):
        at = at or peak
        page.evaluate(f"""()=>{{ const p=game.player, g=game.world.generator, x={at[0]}+{dx}, z={at[1]}+{dz};
            p.x=x+0.5; p.z=z+0.5; p.y=Math.max(g.column(x,z).h+2, 60)+{up}; p.flying=true; p.yaw={yaw}; p.pitch={pitch}; game.time=0.3; }}""")
        for _ in range(120):
            page.wait_for_timeout(1000)
            if page.evaluate("()=>game.world.isAreaLoaded(game.player.x, game.player.z, 7) && game.renderer.isAreaMeshed(Math.floor(game.player.x/16), Math.floor(game.player.z/16), 6)"): break
        page.wait_for_timeout(1500)
        shots.append(Image.open(io.BytesIO(page.screenshot())))
    # yaw 0 looks toward -z (north)
    view(0, 110, 0, 0, 0.05)                    # the highest ground, from the ground
    view(0, 140, 70, 0, -0.35)                  # the highest ground, from above
    view(0, 100, 0, 0, 0.05, typical)           # an ordinary mountain, from the ground
    view(0, 130, 60, 0, -0.35, typical)         # an ordinary mountain, from above
    W, H = shots[0].size
    sheet = Image.new('RGB', (W * 2, H * 2)); [sheet.paste(im, ((i % 2) * W, (i // 2) * H)) for i, im in enumerate(shots)]
    sheet.save(S + NAME + '.png'); print('errors', errors[:3]); b.close()
