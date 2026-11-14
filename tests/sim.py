import re,subprocess
s=open('/home/claude/blockcraft_prototype.html').read()
a=s.index('function h3'); b=s.index('// ---------- pure world')
base=s[a:b]
