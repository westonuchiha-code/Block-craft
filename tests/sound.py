from playwright.sync_api import sync_playwright
import json, sys
# Sound: every effect renders to a real, non-clipping signal, and the game's events (steps, digging, placing, hurting, chests,
# doors, pickups, spells, toasts, creatures) each trigger theirs. Nothing here can judge how it SOUNDS; that needs ears.
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    pg=b.new_page(viewport={'width':1100,'height':560}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','sound'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(5000)
    r=pg.evaluate("""async ()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const o={}; const sleep=t=>new Promise(r=>setTimeout(r,t));
      // 1. render every effect off-line and measure it
      o.fx={}; const mats=['grass','stone','wood','sand','snow','water'];
      for(const name of Object.keys(SOUNDS)){ for(const m of (name==='step'||name==='hit'||name==='brk' ? mats : [''])){
          const ac=new OfflineAudioContext(1, 44100*1.6, 44100); SOUNDS[name](ac, ac.destination, 0.01, {m});
          const buf=await ac.startRendering(), d=buf.getChannelData(0); let peak=0, sum=0, bad=0; for(let i=0;i<d.length;i++){ const v=d[i]; if(!isFinite(v)) bad++; const a=Math.abs(v); if(a>peak) peak=a; sum+=v*v; }
          let last=0; for(let i=d.length-1;i>=0;i--) if(Math.abs(d[i])>0.002){ last=i; break; }
          o.fx[name+(m?':'+m:'')]=[+peak.toFixed(3), +Math.sqrt(sum/d.length).toFixed(4), +(last/44100).toFixed(2), bad]; } }
      // 2. the game's events trigger their sounds
      sndInit(); o.ctx=SND.ac ? SND.ac.state : null; o.vol=SND.vol; const c=n=>SND.count[n]||0; const base=Object.assign({},SND.count);
      let F=null; for(let x=-200;x<200&&!F;x+=5) for(let z=-200;z<200&&!F;z+=5){ const q=colInfo(x,z); if(q.top===GRASS&&!q.open&&q.h>SEA+2&&!nearVillage(x,z)) F=[x,z,q.h]; }
      player.x=F[0]+0.5; player.z=F[1]+0.5; player.y=F[2]+1; lastPCX=null; updateChunks(); await sleep(2500); for(let k=F[2]+1;k<F[2]+5;k++) for(let a=-2;a<=2;a++) for(let e=-2;e<=2;e++) setB(F[0]+a,k,F[1]+e,AIR);
      player.onGround=true; const s0=c('step'); for(let i=0;i<10;i++) sndTick(0.3, 0.016); o.steps=c('step')-s0; o.stepMat=sndMat(getB(F[0],F[2],F[1]));
      o.mats=[sndMat(STONE), sndMat(PLANK_IDS[0]), sndMat(SAND), sndMat(SNOW), sndMat(GRASS), sndMat(WATER)];
      const x=F[0], z=F[1]-2, y=F[2]+1; setB(x,y,z,COBBLE); setB(x,y+1,z,COBBLE); player.yaw=0; player.pitch=-0.2; await sleep(300);
      const h0=c('hit'), b0=c('brk'), sw0=c('swing'); for(let i=0;i<40 && getB(x,y+1,z)===COBBLE;i++){ punch(); await sleep(60); } o.dig=[c('hit')-h0>0, c('brk')-b0, c('swing')-sw0>0];
      const p0=c('place'); inv[COBBLE]=5; HOTBAR[sel]=COBBLE; player.pitch=-0.9; await sleep(200); const tg=target(); o.aim=tg ? NAMES[tg.b] : null; placeBlock(); await sleep(100); o.place=c('place')-p0; player.pitch=-0.2;
      const u0=c('hurt'); hurt(1, true); o.hurt=c('hurt')-u0; health=maxHP();
      const ch0=c('chest'); setB(x+2,y,z,CHEST); openChest(x+2,y,z); closeChest(); o.chest=c('chest')-ch0;
      const d0=c('door'); toggleDoor(x,y,z); o.door=c('door')-d0;
      const f0=c('fire'), l0=c('bolt'); fx.push({ kind:'boom', x:player.x, y:player.y+1, z:player.z-3, age:0, seed:1, size:0.5 }); fx.push({ kind:'bolt', pts:[[player.x,player.y+2,player.z-3],[player.x,player.y,player.z-3]], age:0 }); o.spells=[c('fire')-f0, c('bolt')-l0];
      const t0=c('chime'), ff0=c('fanfare'); skillToast('SOMEWHERE<br><small>discovered</small>', true); skillToast('QUEST DONE<br><small>+5 gold</small>', true); skillToast('+3 gold'); o.toasts=[c('chime')-t0, c('fanfare')-ff0];
      const g0=c('growl'), hs0=c('hiss'), rt0=c('rattle'); sndAggro({kind:'bear',x:player.x+3,y:player.y,z:player.z}); sndAggro({kind:'spider',x:player.x+3,y:player.y,z:player.z}); sndAggro({kind:'skeleton',x:player.x+3,y:player.y,z:player.z}); sndAggro({kind:'bear',x:player.x+300,y:player.y,z:player.z}); o.voices=[c('growl')-g0, c('hiss')-hs0, c('rattle')-rt0];
      const pk0=c('pop'), cn0=c('coin'); spawnDrop(Math.floor(player.x),Math.floor(player.y),Math.floor(player.z),COBBLE); spawnGold(Math.floor(player.x),Math.floor(player.y),Math.floor(player.z),3); await sleep(2500); o.pickups=[c('pop')-pk0>0, c('coin')-cn0>0];
      // 3. the volume button
      const sb=document.getElementById('sndBtn'); const seen=[]; for(let i=0;i<4;i++){ sb.click(); seen.push(sb.textContent); } o.button=seen; o.saved=localStorage.getItem('bc_snd'); o.beds=!!(SND.wind && SND.rain);
      return o; }""")
    fx=r.pop('fx'); print(json.dumps(r)); print(errs)
    silent=[k for k,v in fx.items() if v[0]<0.03]; clip=[k for k,v in fx.items() if v[0]>0.95]; nan=[k for k,v in fx.items() if v[3]]; long_=[k for k,v in fx.items() if v[2]>1.3]
    print('effects', len(fx), 'loudest', max(fx.items(), key=lambda kv: kv[1][0]), 'quietest', min(fx.items(), key=lambda kv: kv[1][0]))
    print('silent', silent, 'clipping', clip, 'not finite', nan, 'too long', long_)
    ok=(not silent and not clip and not nan and not long_ and len(fx)>=30 and r['ctx'] in ('running','suspended') and 2<=r['steps']<=3 and r['stepMat']=='grass' and r['mats']==['stone','wood','sand','snow','grass','water']
        and r['dig'][0] and r['dig'][1]==1 and r['dig'][2] and r['place']==1 and r['hurt']==1 and r['chest']==1 and r['door']==1 and r['spells']==[1,1] and r['toasts']==[1,1] and r['voices']==[1,1,1] and r['pickups']==[True,True]
        and len(set(r['button']))==4 and any('OFF' in t for t in r['button']) and r['beds'])
    if not ok: bad.append('sound')
    b.close()
print('SOUND TEST FAILED', bad) if bad else print('sound ok')
sys.exit(1 if (bad or errs) else 0)
