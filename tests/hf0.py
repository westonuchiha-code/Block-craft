from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/before_furn_houses.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','hf'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ paused=false; update=function(){}; const v=nearestVillage(2); let n=0,t=0,ch=0,bar=0,lan=0, reach=0, tot=0;
      for(const h of v.houses){ tot++; let found=false;
        for(let dx=-7;dx<=7;dx++) for(let dz=-7;dz<=7;dz++) for(let y=h.F;y<=h.F+3;y++){ const b=getB(h.inside[0]+dx,y,h.inside[2]+dz); if(IS_FURN[b]){ if(SH_HALF[b]===1) t++; else ch++; } if(b===BARREL) bar++; }
        // inside to bed reachable on foot (flood fill through free cells at floor level +1/+2)
        const seen=new Set([h.inside[0]+','+h.inside[2]]), q=[[h.inside[0],h.inside[2]]]; const free=(x,z)=>{ const a=getB(x,h.F+1,z), c=getB(x,h.F+2,z); return (a===AIR||PASS[a]||IS_DOOR[a]) && (c===AIR||PASS[c]||IS_DOOR[c]); };
        while(q.length){ const [x,z]=q.pop(); for(const [a,b] of [[1,0],[-1,0],[0,1],[0,-1]]){ const k=(x+a)+','+(z+b); if(!seen.has(k) && free(x+a,z+b) && seen.size<500){ seen.add(k); q.push([x+a,z+b]); } } }
        const bd=h.bed; let adj=false; for(const [a,b] of [[1,0],[-1,0],[0,1],[0,-1]]) if(seen.has((bd[0]+a)+','+(bd[2]+b))) adj=true; if(adj) reach++; }
      const h=v.houses.find(h=>true); window.H=h; return {houses:tot,tables:t,chairs:ch,barrels:bar,bedReach:reach}; }"""))
    print(errs); b.close()
