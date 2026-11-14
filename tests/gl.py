from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    for args in (['--no-sandbox'], ['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']):
        b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=args); pg=b.new_page()
        print(args, pg.evaluate("""()=>{ const c=document.createElement('canvas'); const g=c.getContext('webgl2'); if(!g) return 'no webgl2';
          const e=g.getExtension('WEBGL_debug_renderer_info'); return { renderer: e? g.getParameter(e.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER), max3d: g.getParameter(g.MAX_3D_TEXTURE_SIZE), maxTex: g.getParameter(g.MAX_TEXTURE_SIZE), floatRT: !!g.getExtension('EXT_color_buffer_float') }; }"""))
        b.close()
