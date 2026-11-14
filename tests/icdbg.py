from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':1100,'height':560}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','ic'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{ if(document.getElementById('classMenu').classList.contains('show')){ classPick='warrior'; confirmClass(); } }")
    print(pg.evaluate("""()=>{ const ids=[IRON_ORE,ADAM_ORE,MITH_ORE,IRON_INGOT,ADAM_INGOT,MITH_INGOT,...Array.from({length:15},(_,i)=>METAL_TOOL0+i),...Array.from({length:20},(_,i)=>1111+i)];
            const c=document.createElement('canvas'); c.width=1100; c.height=100; c.id='sheetC'; c.style.cssText='position:fixed;left:0;top:0;z-index:99999;background:#3a3a3a;image-rendering:pixelated';
            const g=c.getContext('2d'); g.imageSmoothingEnabled=false; ids.forEach((id,i)=>g.drawImage(iconCanvas(id),(i%27)*40+4,Math.floor(i/27)*46+6,36,36)); document.body.appendChild(c);
            const d=g.getImageData(0,0,1100,100).data; let n=0; for(let i=0;i<d.length;i+=4) if(d[i+3]&&d[i]!==0x3a) n++; return [ids.length,n]; }"""))
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/icons.png', clip={'x':0,'y':0,'width':1100,'height':100}); print(errs)
