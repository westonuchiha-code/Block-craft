from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':780}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','lp'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    r=pg.evaluate("""()=>{
      const x=Math.floor(player.x)+3, z=Math.floor(player.z), y=Math.floor(player.y)+8; const out={};
      const lightOf=(bx,by,bz)=>{const c=getChunk(Math.floor(bx/CS),Math.floor(bz/CS)); return Array.from(c.light||c.lt||[]).length};
      setB(x,y,z,LAMP); setB(x+4,y,z,LANTERN0+1); setB(x+8,y,z,LANTERN0);
      out.on=[getB(x,y,z),getB(x+4,y,z),getB(x+8,y,z)];
      out.t1=[toggleLamp(x,y,z),toggleLamp(x+4,y,z),toggleLamp(x+8,y,z)];
      out.off=[getB(x,y,z),getB(x+4,y,z),getB(x+8,y,z)];
      out.emit=[IS_EMIT[getB(x,y,z)],IS_EMIT[getB(x+4,y,z)],IS_EMIT[getB(x+8,y,z)]];
      out.drops=[DROP[LAMP_OFF],DROP[LANT_OFF0],DROP[LANT_OFF0+1]];
      toggleLamp(x,y,z);toggleLamp(x+4,y,z);toggleLamp(x+8,y,z);
      out.back=[getB(x,y,z),getB(x+4,y,z),getB(x+8,y,z)]; out.exp=[LAMP,LANTERN0+1,LANTERN0];
      out.toggleStone=toggleLamp(x,y-5,z);
      out.shLamp=[SH_HALF[LANT_OFF0],SH_HALF[LANT_OFF0+1],IS_LANTERN[LANT_OFF0]];
      return out}""")
    print(r,errs); b.close()
