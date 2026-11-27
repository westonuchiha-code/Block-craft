# Pictures of the new biomes: a desert with mesas, the border between two biomes, and inside a cave (lit by flying in at noon).
from common import *
from PIL import Image
import io
S='/tmp/claude-0/-home-user-Block-craft/49148b77-0114-5300-b5b9-1304725e4d54/scratchpad/'
with sync_playwright() as p:
    b, page, errors = open_game(p, 1280, 720)
    start_world(page, 12345)
    page.evaluate("()=>{ game.input.update = ()=>{}; game.input.state = game.input.emptyState(); game.settings.renderDistance=14; }")
    shots = []
    def go(js, label):
        where = page.evaluate(js)
        print(label, where)
        for _ in range(90):
            page.wait_for_timeout(1000)
            if page.evaluate("()=>game.world.isAreaLoaded(game.player.x, game.player.z, 6) && game.renderer.isAreaMeshed(Math.floor(game.player.x/16), Math.floor(game.player.z/16), 5)"): break
        page.wait_for_timeout(1500)
        shots.append(Image.open(io.BytesIO(page.screenshot())))
    # a mesa: desert ground with mesa columns nearby
    go("""()=>{ const g=game.world.generator, p=game.player; for(let r=200;r<6000;r+=150) for(let a=0;a<40;a++){ const x=Math.round(Math.cos(a/6.4)*r), z=Math.round(Math.sin(a/6.4)*r), c=g.column(x,z);
        if(c.biome===4 && !c.mesa && c.h>57){ let m=0; for(let dx=-60;dx<=60;dx+=10) for(let dz=-60;dz<=60;dz+=10) if(g.column(x+dx,z+dz).mesa) m++; if(m>25){ p.x=x+0.5; p.z=z+0.5; p.y=c.h+14; p.flying=true; p.yaw=0.6; p.pitch=-0.25; game.time=0.3; return [x,z,m]; } } } return null; }""", 'desert')
    page.evaluate("()=>{ game.player.yaw += 2.4; }"); page.wait_for_timeout(2500); shots.append(Image.open(io.BytesIO(page.screenshot())))
    # a border: two different biomes either side, seen from above
    go("""()=>{ const g=game.world.generator, p=game.player; for(let r=300;r<6000;r+=150) for(let a=0;a<40;a++){ const x=Math.round(Math.cos(a/6.4)*r), z=Math.round(Math.sin(a/6.4)*r), info=g.regionInfo(x,z);
        if(info.blend>0.4 && g.column(x,z).h>58 && info.biome!==4 && info.other!==4){ p.x=x+0.5; p.z=z+60.5; p.y=g.column(x,z).h+45; p.flying=true; p.yaw=0; p.pitch=-0.45; game.time=0.3; return [x,z,info.biome,info.other]; } } return null; }""", 'border')
    # a cave: the nearest tall cave air under the spawn area
    go("""()=>{ const g=game.world.generator, p=game.player; for(let r=0;r<600;r+=6) for(let a=0;a<24;a++){ const x=Math.round(Math.cos(a/3.8)*r), z=Math.round(Math.sin(a/3.8)*r), h=g.column(x,z).h;
        for(let y=20;y<h-8;y++) if(g.blockAt(x,y,z)===0 && g.blockAt(x,y+1,z)===0 && g.blockAt(x,y+2,z)===0 && g.blockAt(x,y-1,z)!==0){ p.x=x+0.5; p.y=y; p.z=z+0.5; p.flying=true; p.pitch=-0.1; game.time=0.3; window.__glow=[x,y+2,z]; return [x,y,z]; } } return null; }""", 'cave')
    W, H = shots[0].size
    sheet = Image.new('RGB', (W * 2, H * 2)); [sheet.paste(im, ((i % 2) * W, (i // 2) * H)) for i, im in enumerate(shots)]
    sheet.save(S + 'v2_biomes.png'); print('errors', errors[:3]); b.close()
