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
  // 允许 bilibili.com / hdslb.com / *.bilibili.com / *.hdslb.com
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
    // HTTP header 只允许 ASCII,中文/特殊字符走 RFC 5987
    // 现代浏览器读 filename*=UTF-8''xxx,老 IE 读 ASCII 兜底
    res.set('Content-Disposition', buildContentDisposition(filename));
    const contentLength = upstream.headers.get('content-length');
    if (contentLength) res.set('Content-Length', contentLength);

    // 流式转发(避免大图占内存)+ 监听流错误
    const { Readable } = require('stream');
    const nodeStream = Readable.fromWeb(upstream.body);
    nodeStream.on('error', (err) => {
      console.error('[download] upstream stream error:', err.message);
      // header 已发,只能断流;浏览器会自动处理半截响应
      res.destroy(err);
    });
    res.on('close', () => nodeStream.destroy());
    nodeStream.pipe(res);
  } catch (e) {
    console.error('[download] error:', e.message);
    res.status(500).json({ ok: false, error: `下载失败: ${e.message}` });
  }
});

/**
 * 构造 Content-Disposition 头。
 * HTTP header 只允许 ASCII,中文/特殊字符必须按 RFC 5987 用 UTF-8 + percent-encoding。
 * 同时给个 ASCII 兜底 filename(把非法字符替成 _),照顾老 IE/部分下载管理器。
 */
function buildContentDisposition(filename) {
  const safe = (filename || 'cover.jpg').toString();
  // 兜底:去掉控制字符、引号、反斜杠,非 ASCII 替成 _(兼容老客户端)
  const asciiFallback = safe
    .replace(/[\x00-\x1F\x7F"\\]/g, '_')
    .replace(/[^\x20-\x7E]/g, '_');
  // RFC 5987:UTF-8 percent-encode 后用 filename*=UTF-8''... 给出真实名字
  const utf8Encoded = encodeURIComponent(safe)
    .replace(/['()*]/g, (c) => '%' + c.charCodeAt(0).toString(16).toUpperCase());
  return `attachment; filename="${asciiFallback}"; filename*=UTF-8''${utf8Encoded}`;
}

module.exports = router;