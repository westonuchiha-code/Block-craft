# Water and night from a lake shore: go to the nearest lake, let the land there load, look across it at midday, dusk and night.
from common import *
from PIL import Image
import io
S='/tmp/claude-0/-home-user-Block-craft/49148b77-0114-5300-b5b9-1304725e4d54/scratchpad/'
with sync_playwright() as p:
    b, page, errors = open_game(p, 1280, 720)
    start_world(page, 12345)
    page.evaluate("()=>{ game.input.update = ()=>{}; game.input.state = game.input.emptyState(); }")
    print(page.evaluate("""()=>{ const g=game.world.generator, p=game.player;
      for(let r=8;r<300;r+=3) for(let a=0;a<48;a++){ const x=Math.round(p.x+Math.cos(a/7.64)*r), z=Math.round(p.z+Math.sin(a/7.64)*r);
        let n=0; for(let dx=-4;dx<=4;dx+=2) for(let dz=-4;dz<=4;dz+=2) if(g.column(x+dx,z+dz).h<53) n++;
        if(n>=24){ const sx=x-10, sz=z; p.x=sx+0.5; p.z=sz+0.5; p.y=Math.max(g.column(sx,sz).h+3, 60); p.flying=true; p.yaw=-Math.PI/2; p.pitch=-0.3; game.time=0.27; return [x,z,r]; } } return null; }"""))
    for _ in range(60):
        page.wait_for_timeout(1000)
        if page.evaluate("()=>game.renderer.isAreaMeshed(Math.floor(game.player.x/16), Math.floor(game.player.z/16), 2)"): break
    shots = []
    for t in [0.27, 0.49, 0.62]:
        page.evaluate(f"()=>{{ game.time={t}; }}"); page.wait_for_timeout(1500)
        shots.append(Image.open(io.BytesIO(page.screenshot())))
    page.evaluate("()=>game.pause()"); page.wait_for_timeout(1000); shots.append(Image.open(io.BytesIO(page.screenshot())))
    W, H = shots[0].size
    sheet = Image.new('RGB', (W * 2, H * 2)); [sheet.paste(im, ((i % 2) * W, (i // 2) * H)) for i, im in enumerate(shots)]
    sheet.save(S + 'v2_water.png'); print('errors', errors[:3]); b.close()
