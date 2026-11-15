// Blockcraft desktop shell (Electron). The game is the single file game/blockcraft.html; this only gives it a window.
//   - starts full screen, no menu bar; F11 or Alt+Enter toggles full screen; the game's own MENU has everything else
//   - saves live in the app's own profile folder (localStorage), so they survive updates of the game file
//   - the GPU renderer is used whenever the machine has real graphics hardware (the game decides)
//   - "--selftest" starts a world, checks the game runs and saves, writes a screenshot, prints a report and quits
const { app, BrowserWindow, Menu } = require('electron');
const path = require('path'), fs = require('fs');
const SELFTEST = process.argv.includes('--selftest');

app.commandLine.appendSwitch('ignore-gpu-blocklist');                  // old drivers still get the GPU renderer
app.commandLine.appendSwitch('disable-renderer-backgrounding');         // keep running at full speed when not focused
app.commandLine.appendSwitch('autoplay-policy', 'no-user-gesture-required');
if(!app.requestSingleInstanceLock()){ app.quit(); }

let win = null;
function createWindow(){
  win = new BrowserWindow({
    width: 1600, height: 900, minWidth: 960, minHeight: 540,
    fullscreen: !SELFTEST, show: true, backgroundColor: '#000000', title: 'Blockcraft', autoHideMenuBar: true,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: false, backgroundThrottling: false, spellcheck: false }
  });
  Menu.setApplicationMenu(null);
  win.loadFile(path.join(__dirname, 'game', 'blockcraft.html'));
  win.webContents.on('before-input-event', (e, input)=>{
    if(input.type!=='keyDown') return;
    if(input.key==='F11' || (input.key==='Enter' && input.alt)){ win.setFullScreen(!win.isFullScreen()); e.preventDefault(); }
  });
  win.webContents.setWindowOpenHandler(()=>({ action:'deny' }));         // the game never opens other windows
  win.on('closed', ()=>{ win = null; });
  if(SELFTEST) selftest();
}
app.on('second-instance', ()=>{ if(win){ if(win.isMinimized()) win.restore(); win.focus(); } });
app.on('window-all-closed', ()=>app.quit());
app.whenReady().then(createWindow);

async function selftest(){
  const errs = []; const wc = win.webContents;
  wc.on('console-message', (e, level, msg)=>{ if(level>=3) errs.push(String(msg).slice(0,200)); });
  const out = { ok:false };
  try{
    await new Promise(r=>wc.once('did-finish-load', r));
    const run = js=>wc.executeJavaScript(js, true);
    const sleep = ms=>new Promise(r=>setTimeout(r, ms));
    await sleep(1500);
    await run(`document.getElementById('newName').value='selftest'; document.getElementById('newSeed').value='12345'; document.getElementById('newBtn').click(); 1`);
    await sleep(5000);
    const a = await run(`({ gen:worldGen, sea:SEA, gpu:GPU.on, gpuErr:GPU.err||null, frames:(GPU.on ? GPU.frames : (WK.frames||0)), workers:WK.on, y:Math.round(player.y), village:!!nearestVillage(2), size:[innerWidth,innerHeight] })`);
    await sleep(2000);
    const b = await run(`({ frames:(GPU.on ? GPU.frames : (WK.frames||0)) })`);
    await run(`saveWorld(); 1`);
    const saved = await run(`Object.keys(localStorage).filter(k=>k.startsWith('bc.w.')).length`);
    const img = await wc.capturePage(); const shot = path.join(app.getPath('temp'), 'blockcraft_selftest.png'); fs.writeFileSync(shot, img.toPNG());
    Object.assign(out, a, { framesIn2s:b.frames-a.frames, savedKeys:saved, screenshot:shot, errors:errs, userData:app.getPath('userData'), electron:process.versions.electron, chrome:process.versions.chrome });
    out.ok = a.gen>=6 && out.framesIn2s>0 && saved>0 && !errs.length;
  }catch(e){ out.error = String(e); }
  console.log('SELFTEST ' + JSON.stringify(out));
  app.exit(out.ok ? 0 : 1);
}
