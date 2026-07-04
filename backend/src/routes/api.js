/**
 * 封面解析 API 路由
 *
 * GET /  ?url=BV1xx411c7xx  或  ?url=https://www.bilibili.com/video/BV1xx...
 * GET /resolve?url=...
 *
 * 返回结构:
 *   成功: { ok: true, input, type, rawType, data: {...} }
 *   失败: { ok: false, error, code }
 */

const express = require('express');
const bilibili = require('../services/bilibili');
const { TTLCache } = require('../utils/cache');

const router = express.Router();

const cache = new TTLCache({ defaultTtlMs: 5 * 60 * 1000, maxEntries: 5000 });

function cacheKey(url) {
  return 'bili:' + String(url || '').trim().toLowerCase();
}

async function handle(req, res) {
  const url = (req.query.url || req.query.id || req.query.q || '').toString();
  if (!url) {
    return res.status(400).json({
      ok: false,
      code: 'MISSING_PARAM',
      error: '缺少 url 参数,例如 ?url=BV1xx411c7xx 或 ?url=https://www.bilibili.com/video/BV1xx...',
    });
  }

  const key = cacheKey(url);
  const cached = cache.get(key);
  if (cached) {
    return res.json({ ...cached, _cached: true });
  }

  const result = await bilibili.resolve(url);
  if (result.ok) {
    cache.set(key, result);
  }
  // 失败结果也短暂缓存,避免某个无效 ID 被刷爆 B 站 API
  else if (result.code === 'PARSE_FAILED') {
    // 不缓存 —— 用户可能是手抖打错了
  } else {
    cache.set(key, result, 30 * 1000);
  }
  res.json(result);
}

router.get('/', handle);
router.get('/resolve', handle);

// 诊断端点:不调 B 站 API,只看输入被识别成什么,用于排查
router.get('/diag', (req, res) => {
  const url = (req.query.url || req.query.id || req.query.q || '').toString();
  if (!url) {
    return res.status(400).json({ ok: false, error: '缺少 url 参数' });
  }
  const parsed = bilibili.parseId(url);
  res.json({
    ok: true,
    input: url,
    parsed: parsed || null,
    isShortUrl: /^https?:\/\/(b23\.tv|bili2233\.cn)\//i.test(url.trim()),
  });
});

module.exports = router;