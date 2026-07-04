<!--
  API 文档页
  展示后端全部公开端点,每个端点含:
    - method + path
    - 说明
    - 请求参数
    - 响应示例
    - 「在新窗口打开」按钮(直接调 API)
-->
<template>
  <section class="api-docs">
    <header class="docs-header">
      <h1 class="docs-title">API 文档</h1>
      <p class="docs-subtitle">
        本项目后端 API 完全公开,可直接通过 HTTP 调用,无需鉴权。
      </p>
    </header>

    <article v-for="ep in endpoints" :key="ep.path" class="endpoint">
      <div class="endpoint-head">
        <span class="method" :data-method="ep.method.toLowerCase()">{{ ep.method }}</span>
        <code class="path">{{ ep.path }}</code>
        <a
          class="try-btn"
          :href="ep.tryUrl"
          target="_blank"
          rel="noopener"
        >在新窗口打开 ↗</a>
      </div>

      <p class="endpoint-desc">{{ ep.description }}</p>

      <div v-if="ep.params?.length" class="endpoint-block">
        <h4 class="block-title">请求参数</h4>
        <ul class="param-list">
          <li v-for="p in ep.params" :key="p.name">
            <code class="param-name">{{ p.name }}</code>
            <span class="param-type">{{ p.type }}</span>
            <span class="param-required">{{ p.required ? '必填' : '可选' }}</span>
            <span class="param-desc">{{ p.description }}</span>
          </li>
        </ul>
      </div>

      <div class="endpoint-block">
        <h4 class="block-title">响应示例</h4>
        <pre class="code-block"><code>{{ ep.response }}</code></pre>
      </div>
    </article>
  </section>
</template>

<script setup>
const API_PREFIX = '/api'

const endpoints = [
  {
    method: 'GET',
    path: '/?url=xxx',
    tryUrl: `${API_PREFIX}/?url=BV1GJ411x7h7`,
    description: '解析一个 B 站视频/番剧,返回封面地址、标题、UP 主、简介等。',
    params: [
      { name: 'url', type: 'string', required: true, description: 'BV 号 / AV 号 / EP 号 / SS 号 / MD 号,或完整 B 站链接,或 b23.tv 短链' },
      { name: 'id', type: 'string', required: false, description: 'url 的别名,二选一即可' },
      { name: 'q', type: 'string', required: false, description: 'url 的别名,二选一即可' }
    ],
    response: `{
  "ok": true,
  "input": "BV1GJ411x7h7",
  "type": "video",
  "rawType": "BV",
  "data": {
    "id": "BV1GJ411x7h7",
    "aid": 170001,
    "title": "示例视频",
    "cover": "https://i0.hdslb.com/bfs/cover/xxx.jpg",
    "url": "https://www.bilibili.com/video/BV1GJ411x7h7",
    "duration": 213,
    "pubdate": 1612345678,
    "desc": "视频简介...",
    "owner": { "mid": 12345, "name": "示例 UP" }
  }
}`
  },
  {
    method: 'GET',
    path: '/resolve?url=xxx',
    tryUrl: `${API_PREFIX}/resolve?url=md2684`,
    description: '/?url= 的别名,完全等价的接口。',
    params: [
      { name: 'url', type: 'string', required: true, description: '同 /?url= 参数' }
    ],
    response: `// 与 /?url= 返回结构完全一致`
  },
  {
    method: 'GET',
    path: '/diag?url=xxx',
    tryUrl: `${API_PREFIX}/diag?url=https://www.bilibili.com/bangumi/play/ss38921`,
    description: '诊断输入识别结果,不实际调用 B 站接口,可用于排查 ID 解析问题。',
    params: [
      { name: 'url', type: 'string', required: true, description: '待诊断的输入' }
    ],
    response: `{
  "ok": true,
  "input": "https://www.bilibili.com/bangumi/play/ss38921",
  "parsed": {
    "type": "SS",
    "id": "ss38921",
    "source": "path"
  },
  "isShortUrl": false
}`
  },
  {
    method: 'GET',
    path: '/health',
    tryUrl: `${API_PREFIX}/health`,
    description: '健康检查,返回服务运行状态和 uptime(秒)。',
    params: [],
    response: `{
  "ok": true,
  "service": "bilibili-cover",
  "uptime": 1234.56
}`
  }
]
</script>

<style scoped>
.api-docs {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 16px 0 32px;
}

.docs-header {
  text-align: center;
  margin-bottom: 40px;
}

.docs-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--accent);
}

.docs-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.endpoint {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-light);
}

.endpoint-head {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.method {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Consolas, monospace;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: 0.04em;
}

.method[data-method='get'] {
  background: rgba(0, 174, 236, 0.15);
  color: var(--accent-blue);
}

.path {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Consolas, monospace;
  font-size: 14px;
  color: var(--text-primary);
  flex: 1;
  word-break: break-all;
}

.try-btn {
  font-size: 12px;
  padding: 6px 12px;
  border-radius: var(--radius);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  text-decoration: none;
  border: 1px solid var(--border);
  transition: all var(--transition);
  white-space: nowrap;
}

.try-btn:hover {
  color: var(--text-primary);
  border-color: var(--accent);
}

.endpoint-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 16px;
  line-height: 1.7;
}

.endpoint-block {
  margin-bottom: 14px;
}

.endpoint-block:last-child {
  margin-bottom: 0;
}

.block-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 0 0 8px;
}

.param-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.param-list li {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px solid var(--border);
}

.param-list li:last-child {
  border-bottom: none;
}

.param-name {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Consolas, monospace;
  font-size: 12px;
  color: var(--text-primary);
  background: var(--bg-elevated);
  padding: 2px 6px;
  border-radius: 3px;
}

.param-type {
  font-size: 11px;
  color: var(--text-muted);
}

.param-required {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.param-required:not([class*='可选']) {
  background: rgba(251, 114, 153, 0.15);
  color: var(--accent);
}

.param-desc {
  flex-basis: 100%;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.code-block {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 14px;
  margin: 0;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.6;
}

.code-block code {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Consolas, monospace;
  color: var(--text-primary);
  white-space: pre;
}
</style>