from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m: errs.append('C:'+m.text) if m.type=='error' else None)
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.evaluate("()=>document.getElementById('testBtn').click()"); pg.wait_for_timeout(4000)
    print(pg.evaluate("""()=>{ const r={}; r.names=[DYE0,WOOL0,WOOL0+3,STAINED0+5,RUG0+2].map(i=>NAMES[i]); r.drops=[DROP[RUG0+2]];
      r.recipes=RECIPES.filter(x=>/dye|Dye|wool|rugs|Stained/.test(x.name)).length;
      r.icons=[DYE0+3,WOOL0+2,STAINED0+1,RUG0+4].every(i=>!!iconCanvas(i));
      return r; }"""))
    pg.evaluate("""()=>{ health=20; paused=false; const o=testPlan().rooms[6]; player.x=o.x0+6; player.z=TEST_Z+o.side*(4+6); player.y=TEST_FY+1; player.yaw=Math.PI; player.pitch=-0.5; lastPCX=null; updateChunks(); }""")
    pg.wait_for_timeout(2500)
    pg.screenshot(path='/tmp/dy1.png',clip={'x':0,'y':60,'width':390,'height':330})
    # crafting check: flower -> dye -> wool -> dyed wool -> rug
    print(pg.evaluate("""()=>{ for(const k in inv) delete inv[k]; inv[FLOWER0+1]=1; inv[HAY]=1; inv[GLASS]=4; const r=[];
      const find=n=>RECIPES.find(x=>x.name.startsWith(n)); const craft=x=>{ for(const k in x.ing) if((inv[k]||0)<x.ing[k]) return false; for(const k in x.ing) inv[k]-=x.ing[k]; inv[x.out[0]]=(inv[x.out[0]]||0)+x.out[1]; return true; };
      r.push(craft(find('blue dye'))); r.push(craft(find('Wool (placeholder'))); r.push(craft(find('Dye wool blue'))); r.push(craft(find('Stained glass blue')));
      inv[WOOL0+2]=2; r.push(craft(find('blue rugs'))); r.push([inv[DYE0+1],inv[WOOL0+2],inv[STAINED0+1],inv[RUG0+2]]); return r; }"""))
    print(errs); b.close()
