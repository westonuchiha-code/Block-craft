import sys
s=open('/home/claude/blockcraft_prototype.html').read()
views=sys.argv[2]
t='''<script>
document.getElementById('newName').value='vw'; document.getElementById('newBtn').click();
function put(x,z,yaw,pitch,dy){ player.x=x+0.5; player.z=z+0.5; player.yaw=yaw; player.pitch=pitch;
  let y=H-1; for(;y>0;y--){ const b=getB(x,y,z); if(b!==AIR && b!==WATER) break; } player.y=y+1+(dy||0); }
function shot(){ const c=document.createElement('canvas'); c.width=448; c.height=280; const g=c.getContext('2d'); g.imageSmoothingEnabled=false; render(); g.drawImage(document.getElementById('c'),0,0,448,280); return c; }
function find(fn,R,st){ for(let r=0;r<=R;r+=st) for(let a=0;a<6.283;a+=Math.max(0.05,st/Math.max(r,1))){ const x=Math.round(Math.cos(a)*r), z=Math.round(Math.sin(a)*r); const res=fn(x,z); if(res) return res; } return null; }
const out=document.createElement('div'); out.style.cssText='position:fixed;left:0;top:0;z-index:999999;background:#222;width:1350px;display:flex;flex-wrap:wrap;gap:2px';
function add(label,c){ const d=document.createElement('div'); d.style.cssText='position:relative'; d.appendChild(c); const l=document.createElement('div'); l.textContent=label; l.style.cssText='position:absolute;left:4px;bottom:4px;color:#ff0;font:12px monospace;background:#0008;padding:1px 4px'; d.appendChild(l); out.appendChild(d); }
setTimeout(()=>{ try{
'''+views+'''
}catch(e){ out.textContent='ERR '+e+' '+(e.stack||'').slice(0,300); }
document.body.appendChild(out); },300);
</script>'''
open(sys.argv[1],'w').write(s.replace('</body>',t+'</body>'))
