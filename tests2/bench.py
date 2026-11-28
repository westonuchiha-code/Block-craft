# Performance benchmark: the same seed, places and settings each time, so builds can be compared.
#   python3 bench.py [path/to/blockcraft.html] [label]
# Measures: time to load a world; frame time looking across a lake, up at the sky, and from under water (clouds on and off where
# the build has them); triangles and draw calls; time to mesh a section; time to light a chunk; JavaScript memory.
# In the test browser the GPU is emulated on the CPU, so frame times are far slower than a real graphics card: compare builds
# with each other, not with a real PC.
import sys, time, json, statistics
from common import *

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'game', 'blockcraft.html')
label = sys.argv[2] if len(sys.argv) > 2 else 'current'

FRAMES = """(n)=>new Promise(done=>{ const t=[]; const f=now=>{ t.push(now); if(t.length<=n) requestAnimationFrame(f); else {
    const d=t.slice(1).map((v,i)=>v-t[i]).sort((a,b)=>a-b); done({median:+d[d.length>>1].toFixed(1), mean:+(d.reduce((a,b)=>a+b,0)/d.length).toFixed(1)}); } };
  requestAnimationFrame(f); })"""
SETTLED = "()=>game.world.isAreaLoaded(game.player.x, game.player.z, 6) && game.renderer.isAreaMeshed(Math.floor(game.player.x/16), Math.floor(game.player.z/16), 6) && !(game.world.arrived||[]).length"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=ARGS + ['--enable-precise-memory-info'])
    page = b.new_page(viewport={'width': 1280, 'height': 720})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)[:300]))
    page.goto('file://' + os.path.abspath(path)); page.wait_for_timeout(800)
    r = {'build': label}
    t0 = time.time()
    page.evaluate("()=>game.newWorld(12345)")
    while page.evaluate("()=>game.state") != 'playing' and time.time() - t0 < 300: page.wait_for_timeout(200)
    r['load s'] = round(time.time() - t0, 1)
    page.evaluate("()=>{ game.input.update = ()=>{}; game.input.state = game.input.emptyState(); game.settings.renderDistance = 12; }")
    def settle():
        for _ in range(240):
            page.wait_for_timeout(500)
            if page.evaluate(SETTLED): break
        page.wait_for_timeout(1000)
    def measure(name, js, clouds_toggle=False):
        page.evaluate("()=>{ const p=game.player; p.flying=true; p.vx=p.vy=p.vz=0; " + js + " }")
        settle()
        for clouds in ([True, False] if clouds_toggle else [True]):
            page.evaluate(f"()=>{{ game.settings.clouds = {str(clouds).lower()}; }}")
            page.wait_for_timeout(500)
            f = page.evaluate(FRAMES, 30)
            info = page.evaluate("()=>{ const i=game.renderer.gl.info.render; return [i.triangles, i.calls]; }")
            key = name + ('' if not clouds_toggle else (' clouds on' if clouds else ' clouds off'))
            r[key] = {'frame ms median': f['median'], 'mean': f['mean'], 'triangles': info[0], 'draw calls': info[1]}
        page.evaluate("()=>{ game.settings.clouds = true; }")
    measure('lake', "p.x=-136.5; p.z=72.5; p.y=60; p.yaw=-1.3; p.pitch=-0.35; game.time=0.25;", True)
    measure('sky', "p.x=-3.5; p.z=0.5; p.y=game.world.generator.column(-4,0).h+2; p.yaw=0.5; p.pitch=0.35; game.time=0.25;", True)
    measure('underwater', "p.x=-126.5; p.z=72.5; p.y=52.5; p.yaw=0.3; p.pitch=0.7; game.time=0.25;")
    # meshing: rebuild every section within 2 chunks of the lake, timed
    page.evaluate("()=>{ const p=game.player; p.x=-130.5; p.z=72.5; p.y=60; }"); settle()
    r['mesh ms per section'] = page.evaluate("""()=>{ const R=game.renderer, cx=Math.floor(game.player.x/16), cz=Math.floor(game.player.z/16), keys=[];
        for(const k of R.sections.keys()){ const [x,z]=k.split(',').map(Number); if(Math.abs(x-cx)<=2&&Math.abs(z-cz)<=2) keys.push(k); }
        const t0=performance.now(); for(let rep=0;rep<3;rep++) for(const k of keys) R.rebuild(k); return +((performance.now()-t0)/keys.length/3).toFixed(2); }""")
    if page.evaluate("()=>!!game.world.lighting"):
        r['light ms per chunk'] = page.evaluate("""()=>{ const w=game.world, list=[...w.chunks.values()].slice(0,10); let total=0;
            for(const c of list){ const copy=new c.constructor(c.cx,c.cz,c.sections); const t0=performance.now(); w.lighting.lightChunk(copy); total+=performance.now()-t0; w.chunks.set(c.cx+','+c.cz,c); }
            return +(total/list.length).toFixed(2); }""")
    if page.evaluate("()=>!!game.renderer.clouds"):
        r['cloud rebuild ms'] = page.evaluate("""()=>{ const c=game.renderer.clouds, sky=game.renderer.sky.state, e=game.renderer.camera.position.clone(); let total=0;
            for(let i=0;i<10;i++){ e.z+=12; const t0=performance.now(); c.update(e, 0, sky); total+=performance.now()-t0; } return +(total/10).toFixed(2); }""")
        r['cloud triangles'] = page.evaluate("()=>game.renderer.clouds.mesh.geometry.index.count/3")
    r['js heap MB'] = page.evaluate("()=>+(performance.memory.usedJSHeapSize/1048576).toFixed(0)")
    r['errors'] = errors[:3]
    print(json.dumps(r))
    b.close()
