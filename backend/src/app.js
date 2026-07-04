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
const path = require('path');
const fs = require('fs');
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

// 健康端点(根路径,留给监控/反代探活)
app.get('/health', (req, res) => {
  res.json({ ok: true, service: 'bilibili-cover', uptime: process.uptime() });
});

// API 路由挂 /api 前缀,前端 fetch('/api/?url=...') 直接对得上
// 不用 nginx/反代做 /api → / 改写,后端自己扛
app.use('/api', apiRouter);

// 静态托管前端 dist/(生产宝塔部署用)。
// dev 模式下 dist/ 不存在,跳过;dev 用 Vite 自带 dev server。
// 路径相对 backend/src/app.js:../../frontend/dist
const distDir = path.join(__dirname, '..', '..', 'frontend', 'dist');
if (fs.existsSync(distDir)) {
  app.use(
    express.static(distDir, {
      // 不强制 cache,宝塔反代一般会自己加 cache-control
      maxAge: 0,
    }),
  );
  // SPA fallback:任何 GET(非 /api / /health)都回 index.html。
  // 当前是 hash 路由,理论上不会触发,但留着兼容未来切 history 路由。
  app.get(/^(?!\/(?:api|health)(?:\/|$)).*/, (_req, res) => {
    res.sendFile(path.join(distDir, 'index.html'));
  });
} else {
  console.warn(
    `[static] frontend/dist 不存在(${distDir}),跳过静态托管。dev 模式正常,prod 部署请确认 dist/ 已构建。`,
  );
}

// 404 兜底(/api/* 没匹配上的也走这里,返回 JSON 而不是 index.html)
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
      console.log(`  网页:  http://127.0.0.1:${finalPort}/`);
      console.log(`  API:   http://127.0.0.1:${finalPort}/api/?url=BV1xx411c7xx`);
      console.log(`  健康:  http://127.0.0.1:${finalPort}/health`);
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