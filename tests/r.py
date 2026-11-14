import sys
src=open('/home/claude/blockcraft_prototype.html').read()
a=src.index("// ---------- tool sprites"); b=src.index("function drawHand(){")
html=f"""<html><body style='margin:0;background:#000'><canvas id=v width=1080 height=340></canvas><script>
const WOOD_PICK=16, STONE_PICK=20, STICK=15, RW=224, RH=140;
function shadeRGB(c,m){{ return `rgb(${{Math.min(255,c[0]*m)|0}},${{Math.min(255,c[1]*m)|0}},${{Math.min(255,c[2]*m)|0}})`; }}
{src[a:b]}
function frame(id,p){{ const c=document.createElement('canvas'); c.width=RW; c.height=RH; const g=c.getContext('2d');
 g.fillStyle='#8aa8c8'; g.fillRect(0,0,RW,RH); g.fillStyle='#c8b060'; g.fillRect(0,80,RW,60); drawHeldTool(g,id,1,p); return c; }}
const v=document.getElementById('v').getContext('2d'); v.imageSmoothingEnabled=false;
v.drawImage(frame(16,0),0,0,540,337); v.drawImage(frame(20,0.7),540,0,540,337);
</script></body></html>"""
open('/tmp/fp.html','w').write(html)
