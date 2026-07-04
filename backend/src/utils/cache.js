/**
 * 简单的进程内缓存。
 *
 * 需求:同一个 (BV/AV/EP/SS/MD) 短时间内重复请求,直接返回 B 站结果,
 *       不重复打 B 站 API。
 *
 * 设计:
 *   - Map<key, { value, expireAt }>
 *   - get(key) 过期自动返回 undefined 并删除
 *   - set(key, value, ttlMs) 默认 5 分钟
 *   - 容量上限防止内存膨胀 (maxEntries = 5000,超过后清掉最早的 1/4)
 *
 * 老 Flask 仓库的坑:用 str(hash(frozenset(...))) 做 key,PYTHONHASHSEED
 * 随机会让缓存命中率归零。这里直接用 url + id 做字符串 key,稳。
 */

class TTLCache {
  constructor({ defaultTtlMs = 5 * 60 * 1000, maxEntries = 5000 } = {}) {
    this.defaultTtlMs = defaultTtlMs;
    this.maxEntries = maxEntries;
    this.map = new Map();
  }

  get(key) {
    const item = this.map.get(key);
    if (!item) return undefined;
    if (item.expireAt <= Date.now()) {
      this.map.delete(key);
      return undefined;
    }
    // LRU 触达:刷新顺序
    this.map.delete(key);
    this.map.set(key, item);
    return item.value;
  }

  set(key, value, ttlMs = this.defaultTtlMs) {
    if (this.map.has(key)) this.map.delete(key);
    this.map.set(key, { value, expireAt: Date.now() + ttlMs });
    this.evictIfNeeded();
  }

  delete(key) {
    this.map.delete(key);
  }

  clear() {
    this.map.clear();
  }

  size() {
    return this.map.size;
  }

  evictIfNeeded() {
    if (this.map.size <= this.maxEntries) return;
    const dropCount = Math.floor(this.maxEntries / 4);
    const iter = this.map.keys();
    for (let i = 0; i < dropCount; i++) {
      const { value } = iter.next();
      if (value === undefined) break;
      this.map.delete(value);
    }
  }
}

module.exports = { TTLCache };