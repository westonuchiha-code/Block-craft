from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    r=pg.evaluate("""()=>{ const rows={}; const T=[['hand',0],['wood',null],['stone',null],['iron(3)',3],['top(4)',4]];
      const tools={pick:[WOOD_PICK,STONE_PICK],axe:[WOOD_AXE,STONE_AXE],shovel:[WOOD_SHOVEL,STONE_SHOVEL]};
      const fake=(kind,tier)=>{ const id=9000+tier*10+['pick','axe','shovel'].indexOf(kind); TOOLS[id]={kind,tier,speed:1,dur:9}; return id; };
      for(const [nm,b,kind] of [['dirt',DIRT,'shovel'],['grass',GRASS,'shovel'],['sand',SAND,'shovel'],['log',LOG,'axe'],['planks',PLANKS,'axe'],['stone',STONE,'pick'],['cobble',COBBLE,'pick'],['coal',COAL,'pick'],['leaves',LEAVES,'sword'],['glass',GLASS,null],['tall grass',TALL_GRASS,null]]){
        const k=kind||'pick'; rows[nm]=[hitsNeeded(b,0), kind&&kind!=='sword'?hitsNeeded(b,tools[k][0]):'-', kind&&kind!=='sword'?hitsNeeded(b,tools[k][1]):'-', kind&&kind!=='sword'?hitsNeeded(b,fake(k,3)):'-', kind&&kind!=='sword'?hitsNeeded(b,fake(k,4)):'-'];
      }
      skills.mining=100; rows['stone, top pick, Mining 100']=hitsNeeded(STONE,fake('pick',4)); return rows; }""")
    for k,v in r.items(): print(k, v)
    print(errs); b.close()
