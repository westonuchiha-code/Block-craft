from playwright.sync_api import sync_playwright
import json, sys
# Planning ahead on another core: the worker's plans for villages, crypts, road edges and delves are exactly what the game works out
# itself; they arrive for the land around you before you reach it; and the first chunk of new land then generates without a freeze.
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/blockcraft_prototype.html'
bad=[]
SNAP = """()=>{ const J=v=>JSON.stringify(v, (k,x)=> x instanceof Map ? { __map:[...x.entries()].sort((a,b)=>String(a[0])<String(b[0])?-1:1) } : x instanceof Set ? { __set:[...x].sort() } : ArrayBuffer.isView(x) ? Array.from(x) : x);
  const o={}; const S=(name,M)=>{ const keys=[...M.keys()].sort((a,b)=>String(a)<String(b)?-1:1); o[name]=keys.map(k=>[k, J(M.get(k))]); };
  S('villages', villageCache); S('crypts', cryptByNum); S('edges', roadEdgeCache); S('delves', delveByNum); return o; }"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto(F); pg.wait_for_timeout(1500)
    pg.fill('#newName','plan'); pg.fill('#newSeed','5151'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    pg.evaluate("()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; travT=1e9; }")
    got=0
    for i in range(40):
        pg.wait_for_timeout(1500); st=pg.evaluate("()=>[PLN.got, PLN.asked.size, PLN.fail, PLN.err||'', !!PLN.w]")
        got=st[0]
        if st[1]>=25 and not pg.evaluate("()=>PLN.busy"): break
    print('worker', st)
    if not (st[0]>=20 and not st[2] and st[3]=='' and st[4]): bad.append('the worker plans the land around you')
    # 1. what it sent is what the game would have worked out: forget everything, work it all out here, and compare
    pg.evaluate("()=>{ PLN.busy=true; paused=true; }")
    A=pg.evaluate(SNAP)
    B=pg.evaluate("(function(){ const keys={ v:[...villageCache.keys()], c:[...cryptByNum.keys()], e:[...roadEdgeCache.keys()], d:[...delveByNum.keys()] }; "
      "villageCache.clear(); cryptCache.clear(); cryptByNum.clear(); delveByNum.clear(); roadEdgeCache.clear(); roadChunkCache.clear(); roadMemoCx=1e9; cryptMemoRx=1e9; delveMemoRx=1e9; surfaceCache.clear(); colCache.clear(); "
      "const un=k=>{ const rx=Math.floor((k+65536)/131072); return [rx, k-rx*131072]; }; "
      "for(const k of keys.v){ const q=un(k); villageAt(q[0],q[1]); } for(const k of keys.c){ const q=un(k); cryptPlan(q[0],q[1]); } for(const k of keys.e){ const q=un(k); roadEdgesNear(q[0],q[1]); } for(const k of keys.d){ const q=un(k); delvePlan(q[0],q[1]); } "
      "return ("+SNAP+")(); })")
    same={}
    for name in ['villages','crypts','edges','delves']:
        a=dict((str(k),v) for k,v in A[name]); bb=dict((str(k),v) for k,v in B[name])
        common=[k for k in a if k in bb]; diff=[k for k in common if a[k]!=bb[k]]
        same[name]=[len(a), len(common), len(diff)]
        if diff: print('  differs:', name, diff[:3], a[diff[0]][:200], '|||', bb[diff[0]][:200])
    print('compared (sent, also worked out here, different):', json.dumps(same))
    if any(v[2]>0 for v in same.values()) or same['villages'][1]<10 or same['delves'][1]<10 or same['edges'][1]<5 or same['crypts'][1]<10: bad.append('the plans match')
    # 2. the freeze: the first chunk of land the worker has planned, against the first chunk of land nobody has
    t=pg.evaluate("""()=>{ const T=f=>{ const t=performance.now(); f(); return +(performance.now()-t).toFixed(1); };
      const prx=Math.floor(player.x/DRS), prz=Math.floor(player.z/DRS), o={warm:[], cold:[]};
      for(const [a,c] of [[2,0],[-2,1],[1,2],[0,-2]]) o.warm.push(T(()=>genChunk(Math.floor(((prx+a)*DRS+120)/CS), Math.floor(((prz+c)*DRS+120)/CS))));
      for(const [a,c] of [[9,3],[-11,5],[14,-9],[7,12]]) o.cold.push(T(()=>genChunk(Math.floor(((prx+a)*DRS+120)/CS), Math.floor(((prz+c)*DRS+120)/CS))));
      return o; }""")
    print('first chunk of new land, ms:', json.dumps(t), errs)
    if not (max(t['warm'])<40 and max(t['cold'])>2*max(t['warm'])): bad.append('no freeze on planned land')
    # 3. far country is let go, near country is kept, and the worker carries on afterwards
    m=pg.evaluate("""()=>{ const prx=Math.floor(player.x/VREG), prz=Math.floor(player.z/VREG), near=villageAt(prx,prz), o={};
      for(let a=30;a<70;a++) for(let c=-8;c<8;c++) villageAt(prx+a, prz+c);                       // as if you had been a long way east
      o.before=villageCache.size; o.dropped=plTrim(true); o.after=villageCache.size; o.nearKept=villageAt(prx,prz)===near; o.farGone=!villageCache.has(chunkKey(prx+50,prz));
      o.again=!!villageAt(prx+50,prz) || villageAt(prx+50,prz)===null; paused=false; PLN.busy=false; o.got0=PLN.got; player.x+=4*DRS; lastPCX=null; return o; }""")
    for i in range(30):
        pg.wait_for_timeout(1500); g=pg.evaluate("()=>[PLN.got, PLN.fail, PLN.err||'']")
        if g[0]>m['got0']+2: break
    print('trim', json.dumps(m), 'worker after', g)
    if not (m['before']>600 and m['dropped']>300 and m['after']<m['before']-300 and m['nearKept'] and m['farGone'] and m['again'] and g[0]>m['got0']+2 and not g[1] and g[2]==''): bad.append('far country is let go')
    b.close()
print('PLAN TEST FAILED', bad) if bad else print('plan ok')
sys.exit(1 if (bad or errs) else 0)
