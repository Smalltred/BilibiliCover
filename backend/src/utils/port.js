/**
 * 找一个可用的 TCP 端口。
 *
 * 策略:
 *   1. 优先用环境变量 PORT(允许覆盖)
 *   2. 否则在 [start, end] 范围内随机选,最多重试 maxAttempts 次
 *   3. 全部失败抛出
 *
 * 注意: 选出来的端口到真正 listen 之间存在 race condition(可能被其他进程抢占),
 * 调用方应该把 .listen() 失败的处理一并接住 —— 见 app.js 的 startServer()。
 */

const net = require('net');

function isPortFree(port) {
  return new Promise((resolve) => {
    const tester = net
      .createServer()
      .once('error', (err) => {
        if (err.code === 'EADDRINUSE') resolve(false);
        else resolve(false);
      })
      .once('listening', () => {
        tester.close(() => resolve(true));
      })
      .listen(port, '0.0.0.0');
  });
}

async function pickPort({
  start = 3000,
  end = 3999,
  maxAttempts = 20,
  preferred,
} = {}) {
  if (preferred !== undefined && preferred !== null && preferred !== '') {
    const port = Number(preferred);
    if (Number.isInteger(port) && port > 0 && port < 65536) {
      if (await isPortFree(port)) return port;
      throw new Error(`PORT=${port} 已被占用`);
    }
  }

  // 在范围内随机选,避免每次都从 start 开始
  const range = end - start + 1;
  const tried = new Set();

  for (let i = 0; i < maxAttempts; i++) {
    const port = start + Math.floor(Math.random() * range);
    if (tried.has(port)) continue;
    tried.add(port);
    if (await isPortFree(port)) return port;
  }
  throw new Error(`在 ${start}-${end} 范围内 ${maxAttempts} 次都没找到可用端口`);
}

module.exports = { pickPort, isPortFree };