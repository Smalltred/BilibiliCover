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

// 代理下载 —— 解决 B 站 Referer 防盗链(403)
//
// 浏览器直接 <a href="cover.jpg" download> 时,Referer 是当前页(localhost/你的域名),
// B 站图片服务器会拒绝。走后端代理可带正确的 Referer: bilibili.com。
//
// GET /download?url=https://i0.hdslb.com/.../cover.jpg&filename=xxx.jpg
//   -> 二进制流(Content-Disposition: attachment)
router.get('/download', async (req, res) => {
  const url = (req.query.url || '').toString();
  const filename = (req.query.filename || 'cover.jpg').toString();

  if (!url) {
    return res.status(400).json({ ok: false, error: '缺少 url 参数' });
  }

  // 白名单:只允许 B 站域名(防滥用)
  let parsedUrl;
  try {
    parsedUrl = new URL(url);
  } catch {
    return res.status(400).json({ ok: false, error: 'url 不合法' });
  }
  if (!/(^|\.)(bilibili\.com|hdslb\.com)$/i.test(parsedUrl.hostname)) {
    return res.status(400).json({ ok: false, error: '只支持 B 站域名' });
  }

  try {
    const upstream = await fetch(url, {
      headers: {
        Referer: 'https://www.bilibili.com',
        'User-Agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
          '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
      },
      redirect: 'follow',
    });
    if (!upstream.ok) {
      return res.status(502).json({
        ok: false,
        error: `上游返回 ${upstream.status}`,
      });
    }

    const contentType = upstream.headers.get('content-type') || 'image/jpeg';
    res.set('Content-Type', contentType);
    res.set('Content-Disposition', `attachment; filename="${filename}"`);
    const contentLength = upstream.headers.get('content-length');
    if (contentLength) res.set('Content-Length', contentLength);

    // 流式转发(避免大图占内存)
    const { Readable } = require('stream');
    Readable.fromWeb(upstream.body).pipe(res);
  } catch (e) {
    res.status(500).json({ ok: false, error: `下载失败: ${e.message}` });
  }
});

module.exports = router;