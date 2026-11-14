from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']); pg=b.new_page()
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    print(pg.evaluate("""()=>{
      const pl=[], sh={}; for(let b=0;b<NB;b++){ if(IS_PLANT[b]) pl.push(b+':'+(NAMES[b]||'?')+(IS_FLOWER[b]?'(F)':IS_CROP(b)?'(C)':IS_CANE(b)?'(cane)':(b===CORN_TOP||b===GRAPE_TOP)?'(top)':'(tuft?)'));
        if(IS_SHAPED[b]){ const k = IS_DOOR[b]?'door':IS_BED[b]?'bed':IS_WINDOW[b]?'window':IS_LANTERN[b]?'lantern':IS_VINE[b]?'vine':IS_PORTAL[b]?'portal':b===FIRE?'fire':IS_WBP[b]?'wbp':IS_FENCE[b]?'fence':IS_GATE[b]?'gate':IS_STAIR[b]?'stair':IS_SLAB[b]?'slab':'other'; sh[k]=(sh[k]||0)+1; } }
      let maxBoxes=0, tot=0; for(let b=0;b<NB;b++) if(IS_SHAPED[b]&&SH_BOXES[b]){ maxBoxes=Math.max(maxBoxes,SH_BOXES[b].length); tot+=SH_BOXES[b].length; }
      const other=[]; for(let b=0;b<NB;b++) if(IS_SHAPED[b] && !(IS_DOOR[b]||IS_BED[b]||IS_WINDOW[b]||IS_LANTERN[b]||IS_VINE[b]||IS_PORTAL[b]||b===FIRE||IS_WBP[b]||IS_FENCE[b]||IS_GATE[b]||IS_STAIR[b]||IS_SLAB[b])) other.push(b+':'+(NAMES[b]||'?'));
      return JSON.stringify({plants:pl, shaped:sh, maxBoxes, totalBoxes:tot, otherShaped:other.slice(0,40), crops:CROPDEFS.map(d=>d.key+'/'+d.stages), tiles:Object.keys(TILES).filter(k=>/win|bar/i.test(k))});
    }"""))
