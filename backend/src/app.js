/**
 * B 站封面解析 API - Express 入口
 *
 * 端口策略:
 *   - dev: PORT 默认 3000(固定),方便前端 Vite 代理对接
 *   - prod: 用 PORT 或 RANDOM_PORT=1 启动,见 scripts/start-prod.js
 *
 * 启动:
 *   npm start              -> 固定 3000(dev)
 *   PORT=8888 npm start    -> 自定义端口
 *   npm run start:prod     -> 随机端口(生产打包后用)
 */

const express = require('express');
const cors = require('cors');
const { pickPort } = require('./utils/port');
const apiRouter = require('./routes/api');

const app = express();

app.use(cors());
app.use(express.json({ limit: '64kb' }));

// 简易请求日志,带耗时
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const ms = Date.now() - start;
    console.log(
      `[${new Date().toISOString()}] ${req.method} ${req.originalUrl} -> ${res.statusCode} (${ms}ms)`,
    );
  });
  next();
});

app.get('/health', (req, res) => {
  res.json({ ok: true, service: 'bilibili-cover', uptime: process.uptime() });
});

app.use('/', apiRouter);

// 404 兜底
app.use((req, res) => {
  res.status(404).json({ ok: false, code: 'NOT_FOUND', error: '路由不存在' });
});

// 错误兜底
app.use((err, req, res, _next) => {
  console.error('[unhandled]', err);
  res.status(500).json({ ok: false, code: 'INTERNAL', error: err.message || '服务器内部错误' });
});

function resolveDevPort() {
  // dev 默认固定 3000;PORT 环境变量可覆盖
  const env = process.env.PORT;
  if (env && /^\d+$/.test(env)) return Number(env);
  return 3000;
}

async function startServer({ random = false } = {}) {
  let port;
  if (random) {
    port = await pickPort({
      preferred: process.env.PORT,
      start: 3000,
      end: 3999,
      maxAttempts: 20,
    });
  } else {
    port = resolveDevPort();
  }

  const tryListen = (p, attemptsLeft) => {
    const server = app.listen(p, '0.0.0.0', () => {
      const finalPort = server.address().port;
      console.log(`[bilibili-cover] listening on http://127.0.0.1:${finalPort}`);
      console.log(`  试试:  http://127.0.0.1:${finalPort}/?url=BV1xx411c7xx`);
      // 把端口写到磁盘(供生产部署时前端/反代读)
      const fs = require('fs');
      const path = require('path');
      try {
        fs.writeFileSync(
          path.join(__dirname, '..', 'data', 'port.txt'),
          String(finalPort),
          'utf-8',
        );
      } catch (_) {
        /* 不影响主流程 */
      }
    });
    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE' && attemptsLeft > 0) {
        console.warn(`[startup] port ${p} 被抢占,换一个`);
        if (random) {
          pickPort({ start: 3000, end: 3999 })
            .then((np) => tryListen(np, attemptsLeft - 1))
            .catch((e) => {
              console.error('[startup] 重试失败:', e.message);
              process.exit(1);
            });
        } else {
          // 固定端口被占,直接退出 —— 让用户知道冲突了
          console.error(`[startup] port ${p} 已被占用。请检查是否已有进程在跑,或换 PORT=xxxx 启动。`);
          process.exit(1);
        }
      } else {
        console.error('[startup] listen error:', err);
        process.exit(1);
      }
    });
  };

  tryListen(port, random ? 10 : 0);
}

// 通过 RANDOM_PORT=1 启动就走随机模式,否则固定 3000
const useRandom = process.env.RANDOM_PORT === '1';
startServer({ random: useRandom });