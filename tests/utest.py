from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']); pg=b.new_page()
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    print(pg.evaluate(r"""()=>{
      const c=document.createElement('canvas'); c.width=8; c.height=1; const gl=c.getContext('webgl2');
      const vs=`#version 300 es
void main(){ vec2 p = vec2((gl_VertexID<<1)&2, gl_VertexID&2); gl_Position = vec4(p*2.0-1.0, 0.0, 1.0); }`;
      const fs=`#version 300 es
precision highp float; precision highp int; out uvec4 o;
uniform int X[8];
float h3(int x, int y, int z, int s){
  uint h = (uint(x)*0x27d4eb2du) ^ (uint(y)*0x165667b1u) ^ (uint(z)*0x85ebca77u) ^ (uint(s)*0xc2b2ae3du);
  h ^= h>>15u; h *= 0x2c1b3c6du; h ^= h>>12u; h *= 0x297a2d39u; h ^= h>>15u; return float(h>>8u)/16777216.0; }
void main(){ int i=int(gl_FragCoord.x); int x=X[i]; o = uvec4(uint(x), uint(h3(x,-3,7,12400)*16777216.0), 0u, 0u); }`;
      const mk=(t,s)=>{ const sh=gl.createShader(t); gl.shaderSource(sh,s); gl.compileShader(sh); if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(sh); return sh; };
      const pr=gl.createProgram(); gl.attachShader(pr,mk(gl.VERTEX_SHADER,vs)); gl.attachShader(pr,mk(gl.FRAGMENT_SHADER,fs)); gl.linkProgram(pr); gl.useProgram(pr);
      const xs=[-1,-5,-40,-123456,5,0,7,-2]; gl.uniform1iv(gl.getUniformLocation(pr,'X'), xs);
      const tx=gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D,tx); gl.texStorage2D(gl.TEXTURE_2D,1,gl.RGBA32UI,8,1);
      const fb=gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER,fb); gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,tx,0);
      gl.viewport(0,0,8,1); gl.bindVertexArray(gl.createVertexArray()); gl.drawArrays(gl.TRIANGLES,0,3);
      const out=new Uint32Array(32); gl.readPixels(0,0,8,1,gl.RGBA_INTEGER,gl.UNSIGNED_INT,out);
      return xs.map((x,i)=>({x, gpuBits:out[i*4], jsBits:(x>>>0), gpuH:out[i*4+1], jsH:Math.floor(h3(x,-3,7,12400)*16777216)}));
    }"""))
