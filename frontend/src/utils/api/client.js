/**
 * 通用 fetch wrapper
 *
 * 能力:
 *   - JSON 自动 parse
 *   - 超时控制(默认 10s,通过 AbortController 取消)
 *   - 非 2xx 抛带状态的错误
 *   - 网络错误 / 超时统一抛 Error
 *
 * 用法:
 *   const data = await request('/api/?url=xxx')
 *   const data = await request('/api/foo', { method: 'POST', body: { x: 1 }, timeoutMs: 5000 })
 */

/**
 * @typedef {Object} RequestOptions
 * @property {string} [method]       HTTP 方法,默认 'GET'
 * @property {*}      [body]         请求体,会被 JSON.stringify
 * @property {Object} [headers]      额外请求头
 * @property {number} [timeoutMs]    超时毫秒数,默认 10000
 * @property {string} [responseType] 'json' | 'text' | 'blob',默认 'json'
 */

/**
 * @param {string} url
 * @param {RequestOptions} [options]
 * @returns {Promise<*>}
 */
export async function request(url, options = {}) {
  const {
    method = 'GET',
    body,
    headers = {},
    timeoutMs = 10000,
    responseType = 'json'
  } = options

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const res = await fetch(url, {
      method,
      headers: body ? { 'Content-Type': 'application/json', ...headers } : headers,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal
    })

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText || ''}`.trim())
    }

    if (responseType === 'text') return res.text()
    if (responseType === 'blob') return res.blob()
    return res.json()
  } catch (e) {
    if (e.name === 'AbortError') {
      throw new Error(`请求超时(${timeoutMs}ms)`)
    }
    throw e
  } finally {
    clearTimeout(timer)
  }
}