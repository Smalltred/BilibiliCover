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
 * @param {string} input  用户原始输入
 * @returns {{type: string, id?: string, raw?: string} | null}
 */
export function extractVideoId(input) {
  if (!input || typeof input !== 'string') return null
  const text = input.trim()
  if (!text) return null

  // b23.tv 短链:前端无法 resolve redirect,直接返回原值,后端处理
  if (/^https?:\/\/b23\.tv\//i.test(text)) {
    return { type: 'short', raw: text }
  }

  // 先抽出 URL(如果有)
  const urlMatch = text.match(/https?:\/\/[^\s]+/i)
  const candidate = urlMatch ? urlMatch[0] : text

  // BV 号 —— 严格匹配 BV1 + 9 位字母数字
  const bvMatch = candidate.match(/BV1[A-Za-z0-9]{9}/)
  if (bvMatch) return { type: 'bv', id: bvMatch[0] }

  // AV 号
  const avMatch = candidate.match(/\bav(\d+)\b/i)
  if (avMatch) return { type: 'av', id: avMatch[1] }

  // EP 号(番剧)
  const epMatch = candidate.match(/\bep(\d+)\b/i)
  if (epMatch) return { type: 'ep', id: epMatch[1] }

  // SS 号(番剧 season)
  const ssMatch = candidate.match(/\bss(\d+)\b/i)
  if (ssMatch) return { type: 'ss', id: ssMatch[1] }

  // MD 号(媒体)
  const mdMatch = candidate.match(/\bmd(\d+)\b/i)
  if (mdMatch) return { type: 'md', id: mdMatch[1] }

  return null
}