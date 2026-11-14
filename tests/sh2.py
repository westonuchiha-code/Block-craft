from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','sh2'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    r=pg.evaluate("""()=>{
      tod=0.3; const out={};
      const px=Math.floor(player.x), pz=Math.floor(player.z), gy=Math.floor(player.y)-1;
      for(let dx=-8;dx<=8;dx++) for(let dz=-14;dz<=2;dz++){ setB(px+dx,gy,pz+dz,GRASS); for(let y=gy+1;y<gy+8;y++) setB(px+dx,y,pz+dz,AIR); }
      // real staircase: stair k at height k, backed by full blocks, tall side pointing north (facing 0)
      for(let k=0;k<4;k++){ for(let h=0;h<k;h++) setB(px,gy+1+h,pz-3-k,COBBLE); setB(px,gy+1+k,pz-3-k,stairId(4,0,0)); }
      player.x=px+0.5; player.z=pz+0.5; player.y=gy+1; player.yaw=0; player.pitch=0;
      out.px=px; out.pz=pz; out.gy=gy; return out; }""")
    print(r)
    pg.keyboard.down('w'); pg.wait_for_timeout(3500); pg.keyboard.up('w')
    print('after walk', pg.evaluate("[player.x,player.y,player.z]"))
    # placement via placeBlock: hold a slab, aim at ground ahead and place; then second slab on top -> full block
    r=pg.evaluate("""()=>{ const out={};
      const px=Math.floor(player.x), pz=Math.floor(player.z);
      player.x=px+3.5-3; player.z=pz+8; 
      const gy=r0=0; return out; }""")
    r=pg.evaluate("""()=>{ const out={};
      player.x=5.5; player.z=5.5; player.y=Math.floor(player.y); 
      // find ground y
      let gy=119; while(gy>0 && PASS[getB(5,gy,2)]) gy--; 
      player.y=gy+1+0; player.x=5.5; player.z=5.5; player.yaw=0; player.pitch=-0.6;
      for(let dz=-8;dz<=0;dz++) for(let y=gy+1;y<gy+6;y++) setB(5,y,5+dz-0,AIR);
      const s=slabId(0,0); inv[s]=5; inv[stairId(1,0,0)]=3; HOTBAR[0]=s; HOTBAR[1]=stairId(1,0,0); sel=0;
      const t=target(); out.tgt=t&&[t.x,t.y,t.z,t.ny];
      placeBlock();
      out.placed=[]; for(let dz=-8;dz<=0;dz++) for(let y=gy;y<gy+4;y++){ const b=getB(5,y,5+dz); if(b>=256) out.placed.push([dz,y-gy,b]); }
      out.inv=inv[s];
      return out; }""")
    print(r)
    r=pg.evaluate("""()=>{ const out={}; let gy=119; while(gy>0 && PASS[getB(5,gy,2)]) gy--;
      // aim down at slab top and place a second slab: merge
      let c=null; for(let dz=-8;dz<=0;dz++){ const b=getB(5,gy+1,5+dz); if(IS_SLAB[b]) c=[5,gy+1,5+dz]; }
      out.c=c; if(!c) return out;
      player.x=c[0]+0.5; player.z=c[2]+0.5+0.0; player.y=gy+2.0+0.5; player.pitch=-1.55; player.z=c[2]+0.5; // above looking straight down
      const t=target(); out.t=t&&[t.x,t.y,t.z,t.ny];
      placeBlock(); out.after=getB(c[0],c[1],c[2]); out.isCobbleBase=out.after===SH_BASE[slabId(0,0)];
      // break it again
      return out; }""")
    print(r)
    # save/load roundtrip: old format decode
    r=pg.evaluate("""()=>{
      const m=new Map([[5,300],[7,4],[9,268]]); const s=encodeRegion([[1,2,m]]); const d=decodeRegion(s);
      // old format string: uint32 count=1, cx,cz, cnt=2, (idx uint16,id uint8)
      const buf=new ArrayBuffer(4+12+6), dv=new DataView(buf); dv.setUint32(0,1,true); dv.setInt32(4,3,true); dv.setInt32(8,4,true); dv.setUint32(12,2,true);
      dv.setUint16(16,10,true); dv.setUint8(18,77); dv.setUint16(19,11,true); dv.setUint8(21,88);
      let st=''; for(const x of new Uint8Array(buf)) st+=String.fromCharCode(x);
      const o=decodeRegion(btoa(st));
      return [JSON.stringify([...d[0][2]]), d[0][0], d[0][1], JSON.stringify(o[0][0]+','+o[0][1]+':'+JSON.stringify([...o[0][2]]))]; }""")
    print(r, errs)
    b.close()
