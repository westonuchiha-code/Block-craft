from playwright.sync_api import sync_playwright
import time
errs=[]; fails=[]
def chk(name,ok,info=''):
    print(('PASS ' if ok else 'FAIL ')+name+' '+str(info))
    if not ok: fails.append(name)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/blockcraft_prototype.html'); pg.wait_for_timeout(2000)
    pg.fill('#newName','t'); pg.fill('#newSeed','12345'); pg.click('#newBtn'); pg.wait_for_timeout(3000)
    stage="""([px,pz,floor])=>{
      mobs.length=0; tod=0.25;
      if(window.BASEY===undefined) window.BASEY=Math.floor(player.y)+10;
      const by=window.BASEY;
      for(let x=px-12;x<px+12;x++)for(let z=pz-12;z<pz+12;z++)for(let y=by-2;y<by+6;y++)setB(x,y,z,AIR);
      if(floor){for(let x=px-3;x<px+3;x++)for(let z=pz-40;z<pz+3;z++)setB(x,by,z,STONE_BRICK);}
      else {for(let x=px-2;x<=px+2;x++)for(let z=pz-2;z<=pz+2;z++)setB(x,by,z,STONE_BRICK);}
      player.x=px+0.5;player.z=floor?pz+0.5:pz+0.5;player.y=by+1;player.yaw=0;player.vy=0;
      return by;}"""
    def run(sneak,floor,secs):
        by=pg.evaluate(stage,[1000 if not floor else 1000,1000,floor])
        pg.wait_for_timeout(600)
        pg.evaluate("s=>{ if(sneaking!==s) toggleSneak(); }",sneak)
        x0,z0=pg.evaluate("[player.x,player.z]")
        pg.keyboard.down('w'); pg.wait_for_timeout(int(secs*1000)); pg.keyboard.up('w')
        r=pg.evaluate("({x:player.x,y:player.y,z:player.z})")
        pg.evaluate("if(sneaking) toggleSneak()")
        return by,x0,z0,r
    by,x0,z0,r=run(False,False,4)
    chk('a walks off',r['y']<by+1-0.5,r)
    by,x0,z0,r=run(True,False,4)
    chk('b stays on platform',abs(r['y']-(by+1))<0.01 and 1000-2<=r['x']<=1000+3.31 and 1000-2-0.31<=r['z']<=1000+3,r)
    chk('b stopped at edge',r['z']<1000-2+0.31+0.01 ,r)
    _,x0,z0,rw=run(False,True,2); dw=abs(rw['z']-z0)
    _,x0,z0,rs=run(True,True,2); ds=abs(rs['z']-z0)
    chk('c speed ratio',0.2<=ds/dw<=0.4,(dw,ds,ds/dw))
    pg.evaluate("running=false;sneaking=false;stick.classList.remove('run')")
    pg.evaluate("toggleRun();toggleSneak()")
    chk('d1 sneak turns run off',pg.evaluate("running===false&&sneaking===true"))
    pg.evaluate("toggleRun()")
    chk('d2 run turns sneak off',pg.evaluate("running===true&&sneaking===false"))
    pg.evaluate("toggleRun()")
    pg.evaluate("toggleSneak()")
    chk('cue class',pg.evaluate("document.getElementById('rstick').classList.contains('sneak')"))
    pg.keyboard.press('z') if False else pg.evaluate("dispatchEvent(new KeyboardEvent('keydown',{code:'KeyZ'}))")
    chk('KeyZ toggles',pg.evaluate("sneaking===false && !document.getElementById('rstick').classList.contains('sneak')"))
    # tap on right stick
    box=pg.eval_on_selector('#rstick','e=>{const r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2,r.width]}')
    pg.evaluate("document.getElementById('rstick').getBoundingClientRect=()=>({left:100,top:100,width:100,height:100})")
    box=[150,150,50]
    pg.evaluate("""()=>{const e=document.getElementById('rstick');const o={pointerId:7,pointerType:'touch',clientX:%f,clientY:%f,bubbles:true};
      e.setPointerCapture=()=>{};e.dispatchEvent(new PointerEvent('pointerdown',o));e.dispatchEvent(new PointerEvent('pointerup',o));}"""%(box[0],box[1]))
    chk('tap toggles',pg.evaluate("sneaking===true"))
    pg.evaluate("""()=>{const e=document.getElementById('rstick');const o={pointerId:8,pointerType:'touch',clientX:%f,clientY:%f,bubbles:true};
      const o2=Object.assign({},o,{clientX:%f});
      e.dispatchEvent(new PointerEvent('pointerdown',o));e.dispatchEvent(new PointerEvent('pointermove',o2));e.dispatchEvent(new PointerEvent('pointerup',o2));}"""%(box[0],box[1],box[0]+box[2]*0.4))
    chk('drag does not toggle',pg.evaluate("sneaking===true"))
    pg.evaluate("toggleSneak()")
    chk('e no page errors',not errs,errs)
    b.close()
print('ALL PASS' if not fails else 'FAILED: '+str(fails))
