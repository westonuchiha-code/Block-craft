from playwright.sync_api import sync_playwright
import json, sys
# The calendar: eight months of twelve days; holidays are announced at dawn, written in the journal, and change real prices for the day.
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/blockcraft_prototype.html'
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':960,'height':540}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(1500)
    pg.fill('#newName','cal'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const o={};
      o.d0=dateStr(0); o.d3=dateStr(3); o.d11=dateStr(11); o.d12=dateStr(12); o.d71=dateStr(71); o.d72=dateStr(72); o.d95=dateStr(95+72);
      o.ord=[1,2,3,4,11,12].map(ordinal).join(' ');
      const seen=new Set(); let n=0; for(let d=0;d<YEAR_DAYS;d++){ const h=holidayOn(d); if(h){ n++; seen.add(h.name); } } o.perYear=n; o.distinct=seen.size; o.again=holidayOn(3)===holidayOn(3+YEAR_DAYS);
      dayNo=0; o.none=holiday(); o.next=nextHoliday().days; talkNpc=null;
      const base={ buy:buyPrice(IRON_PICK), train:trainCost('mining','miner'), room:roomCost(), crop:sellPrice(CROPS_SOLD.slice().sort((a,b)=>PRICE[b]-PRICE[a])[0]), stone:sellPrice(COBBLE) };
      dayNo=2; const j0=journal.length; questDawn(); o.fair={ name:holiday().name, buy:buyPrice(IRON_PICK), base:base.buy, toast:!!document.body.innerText.match(/MERCHANTS' FAIR/), j:journal.slice(j0).map(e=>e.t)[0] };
      const at=(doy)=>{ dayNo=doy-DAY0; if(dayNo<0) dayNo+=YEAR_DAYS; return holiday(); };
      at(56); o.train=[trainCost('mining','miner'), base.train];
      at(66); o.harvest=[roomCost(), sellPrice(CROPS_SOLD.slice().sort((a,b)=>PRICE[b]-PRICE[a])[0]), base.crop, sellPrice(COBBLE), base.stone];
      at(93); bounty={}; crime([0,0],'assault'); o.fine=[fineOf([0,0]), bountyOf([0,0])]; bounty={};
      at(83); o.spell=holidayMul('spell'); at(41); o.heal=holidayMul('heal'); at(7); o.wagon=holidayMul('wagon');
      dayNo=3; o.sheet=journalSheet().includes('4th of Greening, year 1') && journalSheet().includes("Merchants' Fair");
      dayNo=1; const v=villageAt(0,0); o.news=talkNews({ x:v.cx, z:v.cz, village:[0,0], vc:[v.cx,v.cz], name:'T', job:'farmer' }).includes("Merchants' Fair is in 2 days");
      return o; }""")
    print(json.dumps(r)); print(errs)
    if not (r['d0']=='1st of Greening, year 1' and r['d3']=='4th of Greening, year 1' and r['d11']=='12th of Greening, year 1' and r['d12']=='1st of Highsun, year 1'
            and r['d71']=='12th of Deepwinter, year 1' and r['d72']=='1st of Frostwane, year 2' and r['ord']=='1st 2nd 3rd 4th 11th 12th'): bad.append('dates')
    if not (r['perYear']==8 and r['distinct']==8 and r['again'] and r['none'] is None and r['next']==3): bad.append('holiday table')
    f=r['fair']
    if not (f['name']=="the Merchants' Fair" and f['buy']<f['base'] and abs(f['buy']-0.75*f['base'])<=1 and f['toast'] and f['j'].startswith("Today is the Merchants' Fair")): bad.append('the fair')
    if not (abs(r['train'][0]-0.5*r['train'][1])<=1): bad.append('warriors day')
    h=r['harvest']
    if not (h[0]==0 and h[1]>h[2] and h[3]==h[4]): bad.append('harvest home')
    if not (r['fine'][0]*2==r['fine'][1] and r['spell']==0.5 and r['heal']==0 and r['wagon']==0.5): bad.append('other holidays')
    if not (r['sheet'] and r['news']): bad.append('journal and talk')
    b.close()
print('CALENDAR TEST FAILED', bad) if bad else print('calendar ok')
sys.exit(1 if (bad or errs) else 0)
