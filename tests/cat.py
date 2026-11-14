from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1000)
    pg.fill('#newName','ct'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    r=pg.evaluate("""()=>{ const out={};
      // clear any catnip in the player's chunk so we control the test
      const pcx=Math.floor(player.x/CS), pcz=Math.floor(player.z/CS), c=chunks.get(chunkKey(pcx,pcz));
      for(let i=0;i<c.data.length;i++) if(c.data[i]>=196&&c.data[i]<=203) c.data[i]=0;
      scanCatnip(); out.noNip=catnipHere;
      const cnt=()=>mobs.filter(m=>m.kind==='cat').length;
      mobs.length=0; for(let i=0;i<60;i++) trySpawnCats(); out.catsNoNip=cnt();
      const px=pcx*CS+8, pz=pcz*CS+8, py=ratTop(px,pz);
      setB(px,py-1,pz,TILLED_WET); setB(px,py,pz,CATNIP_B0+1); scanCatnip(); out.nip=catnipHere;
      mobs.length=0; for(let i=0;i<120;i++) trySpawnCats(); out.catsNip=cnt();
      return out;}""")
    print(r,errs); b.close()
