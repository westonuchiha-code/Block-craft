from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1100,'height':560})
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','sw'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3500)
    print(pg.evaluate("""()=>{ const v=nearestVillage(2); window.V=v; update=function(){}; mobs.length=0; tod=0.3; const S=v.sewer;
      return S && {arms:S.arms, Fs:S.Fs, g:v.g, rooms:S.rooms.map(r=>[r.x-v.cx,r.z-v.cz,r.kind]), hut:S.hut}; }"""), errs)
    shots=[('hut',"player.x=V.cx+7.5; player.z=V.cz+0.5; player.y=V.g+1; player.yaw=Math.PI/2; player.pitch=0.05;"),
           ('stair',"player.x=V.sewer.hut[0]-0.5+0.0; player.z=V.sewer.hut[2]+0.5; player.y=V.sewer.hut[1]; player.yaw=0.3; player.pitch=-0.9;"),
           ('tunnel',"player.x=V.cx+9.5; player.z=V.cz+1.5; player.y=V.sewer.Fs+1; player.yaw=-Math.PI/2; player.pitch=0.0;"),
           ('cistern',"player.x=V.cx+4.5; player.z=V.cz+3.5; player.y=V.sewer.Fs+1; player.yaw=-Math.PI/2-0.5; player.pitch=0.15;"),
           ('room0',"const r=V.sewer.rooms[0]; if(r){ const dx=Math.sign(Math.round(r.x-V.cx)), dz=Math.sign(Math.round(r.z-V.cz)); player.x=r.x-dx*3; player.z=r.z-dz*3; player.y=r.y; player.yaw=Math.atan2(dx,-dz); player.pitch=0.0; }"),
           ('room2',"const r=V.sewer.rooms[V.sewer.rooms.length-1]; if(r){ const dx=Math.sign(Math.round(r.x-V.cx)), dz=Math.sign(Math.round(r.z-V.cz)); player.x=r.x-dx*3; player.z=r.z-dz*3; player.y=r.y; player.yaw=Math.atan2(dx,-dz); player.pitch=0.0; }")]
    for n,js in shots:
        pg.evaluate("()=>{ "+js+" lastPCX=null; updateChunks(); }"); pg.wait_for_timeout(1500); pg.screenshot(path='/tmp/sw_%s.png'%n,clip={'x':0,'y':60,'width':390,'height':330})
    print(pg.evaluate("[WK.on, WK.err||null]"), errs); b.close()
