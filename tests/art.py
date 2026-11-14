from playwright.sync_api import sync_playwright
import json, sys
# Artifacts: the four named things of power, what each adds to a blow, and that most delve shrines hold one.
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1100,'height':560}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(1500)
    pg.fill('#newName','art'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(4000)
    r=pg.evaluate("""()=>{ beastSpawnT=1e9; ogreSpawnT=1e9; const o={};
      o.names=ARTIFACT_IDS.map(id=>NAMES[id]+':'+TOOLS[id].kind+':t'+TOOLS[id].tier+':'+PRICE[id]);
      const cat=newCat(Math.floor(player.x)+2, Math.floor(player.y), Math.floor(player.z)); cat.hp=1e6; mobs.push(cat);
      const dmg=(id)=>{ inv[id]=1; HOTBAR[sel]=id; return +(playerAttackDamage()+artifactHit(cat)).toFixed(2); };
      o.mith=dmg(MITH_SWORD); o.ember=dmg(EMBERBRAND); o.storm=dmg(STORMCALLER);
      health=10; o.drain=dmg(LIFEDRINKER); o.healed=health; o.pickTier=TOOLS[DEEPDELVER].tier; o.canMine=canHarvest(ADAM_ORE, DEEPDELVER);
      o.sprites=new Set(ARTIFACT_IDS.map(id=>JSON.stringify(toolSprite(id).filter(Boolean).slice(0,6)))).size;
      const L=delveNear(player.x,player.z,2600); let with_=0; const kinds=new Set();
      for(const P of L){ const c=P.nodes[P.heart].chests[0], it=chestItems(c[0],c[1],c[2]); const a=ARTIFACT_IDS.find(id=>it[id]); if(a){ with_++; kinds.add(a); } const c1=P.nodes[P.heart].chests[1]; if(ARTIFACT_IDS.some(id=>chestItems(c1[0],c1[1],c1[2])[id])) o.second=true; }
      o.delves=L.length; o.withArtifact=with_; o.kinds=kinds.size; return o; }""")
    print(json.dumps(r)); print(errs)
    ok=(len(r['names'])==4 and r['ember']==r['mith']+3 and r['storm']==r['mith']+4 and r['drain']==r['mith']+1 and r['healed']==11 and r['pickTier']==5 and r['canMine'] and r['sprites']==4
        and r['delves']>=8 and 0.4*r['delves']<=r['withArtifact']<=0.95*r['delves'] and r['kinds']>=3 and not r.get('second'))
    if not ok: bad.append('artifacts')
    b.close()
print('ARTIFACT TEST FAILED', bad) if bad else print('artifacts ok')
sys.exit(1 if (bad or errs) else 0)
