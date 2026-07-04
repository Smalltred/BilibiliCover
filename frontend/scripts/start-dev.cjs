// 后台启动前端 Vite dev server
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const LOG = path.join(ROOT, 'vite.log');
fs.mkdirSync(path.dirname(LOG), { recursive: true });

const out = fs.openSync(LOG, 'a');
const child = spawn('cmd', ['/c', 'npm', 'run', 'dev'], {
  cwd: ROOT,
  stdio: ['ignore', out, out],
  detached: true,
  windowsHide: true,
});
child.unref();

console.log(`vite started, pid=${child.pid}, log=${LOG}`);
console.log('停止: taskkill /F /PID ' + child.pid);