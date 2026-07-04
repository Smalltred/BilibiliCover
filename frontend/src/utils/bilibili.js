/**
 * 从用户输入中提取 B 站视频 ID
 *
 * 支持格式:
 *   - BV 号:        BV1xxxxxxxxx(11 位,BV1 开头)
 *   - AV 号:        av\d+
 *   - EP 号(番剧):  ep\d+
 *   - SS 号(番剧 season):  ss\d+
 *   - MD 号(媒体):  md\d+
 *   - 完整 URL:     https://www.bilibili.com/video/BVxxx
 *   - b23.tv 短链:  https://b23.tv/xxxxx(前端无法 redirect,留给后端)
 *
 * 用户复制粘贴的常见形态(分享给朋友):
 *   "【开箱...】 https://b23.tv/7B5lMvN"     →  短链 + 标题
 *   "BV1xx411c7xx 一些备注..."               →  裸 ID + 描述
 *   "看了 https://www.bilibili.com/video/BV1xx 这个视频"  →  URL 在文本中间
 *
 * @param {string} input  用户原始输入
 * @returns {{type: string, id?: string, raw?: string} | null}
 */
export function extractVideoId(input) {
  if (!input || typeof input !== 'string') return null
  const text = input.trim()
  if (!text) return null

  // 1. 先抽出文本里的 URL(如果有)
  //    分享文本里 URL 通常夹在中间/末尾,不能要求开头是 https://
  const urlMatch = text.match(/https?:\/\/[^\s]+/i)
  const candidate = urlMatch ? urlMatch[0] : text

  // 2. b23.tv / bili2233.cn 短链 —— 不管在文本开头还是中间都识别
  //    前端没法 redirect,直接返回原 URL,后端 expandShortUrl 处理
  if (/^https?:\/\/(b23\.tv|bili2233\.cn)\//i.test(candidate)) {
    return { type: 'short', raw: candidate }
  }

  // 3. 标准 B 站 URL 路径(/video/BVxx、/bangumi/...)
  //    优先匹配 URL 路径段,避免吃进文本里其他位置干扰字符
  const pathMatch =
    candidate.match(/\/video\/(BV1[A-Za-z0-9]{9})/i) ||
    candidate.match(/\/video\/[aA][vV](\d+)/) ||
    candidate.match(/\/bangumi\/play\/[eE][pP](\d+)/) ||
    candidate.match(/\/bangumi\/play\/[sS][sS](\d+)/) ||
    candidate.match(/\/bangumi\/media\/[mM][dD](\d+)/)
  if (pathMatch) {
    if (pathMatch[1].startsWith('BV')) return { type: 'bv', id: pathMatch[1] }
    // 按前缀反推 type
    const lower = pathMatch[0].toLowerCase()
    if (lower.includes('/av')) return { type: 'av', id: pathMatch[1] }
    if (lower.includes('/ep')) return { type: 'ep', id: pathMatch[1] }
    if (lower.includes('/ss')) return { type: 'ss', id: pathMatch[1] }
    if (lower.includes('/md')) return { type: 'md', id: pathMatch[1] }
  }

  // 4. 退回到裸 ID 前缀匹配 —— 整个原文里扫一遍,
  //    这样 "BV1xx411c7xx 一些备注" 也能识别
  //    BV 号 —— 严格匹配 BV1 + 9 位字母数字
  const bvMatch = text.match(/BV1[A-Za-z0-9]{9}/)
  if (bvMatch) return { type: 'bv', id: bvMatch[0] }

  // AV 号
  const avMatch = text.match(/\bav(\d+)\b/i)
  if (avMatch) return { type: 'av', id: avMatch[1] }

  // EP 号(番剧)
  const epMatch = text.match(/\bep(\d+)\b/i)
  if (epMatch) return { type: 'ep', id: epMatch[1] }

  // SS 号(番剧 season)
  const ssMatch = text.match(/\bss(\d+)\b/i)
  if (ssMatch) return { type: 'ss', id: ssMatch[1] }

  // MD 号(媒体)
  const mdMatch = text.match(/\bmd(\d+)\b/i)
  if (mdMatch) return { type: 'md', id: mdMatch[1] }

  return null
}