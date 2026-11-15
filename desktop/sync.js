// copies the one-file game into the desktop app (run automatically by "npm start" and the dist scripts)
const fs = require('fs'), path = require('path');
const src = path.join(__dirname, '..', 'game', 'blockcraft.html'), dir = path.join(__dirname, 'game');
fs.mkdirSync(dir, { recursive: true });
fs.copyFileSync(src, path.join(dir, 'blockcraft.html'));
console.log('game copied: ' + fs.statSync(src).size + ' bytes');
