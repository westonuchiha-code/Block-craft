import sys, os
from PIL import Image, ImageDraw
d='/home/claude/screenshots'; files=sorted(f for f in os.listdir(d) if f.endswith('.png'))
lo,hi,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
sel=[f for f in files if lo<=int(f[:2])<=hi]
W,Hh=550,280; cols=2; rows=(len(sel)+1)//2
sheet=Image.new('RGB',(W*cols,(Hh+18)*rows),(20,20,20)); g=ImageDraw.Draw(sheet)
for i,f in enumerate(sel):
    im=Image.open(os.path.join(d,f)).convert('RGB'); im.thumbnail((W,Hh))
    x=(i%cols)*W; y=(i//cols)*(Hh+18); sheet.paste(im,(x,y+18)); g.text((x+4,y+3),f,fill=(255,255,0))
sheet.save(out)
