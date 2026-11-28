# Pictures of liquids: a lake at midday from the shore, the surface from under the water, and a lava pool in a cave.
from common import *
from PIL import Image
import io
S='/tmp/claude-0/-home-user-Block-craft/49148b77-0114-5300-b5b9-1304725e4d54/scratchpad/'
with sync_playwright() as p:
    b, page, errors = open_game(p, 1280, 720)
    start_world(page, 12345)
    page.evaluate("()=>{ game.input.update = ()=>{}; game.input.state = game.input.emptyState(); game.settings.renderDistance=10; }")
    shots = []
    def settle():
        for _ in range(90):
            page.wait_for_timeout(1000)
            if page.evaluate("()=>game.world.isAreaLoaded(game.player.x, game.player.z, 4) && game.renderer.isAreaMeshed(Math.floor(game.player.x/16), Math.floor(game.player.z/16), 3) && !game.world.arrived.length"): break
        page.wait_for_timeout(1500)
    def shot(): shots.append(Image.open(io.BytesIO(page.screenshot())))
    lake = page.evaluate("""()=>{ const g=game.world.generator, p=game.player;
      for(let r=8;r<300;r+=3) for(let a=0;a<48;a++){ const x=Math.round(p.x+Math.cos(a/7.64)*r), z=Math.round(p.z+Math.sin(a/7.64)*r);
        let n=0; for(let dx=-4;dx<=4;dx+=2) for(let dz=-4;dz<=4;dz+=2) if(g.column(x+dx,z+dz).h<52) n++; if(n>=25) return [x,z]; } return null; }""")
    print('lake', lake)
    page.evaluate(f"()=>{{ const p=game.player; p.x={lake[0]}-9.5; p.z={lake[1]}+0.5; p.y=60; p.flying=true; p.yaw=-1.3; p.pitch=-0.35; game.time=0.25; }}")
    settle(); shot()
    page.evaluate(f"()=>{{ const p=game.player; p.x={lake[0]}+0.5; p.z={lake[1]}+0.5; p.y=52.5; p.flying=true; p.yaw=0.3; p.pitch=0.7; game.time=0.25; }}")
    settle(); shot()
    lava = page.evaluate("""()=>{ const w=game.world, g=w.generator; for(let r=0;r<500;r+=4) for(let a=0;a<32;a++){ const x=Math.round(Math.cos(a/5)*r), z=Math.round(Math.sin(a/5)*r);
        for(let y=3;y<9;y++) if(g.blockAt(x,y,z)===BLOCK.lava && g.blockAt(x,y+1,z)===0 && g.blockAt(x,y+2,z)===0 && g.blockAt(x,y+3,z)===0) return [x,y,z]; } return null; }""")
    print('lava', lava)
    if lava:
        page.evaluate(f"()=>{{ const p=game.player; p.x={lava[0]}+0.5; p.z={lava[2]}+0.5; p.y={lava[1]}+2; p.flying=true; p.yaw=0.8; p.pitch=-0.6; game.time=0.25; }}")
        settle(); shot()
    page.evaluate(f"()=>{{ const p=game.player; p.x={lake[0]}-9.5; p.z={lake[1]}+0.5; p.y=58; p.flying=true; p.yaw=-1.3; p.pitch=-0.15; game.time=0.48; }}")
    settle(); shot()
    W, H = shots[0].size
    sheet = Image.new('RGB', (W * 2, H * 2)); [sheet.paste(im, ((i % 2) * W, (i // 2) * H)) for i, im in enumerate(shots)]
    sheet.save(S + 'liquids.png'); print('errors', errors[:3]); b.close()
