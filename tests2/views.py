# Pictures of the new renderer from one spot: four directions at midday, then dusk and night, looking down at water,
# and from inside a cave. Full frames, for checking by eye.
from common import *
import sys
from PIL import Image
import io
S='/tmp/claude-0/-home-user-Block-craft/49148b77-0114-5300-b5b9-1304725e4d54/scratchpad/'
with sync_playwright() as p:
    b, page, errors = open_game(p, 1280, 720)
    start_world(page, 12345)
    page.wait_for_timeout(3000)
    page.evaluate("()=>{ game.input.update = ()=>{}; game.input.state = game.input.emptyState(); }")   # hold still: no input
    shots = []
    def shot(js, wait=2500):
        page.evaluate(js); page.wait_for_timeout(wait)
        shots.append(Image.open(io.BytesIO(page.screenshot())))
    for yaw in [0, 1.57, 3.14, 4.71]:
        shot(f"()=>{{ game.time=0.27; game.player.yaw={yaw}; game.player.pitch=-0.05; }}")
    shot("()=>{ game.time=0.48; game.player.yaw=1.57; }")
    shot("()=>{ game.time=0.62; game.player.yaw=1.57; }")
    # water: find the nearest lake and look at it from its shore
    print(page.evaluate("""()=>{ const g=game.world.generator, p=game.player; for(let r=4;r<120;r+=2) for(let a=0;a<32;a++){ const x=Math.round(p.x+Math.cos(a/5.1)*r), z=Math.round(p.z+Math.sin(a/5.1)*r);
        if(g.column(x,z).h < 54){ p.x=x+0.5-Math.cos(a/5.1)*8; p.z=z+0.5-Math.sin(a/5.1)*8; p.y=Math.max(g.column(Math.floor(p.x),Math.floor(p.z)).h+1, 57); p.flying=true; p.yaw=Math.atan2(-(x-p.x), -(z-p.z)); p.pitch=-0.35; game.time=0.3; return [x,z]; } } return null; }"""))
    shot("()=>{}", 6000)
    # a cave: dig the player into the rock under them
    shot("""()=>{ const p=game.player, x=Math.floor(p.x), z=Math.floor(p.z); for(let y=40;y<=44;y++) for(let dx=-3;dx<=3;dx++) for(let dz=-3;dz<=3;dz++) game.world.setBlock(x+dx,y,z+dz,0);
        game.world.setBlock(x+2,41,z-2, game.world.generator && 0 || 34); p.y=40; p.flying=true; p.pitch=0; game.time=0.3; }""", 4000)
    W, H = shots[0].size
    sheet = Image.new('RGB', (W * 2, H * 4))
    for i, im in enumerate(shots): sheet.paste(im, ((i % 2) * W, (i // 2) * H))
    sheet.save(S + 'v2_views.png')
    print('errors', errors[:4]); b.close()
