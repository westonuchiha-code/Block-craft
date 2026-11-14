from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','hs'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    r=pg.evaluate("""async ()=>{ const sleep=t=>new Promise(r=>setTimeout(r,t)); const out={};
      // find flat ground away from villages
      let X=null; for(let x=-400;x<400&&!X;x+=3)for(let z=-400;z<400;z+=3){ const c=colInfo(x,z); if(c.top===GRASS&&!c.open&&c.h>SEA+2&&!nearVillage(x,z)){ let ok=true; for(let a=-8;a<=8&&ok;a+=2)for(let b2=-8;b2<=8;b2+=2){ const q=colInfo(x+a,z+b2); if(Math.abs(q.h-c.h)>0){ ok=false; break; } } if(ok){ X=[x,z,c.h]; break; } } }
      const [x0,z0,h]=X; player.x=x0+0.5; player.z=z0-8; player.y=h+1; await sleep(1500);
      for(let i=-9;i<=9;i++) for(let j=-9;j<=9;j++){ for(let k=h+1;k<=h+8;k++) setB(x0+i,k,z0+j,AIR); setB(x0+i,h,z0+j,GRASS); }
      // build a 5x5 room (walls 7x7 outer), roof, door on north side
      const house=(cx,cz,station)=>{ for(let i=-3;i<=3;i++) for(let j=-3;j<=3;j++){ const wall = Math.abs(i)===3||Math.abs(j)===3; setB(cx+i,h,cz+j,PLANKS); for(let k=1;k<=3;k++) if(wall) setB(cx+i,h+k,cz+j,PLANKS); setB(cx+i,h+4,cz+j,PLANKS); }
        setB(cx,h+1,cz-3,doorId(0,0,0,0,0)); setB(cx,h+2,cz-3,doorId(0,0,0,1,0)); if(station) setB(cx+2,h+1,cz+2,station); };
      house(x0,z0,FURNACE); house(x0+9,z0,COOK_TABLE);
      // an open-roofed shack
      for(let i=-2;i<=2;i++) for(let j=-2;j<=2;j++){ if(Math.abs(i)===2||Math.abs(j)===2){ setB(x0-9+i,h+1,z0+j,PLANKS); setB(x0-9+i,h+2,z0+j,PLANKS);} }
      // place beds via the real placement path
      const putBed=(bx,bz)=>{ inv[BED0]=(inv[BED0]||0)+1; HOTBAR[0]=BED0; sel=0; player.x=bx+0.5; player.z=bz-1.5; player.y=h+1; player.pitch=-1.2; let ba=0,bd=-9; for(let a=0;a<6.283;a+=0.02){ player.yaw=a; const v=camVectors().f; if(v[2]>bd){bd=v[2];ba=a;} } player.yaw=ba; placeBlock(); return IS_BED[getB(bx,h+1,bz)]||IS_BED[getB(bx,h+1,bz+1)]; };
      out.bed1=putBed(x0-1,x0===x0?z0:0); out.check1=JSON.stringify(houseCheck(x0-1,h+1,z0));
      out.hs=homesteads.length && homesteads[0].name; if(!homesteads.length){ out.b=[getB(x0-1,h+1,z0),getB(x0-1,h+1,z0+1),getB(x0-1,h+1,z0-1)].map(b=>NAMES[b]); out.inv=inv[BED0]; out.toast=document.getElementById('skillToast').innerHTML; return out; } out.homes=homesteads[0]&&homesteads[0].homes.map(H=>H.job);
      out.bed2=putBed(x0+8,z0); out.homes2=homesteads[0]&&homesteads[0].homes.map(H=>H.job);
      out.shack=JSON.stringify((()=>{ setB(x0-9,h+1,z0,BED0); setB(x0-9,h+1,z0+1,BED0+1); return houseCheck(x0-9,h+1,z0); })());
      // sunrise: settlers arrive
      for(let d=0; d<4 && homesteads[0].homes.some(H=>!H.ch); d++) homesteadDawn();
      out.settlers=homesteads[0].homes.map(H=>H.ch && (H.ch.name+'/'+H.ch.job));
      player.x=x0+4.5; player.z=z0-6; player.y=h+1; tod=0.3; await sleep(5000);
      out.spawned=mobs.filter(m=>m.kind==='npc'&&m.home&&m.home[0]==='h').map(m=>m.job+':'+m.village.join(''));
      // talk to one, check trade + work
      const s=mobs.find(m=>m.home&&m.home[0]==='h'); openTalk(s); out.talk=document.getElementById('talkGold').textContent; talkAction('news'); out.news=talkLine; talkAction('work'); out.work=talkLine.slice(0,90); talkOffer=null; closeCraft();
      // third settler -> guard
      house(x0,z0+10,null); out.bed3=putBed(x0-1,z0+10); homesteadDawn(); homesteadDawn(); homesteadDawn(); out.third=homesteads[0].homes.map(H=>H.ch&&H.ch.job);
      // break a bed -> they leave at dawn
      const H0=homesteads[0].homes[0]; setB(...H0.bed,AIR); homesteadDawn(); out.afterBreak=homesteads[0].homes[0].ch;
      saveWorld(); return out; }""")
    print(json.dumps(r, indent=0))
    pg.evaluate("()=>openSheet('standing')"); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/hs_sheet.png')
    print(errs[:3]); b.close()
