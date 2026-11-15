from playwright.sync_api import sync_playwright
from PIL import Image
import json, sys, base64, io
SCENES = sys.argv[1].split(',') if len(sys.argv)>1 else ['field','village','water','under','k_beasts','k_third','delve','k_delve','tavern']
bad = []
CMP = r"""async (scene)=>{
  const sleep=t=>new Promise(r=>setTimeout(r,t));
  if(!scene.startsWith('k_')) mobs.length=0; beastSpawnT=1e9; ogreSpawnT=1e9; health=1000; camMode=0;
  const go=(x,z,yaw,pitch,t)=>{ player.x=x+0.5; player.z=z+0.5; player.y=colInfo(x,z).h+1; player.yaw=yaw; player.pitch=pitch; if(t!==undefined) tod=t; };
  if(scene==='field'){ let X=null; for(let x=-200;x<200&&!X;x+=7) for(let z=-200;z<200;z+=7){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+3&&!nearVillage(x,z)){ X=[x,z]; break; } } go(X[0],X[1],0.7,-0.12,0.3); }
  if(scene==='village'){ const v=nearestVillage(2); go(v.cx,v.cz+12,0,-0.05,0.3); }
  if(scene==='tavern'){ const v=nearestVillage(2), h=v.houses[v.tavern], dx=(h.out[0]-h.inside[0])/2, dz=(h.out[2]-h.inside[2])/2, x=h.out[0]+dx*4+dz*3, z=h.out[2]+dz*4+dx*3;      // a tavern's front: the hanging lamps and the sign
    go(x,z,Math.atan2(h.out[0]-x,-(h.out[2]-z)),0.22,0.3); }
  if(scene==='night'){ const v=nearestVillage(2); go(v.cx,v.cz+12,0,-0.05,0.8); }
  if(scene==='water'){ let L=null; for(let x=-400;x<400&&!L;x+=6) for(let z=-400;z<400;z+=6){ const c=colInfo(x,z); if(c.h<SEA-4 && getB(x,SEA,z)!==AIR){ L=[x,z]; break; } } player.x=L[0]-6.5; player.z=L[1]+0.5; player.y=SEA+2; player.yaw=1.57; player.pitch=-0.35; tod=0.35; }
  if(scene==='under'){ let P=null; for(let x=0;x<400&&!P;x+=4){ const z=UNDER_Z+40, c=underCol(x,z); if(c.hf>UNDER_LAVA+3 && c.hc-c.hf>14) P=[x,z,c.hf]; } player.x=P[0]+0.5; player.z=P[1]+0.5; player.y=P[2]+1; player.yaw=0.3; player.pitch=-0.15; }
  if(scene==='delve' || scene==='k_delve'){ let P=null; for(let a=-4;a<=4&&!P;a++) for(let b=-4;b<=4&&!P;b++) P=delvePlan(a,b);      // the shrine at the bottom of a delve: caverns, ruins, glow moss, lamps
    const N=P.nodes[P.heart]; player.x=N.cx+0.5; player.z=N.cz-4.5; player.y=N.F+0.01; player.yaw=Math.PI; player.pitch=0.12; lastPCX=null; updateChunks();
    if(scene==='k_delve'){ await sleep(3500); player.x=N.cx+0.5; player.z=N.cz-4.5; player.y=N.F+0.01; mobs.forEach(m=>{ m.idleT=999; m.angry=0; }); } }
  const flat=()=>{ for(let x=-200;x<200;x+=5) for(let z=-200;z<200;z+=5){ const c=colInfo(x,z); if(c.top!==GRASS||c.open||c.h<=SEA+2||nearVillage(x,z)) continue; let ok=true; for(let a=-6;a<=6&&ok;a+=3) for(let b=-6;b<=6;b+=3){ const q=colInfo(x+a,z+b); if(Math.abs(q.h-c.h)>1||q.top!==GRASS){ ok=false; break; } } if(ok) return [x,z,c.h]; } };
  if(scene==='k_beasts'){ mobs.length=0; const [x,z,h]=flat(); player.x=x-6.5; player.z=z+0.5; player.y=h+1; player.yaw=Math.PI/2; player.pitch=-0.15; tod=0.3; await sleep(2500);
    for(let i=-2;i<=2;i++) for(let j=-4;j<=4;j++) for(let k=h+1;k<h+6;k++) setB(x+i+1,k,z+j,AIR);
    const ks=['bear','tiger','spider','scorpion']; ks.forEach((k,i)=>{ const m=newBeast(k,x+1,h+1,z-3+i*2); m.yaw=-Math.PI/2+0.4*i; m.idleT=999; mobs.push(m); });
    mobs.push(newCat(x-2,h+1,z+3)); mobs.push(newRat(x-3,h+1,z-2)); mobs.push(newWb(x+4,h+1,z+5)); const m=mobs[0]; m.hurtT=0.3; }
  if(scene==='k_village'){ const v=nearestVillage(2); player.x=v.cx+0.5; player.z=v.cz+6.5; player.y=colInfo(v.cx,v.cz+6).h+1; player.yaw=0; player.pitch=-0.1; tod=0.3; await sleep(2500);
    const npcs=mobs.filter(m=>m.kind==='npc'); npcs.slice(0,4).forEach((m,i)=>{ m.x=v.cx-1.5+i*1.2; m.z=v.cz+2.5; m.y=colInfo(Math.floor(m.x),Math.floor(m.z)).h; m.path=null; m.idleT=99; }); mobs.length=0; npcs.slice(0,4).forEach(m=>mobs.push(m)); }
  if(scene==='k_ogre'){ mobs.length=0; const [x,z,h]=flat(); player.x=x-7.5; player.z=z+0.5; player.y=h+1; player.yaw=Math.PI/2; player.pitch=0.1; tod=0.3; await sleep(2500); const o=newOgre(x,h+1,z); o.hostile=false; o.idleT=999; mobs.push(o); }
  if(scene==='k_third'){ mobs.length=0; const [x,z,h]=flat(); player.x=x+0.5; player.z=z+0.5; player.y=h+1; player.yaw=0.6; player.pitch=0.3; tod=0.3; await sleep(2500);
    for(let k=0;k<4;k++){ const id=AR(4,k); inv[id]=1; equipArmor(id); } inv[MITH_SWORD]=1; HOTBAR[0]=MITH_SWORD; sel=0; updateHotbar(); camMode=2; mobs.length=0; }
  if(scene==='k_daedra'){ mobs.length=0; let P=null; for(let x=0;x<400&&!P;x+=4){ const z=UNDER_Z+40, c=underCol(x,z); if(c.hf>UNDER_LAVA+3 && c.hc-c.hf>14){ let ok=true; for(let a=-6;a<=6;a+=3) if(Math.abs(underCol(x+a,z).hf-c.hf)>1) ok=false; if(ok) P=[x,z,c.hf]; } }
    player.x=P[0]+0.5; player.z=P[1]+0.5; player.y=P[2]+1; player.yaw=Math.PI/2; player.pitch=-0.1; await sleep(2500); mobs.length=0;
    const d=newBeast('daedra',P[0]+6,P[2]+1,P[1]-1), r=newBeast('daedroth',P[0]+6,P[2]+1,P[1]+2), s=newBeast('skeleton',P[0]+4,P[2]+1,P[1]+4); [d,r,s].forEach(m=>{ m.idleT=999; m.angry=0; mobs.push(m); }); }
  if(!scene.startsWith('k_')){ await sleep(2500); mobs.length=0; }
  for(let i=0;i<3;i++){ for(const c of chunks.values()){} await sleep(200); }
  const t0=performance.now(); const pn=performance.now; performance.now=()=>t0;
  // CPU picture
  GPU.on=false; const won=WK.on; WK.on=false; R_Y0=0; R_STEP=1; render(); const cpu=new Uint8ClampedArray(img.data);
  // GPU picture, same size, same moment
  GPU.force=[RW,RH]; gpuSet(true); GPU.frames=0; gpuRender(); gpuRender();
  const gl=GPU.gl, px=new Uint8Array(RW*RH*4); gl.readPixels(0,0,RW,RH,gl.RGBA,gl.UNSIGNED_BYTE,px);
  const gpu=new Uint8ClampedArray(RW*RH*4); for(let y=0;y<RH;y++) gpu.set(px.subarray((RH-1-y)*RW*4,(RH-y)*RW*4), y*RW*4);
  performance.now=pn; GPU.force=null; gpuSet(false); WK.on=won;
  let n8=0, n24=0, mx=0, sum=0; const diff=new Uint8ClampedArray(RW*RH*4);
  for(let i=0;i<RW*RH;i++){ let m=0; for(let k=0;k<3;k++){ const d=Math.abs(cpu[i*4+k]-gpu[i*4+k]); if(d>m) m=d; } sum+=m; if(m>8) n8++; if(m>24) n24++; if(m>mx) mx=m; const v=Math.min(255,m*4); diff[i*4]=v; diff[i*4+1]=m>24?0:v; diff[i*4+2]=m>24?0:v; diff[i*4+3]=255; }
  const enc=a=>{ const c=document.createElement('canvas'); c.width=RW; c.height=RH; c.getContext('2d').putImageData(new ImageData(a,RW,RH),0,0); return c.toDataURL(); };
  return { scene, err:GPU.err, pct8:+(100*n8/(RW*RH)).toFixed(2), pct24:+(100*n24/(RW*RH)).toFixed(2), mean:+(sum/(RW*RH)).toFixed(2), max:mx, cpu:enc(cpu), gpu:enc(gpu), diff:enc(diff) };
}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.on('console', lambda m: errs.append('console: '+m.text[:300]) if m.type=='error' else None)
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','gc'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    rows=[]
    for sc in SCENES:
        r=pg.evaluate(CMP, sc)
        ims=[Image.open(io.BytesIO(base64.b64decode(r[k].split(',')[1]))).resize((432,270),Image.NEAREST) for k in ('cpu','gpu','diff')]
        row=Image.new('RGB',(432*3+20,270)); [row.paste(im,(i*442,0)) for i,im in enumerate(ims)]; rows.append(row)
        print(json.dumps({k:v for k,v in r.items() if k not in ('cpu','gpu','diff')}))
        if r['err'] or r['pct24'] > 0.5: bad.append(sc)
    S=Image.new('RGB',(rows[0].width, 280*len(rows)))
    for i,rw in enumerate(rows): S.paste(rw,(0,i*280))
    S.save('/tmp/gpucmp.png'); print(errs[:5])
print('GPU MATCH FAILED:', bad) if bad else print('gpu matches cpu in', len(SCENES), 'scenes')
import sys as _s; _s.exit(1 if (bad or errs) else 0)
