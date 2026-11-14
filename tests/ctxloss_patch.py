p='/home/claude/blockcraft_prototype.html'; s=open(p).read()
def rep(a,b,n=1):
    global s; assert s.count(a)==n, (s.count(a), a[:90]); s=s.replace(a,b)
rep("    GPU.gl = gl; GPU.cv = cv; GPU.pr = pr; GPU.U = {};",
"""    GPU.gl = gl; GPU.cv = cv; GPU.pr = pr; GPU.U = {};
    if(!GPU.lossHooked){                                     // the graphics card can drop the context (app sent to the background, driver reset):
      GPU.lossHooked = true;                                 // the CPU renderer takes over at once, and the GPU comes back when the context does
      cv.addEventListener('webglcontextlost', e=>{ e.preventDefault(); const was = GPU.on; GPU.on = false; GPU.ok = false; GPU.made = false; GPU.lost = was;
        document.body.classList.remove('gpu'); if(wkWanted){ WK.fail = false; wkStart(); } });
      cv.addEventListener('webglcontextrestored', ()=>{ GPU.texSeed = null; GPU.models = new Map(); GPU.mdlN = 0; GPU.skinN = 0; GPU.grassSet = false;
        if(GPU.lost){ GPU.lost = false; gpuSet(true); } });
    }""")
open(p,'w').write(s); print('patched')
