src=open('/home/claude/blockcraft_prototype.html').read()
a=src.index("// ---------- tool sprites"); b=src.index("function drawHand(){")
html=f"""<html><body style='margin:0;background:#000'><canvas id=v width=1600 height=800></canvas><script>
const WOOD_PICK=16, STONE_PICK=20, STICK=15, RW=224, RH=140;
function shadeRGB(c,m){{ return `rgb(${{Math.min(255,c[0]*m)|0}},${{Math.min(255,c[1]*m)|0}},${{Math.min(255,c[2]*m)|0}})`; }}
{src[a:b]}
function frame(id,p){{ const c=document.createElement('canvas'); c.width=RW; c.height=RH; const g=c.getContext('2d');
 g.fillStyle='#8aa8c8'; g.fillRect(0,0,RW,RH); g.fillStyle='#7a9a52'; g.fillRect(0,90,RW,50); drawHeldTool(g,id,1,0,p); return c; }}
const v=document.getElementById('v').getContext('2d'); v.imageSmoothingEnabled=false;
[16,17,18,19].forEach((id,c)=>[0,0.55].forEach((p,r)=>v.drawImage(frame(id,p),100,40,124,100,c*400,r*400,400,400)));
</script></body></html>"""
open('/tmp/held.html','w').write(html)
