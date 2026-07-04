/**
 * 生产启动:后台跑 + 随机端口
 *
 * 用法:
 *   npm run start:prod
 *
 * 与 npm start 的区别:
 *   - npm start       -> dev,固定 3000,前端 Vite 代理可直接对接
 *   - npm run start:prod -> 生产,随机端口,适合打包部署
 *
 * 日志写到 data/server.log,端口写到 data/port.txt
 */
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const LOG = path.join(ROOT, 'data', 'server.log');
fs.mkdirSync(path.dirname(LOG), { recursive: true });

const out = fs.openSync(LOG, 'a');
const child = spawn(process.execPath, [path.join(ROOT, 'src', 'app.js')], {
  cwd: ROOT,
  env: { ...process.env, RANDOM_PORT: '1' },
  stdio: ['ignore', out, out],
  detached: true,
  windowsHide: true,
});
child.unref();

// 等一会儿让服务把端口写出来
setTimeout(() => {
  let port = '(尚未写入)';
  try {
    port = fs.readFileSync(path.join(ROOT, 'data', 'port.txt'), 'utf-8').trim();
  } catch {}
  console.log(`server started (prod, random port), pid=${child.pid}, port=${port}, log=${LOG}`);
  console.log('停止: taskkill /F /PID ' + child.pid);
}, 1500);