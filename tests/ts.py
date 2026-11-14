import sys
from playwright.sync_api import sync_playwright
out=sys.argv[1]
JS="""()=>{
 const names=['dirt','stone','cobble','gravel','sand','coal','planks','plaster','flag','beam','thatch','path','pillSide','cutSide','books','barrel'];
 const list=[]; for(const n of names) list.push([n,TILES[n]]); list.push(['bark27',TILES.bark[27]],['bark7',TILES.bark[7]],['bark28',TILES.bark[28]],['bark29',TILES.bark[29]],['cut27',TILES.cut[27]]);
 for(const n of ['andesite','granite','diorite','tuff','mossrock','ice','sandstone','cactus','ember','iron','snow','bedrock','tuff','granite','andesite','moss','diorite']) if(TILES[n]) list.push([n,TILES[n]]);
 const S=8,cols=7,rows=Math.ceil(list.length/cols), cv=document.createElement('canvas'); cv.width=cols*(16*S+6); cv.height=rows*(16*S+6); const g=cv.getContext('2d'); g.fillStyle='#222'; g.fillRect(0,0,cv.width,cv.height);
 list.forEach(([n,t],i)=>{ const ox=(i%cols)*(16*S+6)+3, oy=Math.floor(i/cols)*(16*S+6)+3; for(let y=0;y<16;y++)for(let x=0;x<16;x++){ const c=t[y][x]; if(!c||!c.length){continue;} g.fillStyle=`rgb(${c[0]|0},${c[1]|0},${c[2]|0})`; g.fillRect(ox+x*S,oy+y*S,S,S);} });
 return cv.toDataURL().split(',')[1]; }"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context().new_page(); pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    import base64; open(out,'wb').write(base64.b64decode(pg.evaluate(JS))); b.close()
