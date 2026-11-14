from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']); pg=b.new_page()
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    for n in ['IRON_SWORD','IRON_PICK','IRON_AXE']:
        print(n, pg.evaluate("(n)=>{ const id=eval(n); const c=heldCells(id); const g=Array.from({length:16},()=>Array(16).fill('.')); for(const q of c) g[q.y][q.x]= q.col[0]>150?'#':q.col[0]>100?'o':'x'; return JSON.stringify(toolSprite(id).grip)+'\\n'+g.map(r=>r.join('')).join('\\n'); }", n))
    b.close()
