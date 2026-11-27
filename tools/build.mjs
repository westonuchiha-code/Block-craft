// Builds the game into ONE self-contained HTML file, so it runs by double-clicking, from a launcher, or in the desktop app.
//
//   src/index.html        the page skeleton (with two markers, below)
//   src/ui/style.css      every style the page uses           -> replaces <!--STYLE-->
//   src/main.js           the game, with all its imports       -> replaces <!--SCRIPT-->
//   src/world/worker.js   the world-generation worker, bundled on its own and handed to the game as a string
//
// Output: dist/blockcraft.html (scratch) and next/blockcraft.html (the copy that is committed, for playing).
//   node tools/build.mjs           build once
//   node tools/build.mjs --watch   rebuild whenever a file in src/ changes
import * as esbuild from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const src = p => path.join(root, 'src', p);

async function bundle(entry, extra = {}) {
  const out = await esbuild.build({
    entryPoints: [entry], bundle: true, write: false, format: 'iife', target: 'es2022',
    minify: true, legalComments: 'none', logLevel: 'warning', ...extra,
  });
  return out.outputFiles[0].text;
}

async function buildOnce() {
  const t0 = Date.now();
  const worker = await bundle(src('world/worker.js'));
  const game = await bundle(src('main.js'), { define: { __WORKER_SOURCE__: JSON.stringify(worker) } });
  const css = fs.readFileSync(src('ui/style.css'), 'utf8');
  let html = fs.readFileSync(src('index.html'), 'utf8');
  // (a function, not a string, as the replacement: the code contains "$&" and similar sequences that replace() would expand)
  html = html.replace('<!--STYLE-->', () => `<style>\n${css}\n</style>`);
  html = html.replace('<!--SCRIPT-->', () => `<script>\n${game.replace(/<\/script/gi, '<\\/script')}\n</script>`);
  for (const dir of ['dist', 'next']) {
    fs.mkdirSync(path.join(root, dir), { recursive: true });
    fs.writeFileSync(path.join(root, dir, 'blockcraft.html'), html);
  }
  console.log(`built next/blockcraft.html: ${(html.length / 1024).toFixed(0)} KB in ${Date.now() - t0} ms`);
}

await buildOnce();
if (process.argv.includes('--watch')) {
  let timer = null;
  fs.watch(path.join(root, 'src'), { recursive: true }, () => {
    clearTimeout(timer);
    timer = setTimeout(() => buildOnce().catch(e => console.error(e.message)), 150);
  });
  console.log('watching src/ for changes...');
}
