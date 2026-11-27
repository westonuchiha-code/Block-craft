# Pictures of light: a cave at noon without and with torches, a cave mouth from inside, and torches and glowstone at night.
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
    # a roomy cave: a spot with 4+ blocks of air above solid floor, well under the ground
    cave = page.evaluate("""()=>{ const g=game.world.generator; for(let r=0;r<800;r+=5) for(let a=0;a<28;a++){ const x=Math.round(Math.cos(a/4.4)*r), z=Math.round(Math.sin(a/4.4)*r), h=g.column(x,z).h;
        for(let y=20;y<h-14;y++) if(g.blockAt(x,y-1,z)!==0 && [0,1,2,3].every(k=>g.blockAt(x,y+k,z)===0) && [-3,3].every(d=>g.blockAt(x+d,y,z)===0 || g.blockAt(x,y,z+d)===0)) return [x,y,z]; } return null; }""")
    print('cave', cave)
    page.evaluate(f"()=>{{ const p=game.player; p.x={cave[0]}+0.5; p.y={cave[1]}; p.z={cave[2]}+0.5; p.flying=true; p.yaw=0.4; p.pitch=-0.15; game.time=0.25; }}")
    settle(); shot()
    # torches on the cave floor round the player
    placed = page.evaluate(f"""()=>{{ const w=game.world, n=[]; for(let dx=-12;dx<=12;dx+=4) for(let dz=-12;dz<=12;dz+=4){{
        for(let y={cave[1]}+3;y>{cave[1]}-6;y--) if(w.getBlock({cave[0]}+dx,y,{cave[2]}+dz)===0 && w.isSolid({cave[0]}+dx,y-1,{cave[2]}+dz) && w.getBlock({cave[0]}+dx,y-1,{cave[2]}+dz)!==BLOCK.water){{ w.setBlock({cave[0]}+dx,y,{cave[2]}+dz,BLOCK.torch); n.push([dx,dz]); break; }} }} return n.length; }}""")
    print('torches placed', placed)
    settle(); shot()
    # a cave mouth: from inside a tunnel where the daylight is fading (sky light 5-9 at the eye), looking toward the brighter side
    mouth = page.evaluate("""()=>{ const w=game.world, L=w.lighting, p=game.player, x0=Math.floor(p.x), z0=Math.floor(p.z);
        for(let r=2;r<70;r++) for(let a=0;a<r*4;a++){ const x=x0+Math.round(Math.cos(a/(r*4)*6.283)*r), z=z0+Math.round(Math.sin(a/(r*4)*6.283)*r);
          for(let y=30;y<110;y++){ const s=L.get(x,y,z)>>4, s2=L.get(x,y+1,z)>>4; if(s>=5&&s<=8&&s2>=5&&w.getBlock(x,y,z)===0&&w.getBlock(x,y+1,z)===0&&w.isSolid(x,y-1,z)){
            let best=0,yaw=0; for(let k=0;k<16;k++){ const ang=k/16*6.283, v=L.get(Math.round(x-Math.sin(ang)*3),y+1,Math.round(z-Math.cos(ang)*3))>>4; if(v>best){best=v;yaw=ang;} }
            return [x,y,z,yaw]; } } } return null; }""")
    print('mouth', mouth)
    if mouth:
        page.evaluate(f"()=>{{ const p=game.player; p.x={mouth[0]}+0.5; p.y={mouth[1]}; p.z={mouth[2]}+0.5; p.flying=true; p.yaw={mouth[3]}; p.pitch=0.1; game.time=0.25; }}")
        settle(); shot()
    # night: a ring of torches and a glowstone pillar on the ground at the spawn point
    page.evaluate("""()=>{ const w=game.world, g=w.generator, p=game.player, x0=0, z0=-8;
        for(let a=0;a<8;a++){ const x=x0+Math.round(Math.cos(a/8*6.283)*7), z=z0+Math.round(Math.sin(a/8*6.283)*7), h=g.column(x,z).h; if(w.getBlock(x,h+1,z)===0||w.getBlock(x,h+1,z)===BLOCK.tall_grass) w.setBlock(x,h+1,z,BLOCK.torch); }
        const h=g.column(x0,z0).h; for(let k=1;k<=3;k++) w.setBlock(x0,h+k,z0,BLOCK.glowstone);
        p.x=x0+0.5; p.z=z0+18.5; p.y=Math.max(h, g.column(x0,z0+18).h)+12; p.flying=true; p.yaw=0; p.pitch=-0.55; game.time=0.75; }""")
    settle(); shot()
    W, H = shots[0].size
    sheet = Image.new('RGB', (W * 2, H * 2)); [sheet.paste(im, ((i % 2) * W, (i // 2) * H)) for i, im in enumerate(shots)]
    sheet.save(S + 'light.png'); print('errors', errors[:3]); b.close()
