/**
 * B 站视频/番剧封面解析服务
 *
 * 支持 5 种 ID:
 *   - BV  普通视频(BV1xxx...)
 *   - AV  普通视频(av12345, 老格式)
 *   - EP  番剧集(ep12345)
 *   - SS  番剧季(ss12345)
 *   - MD  番剧条目(md12345)
 *
 * 入参:
 *   - 可以直接传 ID: "BV1xx", "av12345", "ep12345"
 *   - 也可以传完整 URL,会先抽 ID
 *
 * 不需要自己做 BV↔AV 转换 —— B 站 view 接口直接支持 bvid 和 aid 两个参数。
 * 老 Flask 仓库就是被自己的旧 BV 算法坑了。
 */

const BILI_API_HEADERS = {
  'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  Referer: 'https://www.bilibili.com',
};

// 精确匹配 —— 跟老 Flask 仓库那个 BV.*?.{10} 不同,这里限定长度和字符集
const ID_PATTERNS = [
  { type: 'BV', regex: /BV([a-zA-Z0-9]{10})/i },
  { type: 'AV', regex: /[aA][vV](\d{1,12})/ },
  { type: 'EP', regex: /[eE][pP](\d{1,12})/ },
  { type: 'SS', regex: /[sS][sS](\d{1,12})/ },
  { type: 'MD', regex: /[mM][dD](\d{1,12})/ },
];

// 路径感知正则 —— 优先匹配 B 站标准 URL 路径里的 ID,避免误吃文本里的杂字符
const PATH_PATTERNS = [
  { type: 'BV', regex: /\/video\/(BV[a-zA-Z0-9]{10})/i },
  { type: 'AV', regex: /\/video\/[aA][vV](\d{1,12})/ },
  { type: 'EP', regex: /\/bangumi\/play\/[eE][pP](\d{1,12})/ },
  { type: 'SS', regex: /\/bangumi\/play\/[sS][sS](\d{1,12})/ },
  { type: 'MD', regex: /\/bangumi\/media\/[mM][dD](\d{1,12})/ },
];

// 短链域名,需要先 redirect 才能拿到真实 URL
const SHORT_URL_RE = /^https?:\/\/(b23\.tv|bili2233\.cn)\//i;

// 顺序很重要:BV 优先于 AV(BV 里有数字,AV 也有数字,但 BV 标识更明确),
// MD 优先于 SS(都含字母+数字,但 MD 更短小精确)
const ORDERED_PATTERNS = [
  ID_PATTERNS[0], // BV
  ID_PATTERNS[4], // MD
  ID_PATTERNS[3], // SS
  ID_PATTERNS[2], // EP
  ID_PATTERNS[1], // AV
];

/**
 * 如果输入是 B 站短链(b23.tv / bili2233.cn),跟随跳转拿真实 URL。
 * 否则原样返回。失败时也原样返回,让后面的正则自己处理。
 */
async function expandShortUrl(input, { timeoutMs = 5000 } = {}) {
  if (!input || typeof input !== 'string') return input;
  if (!SHORT_URL_RE.test(input.trim())) return input;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(input, {
      method: 'GET',
      redirect: 'follow',
      headers: BILI_API_HEADERS,
      signal: controller.signal,
    });
    // res.url 是 fetch 跟随所有 redirect 后的最终 URL
    return res.url || input;
  } catch {
    return input;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * 从一段文本(可能包含 URL、也可能是裸 ID)里抽出第一个匹配的 ID。
 * 解析顺序:
 *   1. 优先看是不是 B 站标准 URL 路径(如 /video/BVxx、/bangumi/media/mdxx)
 *      —— 这样不会被分享描述里"类似 BV1xx"或"from_spmid=666.4.mylist.2"等噪声干扰
 *   2. 路径没匹配到,再按 ID 前缀在文本里扫一遍
 *
 * 返回 { type, id } 或 null
 */
function parseId(input) {
  if (!input || typeof input !== 'string') return null;
  const text = input.trim();
  if (!text) return null;

  // 先尝试路径感知匹配
  for (const { type, regex } of PATH_PATTERNS) {
    const m = text.match(regex);
    if (m) {
      let id = m[1];
      if (type !== 'BV') id = type.toLowerCase() + id;
      return { type, id, source: 'path' };
    }
  }

  // 退回到普通 ID 前缀匹配
  for (const { type, regex } of ORDERED_PATTERNS) {
    const m = text.match(regex);
    if (m) {
      let id = m[1];
      if (type === 'BV') id = 'BV' + id;
      else id = type.toLowerCase() + id;
      return { type, id, source: 'prefix' };
    }
  }
  return null;
}

/**
 * 统一 fetch wrapper:解析 JSON,带超时,失败抛带原因的错。
 * 不同端点的有效载荷 key 不同(普通视频用 data,番剧用 result),
 * payloadKey 参数控制取哪个字段。
 */
async function biliFetch(url, { timeoutMs = 10000, payloadKey = 'data' } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      headers: BILI_API_HEADERS,
      signal: controller.signal,
    });
    if (!res.ok) {
      throw new Error(`B 站接口 HTTP ${res.status}`);
    }
    const json = await res.json();
    if (json.code !== 0) {
      throw new Error(`B 站接口业务错误 code=${json.code} ${json.message || ''}`.trim());
    }
    const payload = json[payloadKey];
    if (payload == null) {
      throw new Error(`B 站接口返回无 payload (${payloadKey} 为空)`);
    }
    return payload;
  } catch (e) {
    if (e.name === 'AbortError') {
      throw new Error(`B 站接口超时 (${timeoutMs}ms)`);
    }
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * 解析普通视频(BV / AV)
 */
async function fetchVideo(id, { type }) {
  const paramName = type === 'BV' ? 'bvid' : 'aid';
  const idValue = type === 'BV' ? id : id.slice(2); // av12345 -> 12345
  const data = await biliFetch(
    `https://api.bilibili.com/x/web-interface/view?${paramName}=${encodeURIComponent(idValue)}`,
  );

  // B 站 view 返回的字段名是固定的,在这里归一化
  return {
    id: data.bvid,         // 主 ID 用 BV 统一表达
    aid: data.aid,
    title: data.title,
    cover: data.pic,
    url: data.short_link || `https://www.bilibili.com/video/${data.bvid}`,
    duration: data.duration,    // 秒
    pubdate: data.pubdate,     // 秒级时间戳
    desc: data.desc,
    owner: data.owner
      ? { mid: data.owner.mid, name: data.owner.name, face: data.owner.face }
      : null,
    stat: data.stat || null,
    pages: Array.isArray(data.pages)
      ? data.pages.map((p) => ({
          cid: p.cid,
          page: p.page,
          part: p.part,
          duration: p.duration,
        }))
      : [],
    tname: data.tname || null,
  };
}

/**
 * 解析番剧(EP / SS / MD)
 * 端点选择:
 *   - EP  → pgc/view/web/season?ep_id=xxx     (有效载荷 key = result)
 *   - SS  → pgc/view/web/season?season_id=xxx (有效载荷 key = result)
 *   - MD  → pgc/view/web/media?media_id=xxx   (有效载荷 key = result, 顶层还带 media)
 */
async function fetchBangumi(id, { type }) {
  const idValue = id.slice(2); // ep12345 -> 12345
  let data;
  if (type === 'EP') {
    data = await biliFetch(
      `https://api.bilibili.com/pgc/view/web/season?ep_id=${encodeURIComponent(idValue)}`,
      { payloadKey: 'result' },
    );
  } else if (type === 'SS') {
    data = await biliFetch(
      `https://api.bilibili.com/pgc/view/web/season?season_id=${encodeURIComponent(idValue)}`,
      { payloadKey: 'result' },
    );
  } else {
    // MD: /media 返回结构多套一层 media,统一展平到外层
    const media = await biliFetch(
      `https://api.bilibili.com/pgc/view/web/media?media_id=${encodeURIComponent(idValue)}`,
      { payloadKey: 'result' },
    );
    data = { ...(media || {}), ...(media.media || {}) };
  }

  return {
    id:
      type === 'EP'
        ? `ep${idValue}`
        : type === 'SS'
          ? `ss${idValue}`
          : `md${idValue}`,
    title: data.title,
    cover: data.cover,
    url:
      type === 'EP'
        ? `https://www.bilibili.com/bangumi/play/ep${idValue}`
        : type === 'SS'
          ? `https://www.bilibili.com/bangumi/play/ss${idValue}`
          : `https://www.bilibili.com/bangumi/media/md${idValue}`,
    desc: data.evaluate || '',
    type: data.type || null,           // 1 = 番剧, 2 = 电影, 3 = 纪录片 ...
    areas: data.areas || [],
    styles: data.styles || [],
    publish: data.publish || null,     // 上线时间
    episodes: (data.episodes || []).slice(0, 50).map((ep) => ({
      id: ep.id,
      aid: ep.aid,
      bvid: ep.bvid,
      title: ep.title,
      long_title: ep.long_title,
      cover: ep.cover,
      duration: ep.duration,
      url: ep.share_url || (ep.bvid ? `https://www.bilibili.com/video/${ep.bvid}` : null),
    })),
    season_id: data.season_id,
    media_id: data.media_id,
  };
}

/**
 * 对外主入口:解析输入,返回统一结构。
 *  - type: 'video' | 'bangumi'
 *  - data: { ... } 失败时为 null
 *  - error: 失败时的描述
 */
async function resolve(input) {
  // 短链先展开
  const expanded = await expandShortUrl(input);
  const parsed = parseId(expanded);
  if (!parsed) {
    return {
      ok: false,
      error: '无法识别 ID(支持 BV/AV/EP/SS/MD 或对应 URL)',
      code: 'PARSE_FAILED',
    };
  }

  const isBangumi = parsed.type === 'EP' || parsed.type === 'SS' || parsed.type === 'MD';

  try {
    const data = isBangumi
      ? await fetchBangumi(parsed.id, parsed)
      : await fetchVideo(parsed.id, parsed);
    return {
      ok: true,
      input: parsed.id,
      type: isBangumi ? 'bangumi' : 'video',
      rawType: parsed.type,
      data,
    };
  } catch (e) {
    return {
      ok: false,
      input: parsed.id,
      error: e.message || String(e),
      code: 'API_ERROR',
    };
  }
}

module.exports = {
  resolve,
  parseId,
  // 单独导出方便测试
  _internals: { fetchVideo, fetchBangumi, biliFetch },
};