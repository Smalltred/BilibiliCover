// 启动后端服务,日志写到 data/server.log
// 用法: node scripts/start.js
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const LOG = path.join(ROOT, 'data', 'server.log');
fs.mkdirSync(path.dirname(LOG), { recursive: true });

const out = fs.openSync(LOG, 'a');
const child = spawn(process.execPath, [path.join(ROOT, 'src', 'app.js')], {
  cwd: ROOT,
  stdio: ['ignore', out, out],
  detached: true,
  windowsHide: true,
});
child.unref();

console.log(`server started, pid=${child.pid}, log=${LOG}`);
console.log('停止: taskkill /F /PID ' + child.pid);