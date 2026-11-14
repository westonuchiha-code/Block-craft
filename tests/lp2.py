from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':780,'height':390}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','lp2'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    r=pg.evaluate("""()=>{
      const x=Math.floor(player.x)+3, z=Math.floor(player.z), y=Math.floor(player.y)+10;
      // sealed pocket high in the air: stone box with a lamp
      for(let a=-2;a<=2;a++)for(let c=-2;c<=2;c++)for(let d=-1;d<=3;d++) setB(x+a,y+d,z+c,STONE);
      for(let a=-1;a<=1;a++)for(let c=-1;c<=1;c++)for(let d=0;d<=2;d++) setB(x+a,y+d,z+c,AIR);
      setB(x,y+2,z,LAMP);
      const on=getLightAt(x+1,y,z); toggleLamp(x,y+2,z); const off=getLightAt(x+1,y,z); toggleLamp(x,y+2,z); const on2=getLightAt(x+1,y,z);
      // use via placeBlock: aim at the lamp
      toggleLamp(x,y+2,z); const viaFn=getLightAt(x+1,y,z); toggleLamp(x,y+2,z);
      return {on,off,on2,viaFn}}""")
    print(r,errs); b.close()
