# Light: a sealed stone room high in the sky, built across a chunk border.
#   dark inside; a torch lights it, fading one level per block; breaking the torch makes it dark again;
#   a hole in the roof lets daylight fall in; closing it shuts the daylight out again.
# After every step, and over a natural area round the spawn, every block's light is checked against its neighbours
# (the rules in light.js must hold everywhere: a block's light is what its brightest neighbour gives it, or its own glow).
from common import *
import sys

CHECK = """(box)=>{ const w=game.world, L=w.lighting, {LIGHT_OF, LIGHT_PASS}=LIGHT_TABLES; const bad=[];
  const [x0,y0,z0,x1,y1,z1]=box;
  for(let x=x0;x<=x1;x++) for(let z=z0;z<=z1;z++) for(let y=y0;y<=y1;y++){
    const id=w.getBlock(x,y,z), b=L.get(x,y,z);
    for(const ch of [0,1]){
      const have = ch ? b&15 : b>>4;
      let want = ch ? LIGHT_OF[id] : 0;
      if(LIGHT_PASS[id]){
        for(const [dx,dy,dz,down] of [[1,0,0],[-1,0,0],[0,1,0,1],[0,-1,0],[0,0,1],[0,0,-1]]){
          const nb=L.get(x+dx,y+dy,z+dz), n = ch ? nb&15 : nb>>4;
          const give = (!ch && down && n===15 && LIGHT_PASS[id]===2) ? 15 : n-1;
          if(give>want) want=give;
        }
      }
      if(have!==want && bad.length<5) bad.push([x,y,z,ch?'block':'sky',have,want,id]);
    }
  }
  return bad; }"""

with sync_playwright() as p:
    b, page, errors = open_game(p, 960, 540)
    start_world(page, 12345)
    page.evaluate("()=>{ game.input.update = ()=>{}; game.input.state = game.input.emptyState(); }")
    ok = True
    def check(label, box):
        global ok
        bad = page.evaluate(CHECK, box)
        print(label, 'rule broken at' if bad else 'light consistent', bad if bad else '')
        if bad: ok = False

    # the room: inside 12 x 4 x 6, its middle on a chunk border
    base = page.evaluate("""()=>{ const p=game.player, cx=Math.floor(p.x/16)*16; return [cx-6, 200, Math.floor(p.z)-3]; }""")
    x0, y0, z0 = base
    page.evaluate(f"""()=>{{ const w=game.world, S=BLOCK.stone;
      for(let x={x0}-1;x<={x0}+12;x++) for(let y={y0}-1;y<={y0}+4;y++) for(let z={z0}-1;z<={z0}+6;z++){{
        const wall = x<{x0}||x>{x0}+11||y<{y0}||y>{y0}+3||z<{z0}||z>{z0}+5; w.setBlock(x,y,z, wall?S:BLOCK.air); }} }}""")
    box = [x0 - 2, y0 - 2, z0 - 2, x0 + 13, y0 + 5, z0 + 7]
    L = lambda x, y, z: page.evaluate(f"()=>{{ const b=game.world.lighting.get({x},{y},{z}); return [b>>4, b&15]; }}")
    r = {}
    r['sealed'] = L(x0 + 5, y0 + 1, z0 + 2)
    check('sealed', box)
    page.evaluate(f"()=>game.world.setBlock({x0}+2,{y0},{z0}+2,BLOCK.torch)")
    r['torch'] = [L(x0 + 2, y0, z0 + 2), L(x0 + 5, y0, z0 + 2), L(x0 + 11, y0, z0 + 2)]   # at it, 3 away, 9 away (across the border)
    check('torch', box)
    page.evaluate(f"()=>game.world.setBlock({x0}+2,{y0},{z0}+2,BLOCK.air)")
    r['torch gone'] = L(x0 + 5, y0, z0 + 2)
    check('torch gone', box)
    page.evaluate(f"()=>game.world.setBlock({x0}+8,{y0}+4,{z0}+2,BLOCK.air)")
    r['hole'] = [L(x0 + 8, y0, z0 + 2), L(x0 + 9, y0, z0 + 2), L(x0 + 11, y0, z0 + 5)]
    check('hole', box)
    page.evaluate(f"()=>game.world.setBlock({x0}+8,{y0}+4,{z0}+2,BLOCK.stone)")
    r['hole shut'] = L(x0 + 8, y0, z0 + 2)
    check('hole shut', box)
    # the natural ground round the spawn point, from bedrock up (caves, trees, water)
    sx, sz = page.evaluate("()=>[Math.floor(game.player.x), Math.floor(game.player.z)]")
    check('ground round spawn', [sx - 20, 1, sz - 20, sx + 20, 130, sz + 20])
    # how long lighting a chunk takes
    r['ms per chunk'] = page.evaluate("""()=>{ const w=game.world, c=[...w.chunks.values()][5]; const copy=new c.constructor(c.cx,c.cz,c.sections);
      const t0=performance.now(); for(let i=0;i<5;i++){ copy.light=null; w.lighting.quiet=copy; w.lighting.lightChunk(copy); } w.chunks.set(c.cx+','+c.cz, c); return +((performance.now()-t0)/5).toFixed(1); }""")
    print(r)
    want = (r['sealed'] == [0, 0] and r['torch'][0] == [0, 14] and r['torch'][1] == [0, 11] and r['torch'][2] == [0, 5]
            and r['torch gone'] == [0, 0] and r['hole'][0] == [15, 0] and r['hole'][1] == [14, 0] and r['hole'][2][0] == 9
            and r['hole shut'] == [0, 0])
    print('errors', errors[:3])
    print('LIGHT OK' if ok and want and not errors else 'LIGHT FAIL')
    b.close()
    sys.exit(0 if ok and want and not errors else 1)
