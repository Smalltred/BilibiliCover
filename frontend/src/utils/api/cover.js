/**
 * 封面 API 专属层
 *
 * 职责:
 *   - 把前端 ID 结构还原成完整输入(URL / BV号 / AV号 / EP/SS/MD号)
 *   - 调后端 /api/?url=xxx 拿统一响应
 *   - 把后端响应(后端字段名)映射成前端组件期望的扁平结构
 *
 * 后端统一负责:
 *   - BV/AV/EP/SS/MD 五种 ID 解析
 *   - 调对应 B 站接口
 *   - 归一化返回结构 { ok, type, data: {...} }
 */

import { request } from './client.js'
import { API_BASE } from '@/utils/constants.js'

/**
 * @typedef {Object} VideoId
 * @property {string} type  'bv' | 'av' | 'ep' | 'ss' | 'md' | 'short'
 * @property {string} [id]  纯 ID(不带前缀)
 * @property {string} [raw] 原始输入(URL / 短链)
 */

/**
 * @typedef {Object} CoverData
 * @property {string}  id           跨类型规范 ID:BV/AV → 'BV1xx'|'av12345',EP/SS/MD → 'ep12345'|'ss12345'|'md12345'
 * @property {string}  title
 * @property {string}  cover
 * @property {string}  [bvid]       仅 BV/AV 视频有值
 * @property {string}  [avid]       仅 AV 视频有值('av12345' 形式)
 * @property {string}  [author]
 * @property {number|null} [play]
 * @property {number}  [duration]   秒
 * @property {number}  [pubdate]    秒级时间戳
 * @property {string}  [description]
 * @property {string}  [url]
 * @property {string}  [type]       'video' | 'season' | 'mock'
 * @property {Object|null} [season]
 */

/**
 * @typedef {Object} ApiResponse
 * @property {number} code
 * @property {string} message
 * @property {CoverData|null} data
 */

/**
 * 把前端 ID 结构还原成后端期望的字符串输入
 * @param {VideoId} videoId
 * @returns {string|null}
 */
function buildInput(videoId) {
  if (videoId.raw) return videoId.raw
  if (videoId.id) {
    // bv 直接是 BV1xxx,其他要补回前缀(av/ep/ss/md)
    return videoId.type === 'bv' ? videoId.id : `${videoId.type}${videoId.id}`
  }
  return null
}

/**
 * 把后端归一化响应映射成前端组件期望的扁平结构
 *
 * 后端 video.data:  { id, aid, title, cover, url, duration, pubdate, desc, owner, stat, ... }
 * 后端 bangumi.data:{ id, title, cover, url, desc, type, areas, styles, publish, episodes, ... }
 *
 * @returns {CoverData}
 */
function mapCoverData(payload) {
  const isBangumi = payload.type === 'bangumi'
  const d = payload.data || {}
  const owner = d.owner || null

  return {
    // 跨类型规范 ID:BV/AV → 'BV1xx'/'av12345',EP/SS/MD → 'ep12345'/'ss12345'/'md12345'
    // 下游(下载文件名等)优先用这个字段,不再依赖 bvid/avid
    id: d.id || '',
    title: d.title || '',
    cover: d.cover || '',
    bvid: isBangumi ? '' : d.id || '',
    avid: isBangumi ? '' : d.aid ? `av${d.aid}` : '',
    author: isBangumi ? '' : owner?.name || '',
    play: isBangumi ? null : d.stat?.view || 0,
    duration: isBangumi ? 0 : d.duration || 0,
    pubdate:
      d.pubdate ||
      (d.publish?.pub_time ? Date.parse(d.publish.pub_time) / 1000 : 0),
    description: d.desc || d.evaluate || '',
    url: d.url || '',
    type: isBangumi ? 'season' : 'video',
    season: isBangumi
      ? {
          seasonId: d.season_id,
          mediaId: d.media_id,
          areas: d.areas || [],
          styles: d.styles || [],
          episodeCount: (d.episodes || []).length,
          firstEpisodes: (d.episodes || []).slice(0, 12)
        }
      : null
  }
}

/**
 * 主入口:解析一个视频 ID,拿封面数据
 * @param {VideoId} videoId
 * @returns {Promise<ApiResponse>}
 * @throws 后端返回 ok=false 时,把 error 抛出去给上层 catch
 */
export async function fetchCover(videoId) {
  const input = buildInput(videoId)
  if (!input) {
    throw new Error('无法识别输入')
  }

  const url = `${API_BASE}/?url=${encodeURIComponent(input)}`
  const json = await request(url)

  if (!json.ok) {
    throw new Error(json.error || '后端返回失败')
  }

  return {
    code: 200,
    message: '获取成功',
    data: mapCoverData(json)
  }
}