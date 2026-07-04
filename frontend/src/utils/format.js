/**
 * 展示用格式化函数 —— 跟 UI 渲染逻辑解耦,方便测试和复用
 */

/**
 * 播放量/点赞数等大数字 → "12.3 万" / "1.5 亿"
 */
export function formatStat(n) {
  if (n === null || n === undefined) return ''
  if (n >= 100000000) return (n / 100000000).toFixed(1) + ' 亿'
  if (n >= 10000) return (n / 10000).toFixed(1) + ' 万'
  return String(n)
}

/**
 * 秒数 → "mm:ss" 或 "h:mm:ss"
 */
export function formatDuration(s) {
  if (!s && s !== 0) return ''
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return h > 0
    ? `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
    : `${m}:${String(sec).padStart(2, '0')}`
}

/**
 * 秒级时间戳 → "2024/5/1 12:34:56"(本地时区)
 */
export function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts * 1000)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleString('zh-CN', { hour12: false })
}