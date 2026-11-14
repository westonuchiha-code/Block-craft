from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for name,vp in [('port',{'width':390,'height':780}),('land',{'width':780,'height':390})]:
        pg=b.new_page(viewport=vp,device_scale_factor=2)
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
        pg.evaluate("document.getElementById('menu').classList.add('show')")
        pg.click('#charBtn'); pg.wait_for_timeout(800)
        pg.screenshot(path=f'/tmp/cc_{name}_hair.png')
        if name=='port':
            pg.click('#ccTabs button:nth-child(3)'); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/cc_port_face.png')
            pg.click('#ccTabs button:nth-child(4)'); pg.wait_for_timeout(300); pg.screenshot(path='/tmp/cc_port_chest.png')
        print(name,errs)
    b.close()
