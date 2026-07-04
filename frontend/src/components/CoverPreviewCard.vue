<!--
  C 布局结果卡(banner 风格,无持久化)
  - 操作按钮组在封面之上
  - 封面 banner 铺满容器宽度,16:9
  - 元信息横排(UP 主 · 时长 · 播放 · 发布 · BV · AV)
  - 简介完整展开
  - 按钮右对齐,outline 风格
-->
<template>
  <article class="card">
    <!-- 操作按钮(在封面之上) -->
    <div class="card-actions">
      <button class="action-btn action-primary" @click="handleCopy">
        {{ copyLabel }}
      </button>
      <button class="action-btn" @click="handleDownload">
        {{ downloadLabel }}
      </button>
      <a
        v-if="data.url"
        :href="data.url"
        target="_blank"
        rel="noopener"
        class="action-btn"
      >B 站 ↗</a>
      <button class="action-btn" @click="$emit('reset')">
        重新解析
      </button>
    </div>

    <!-- 封面(banner) -->
    <div class="card-cover">
      <img
        :src="data.cover"
        :alt="data.title"
        class="card-img"
        referrerpolicy="no-referrer"
        loading="lazy"
      />
      <div v-if="data.type === MOCK_TYPE" class="card-mock-badge">演示数据</div>
    </div>

    <!-- 信息 -->
    <div class="card-info">
      <h3 class="card-title">{{ data.title || '无标题' }}</h3>

      <dl class="card-meta">
        <span v-if="data.author" class="meta-item">
          <span class="meta-key">UP 主</span>{{ data.author }}
        </span>
        <span v-if="data.duration" class="meta-item">
          <span class="meta-key">时长</span>{{ formatDuration(data.duration) }}
        </span>
        <span v-if="data.play" class="meta-item">
          <span class="meta-key">播放</span>{{ formatStat(data.play) }}
        </span>
        <span v-if="data.pubdate" class="meta-item">
          <span class="meta-key">发布</span>{{ formatTime(data.pubdate) }}
        </span>
        <span v-if="data.bvid" class="meta-item meta-mono">
          <span class="meta-key">BV</span>{{ data.bvid }}
        </span>
        <span v-if="data.avid" class="meta-item meta-mono">
          <span class="meta-key">AV</span>{{ data.avid }}
        </span>
      </dl>

      <p v-if="data.description" class="card-desc">{{ data.description }}</p>
    </div>
  </article>
</template>

<script setup>
import { ref, computed } from 'vue'
import { formatStat, formatDuration, formatTime } from '@/utils/format.js'
import { useClipboard } from '@/composables/useClipboard.js'
import { MOCK_TYPE } from '@/utils/constants.js'

const props = defineProps({
  data: { type: Object, required: true }
})
defineEmits(['reset'])

const filename = computed(() => {
  const title = (props.data?.title || 'cover')
    // 去掉文件系统不允许的字符
    .replace(/[\\/:*?"<>|\r\n]/g, '_')
    // 截断过长的标题(保留前 50 字)
    .slice(0, 50)
  const id = props.data?.id || props.data?.bvid || props.data?.avid || 'unknown'
  // YYYYMMDD_HHMMSS —— 精确到秒,避免一秒内多次下载覆盖
  const d = new Date()
  const ts =
    d.getFullYear().toString() +
    String(d.getMonth() + 1).padStart(2, '0') +
    String(d.getDate()).padStart(2, '0') +
    '_' +
    String(d.getHours()).padStart(2, '0') +
    String(d.getMinutes()).padStart(2, '0') +
    String(d.getSeconds()).padStart(2, '0')
  return `${title}-${id}-${ts}.jpg`
})

const { copy } = useClipboard()
const copyLabel = ref('复制封面链接')
const downloadLabel = ref('下载')
let resetTimer = null
let downloadTimer = null

async function handleCopy() {
  const ok = await copy(props.data.cover)
  copyLabel.value = ok ? '已复制 ✓' : '复制失败'
  if (resetTimer) clearTimeout(resetTimer)
  resetTimer = setTimeout(() => {
    copyLabel.value = '复制封面链接'
  }, 1500)
}

// 走后端代理下载,绕过 B 站 Referer 防盗链
async function handleDownload() {
  try {
    downloadLabel.value = '下载中…'
    const url = `/api/download?url=${encodeURIComponent(props.data.cover)}&filename=${encodeURIComponent(filename.value)}`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const blob = await res.blob()
    const blobUrl = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = filename.value
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(blobUrl)
    downloadLabel.value = '已下载 ✓'
  } catch {
    downloadLabel.value = '下载失败'
  }
  if (downloadTimer) clearTimeout(downloadTimer)
  downloadTimer = setTimeout(() => {
    downloadLabel.value = '下载'
  }, 1500)
}
</script>

<style scoped>
/* ===== 卡片布局(banner 风格:上下结构)===== */
.card {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ----- 封面(banner:铺满容器宽度,16:9)----- */
.card-cover {
  position: relative;
  border-radius: var(--radius);
  overflow: hidden;
  aspect-ratio: 16 / 9;
  background: var(--bg-elevated);
  width: 100%;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.card-mock-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 10px;
  background: rgba(251, 114, 153, 0.9);
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
}

/* ----- 信息 ----- */
.card-info {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 0;
}

.card-title {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 16px;
  color: var(--text-primary);
  line-height: 1.4;
  word-break: break-word;
}

/* ===== 元信息(横排,key + value)===== */
.card-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 14px;
  margin: 0 0 16px;
  padding: 12px 16px;
  background: var(--bg-elevated);
  border-radius: var(--radius);
  font-size: 13px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-primary);
}

.meta-key {
  font-size: 11px;
  color: var(--text-muted);
  padding: 1px 6px;
  background: var(--bg-secondary);
  border-radius: 3px;
  letter-spacing: 0.04em;
}

.meta-mono {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Consolas, monospace;
  font-size: 12px;
}

/* ===== 简介(完整展开)===== */
.card-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: var(--radius);
  border-left: 3px solid var(--accent);
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
}

/* ===== 操作按钮(右对齐)===== */
.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 18px;
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  font-family: inherit;
  white-space: nowrap;
  transition: all var(--transition);
  flex: 1 1 0; /* 等宽 4 个按钮均分容器宽度 */
  min-width: 0;
}

.action-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

/* 移动端 (<= 480px):2x2 网格 + 紧凑间距,4 个中文按钮不再被截断 */
@media (max-width: 480px) {
  .card-actions {
    gap: 6px;
  }
  .action-btn {
    /* 每行 2 个:calc(50% - 3px) 算上 6px gap */
    flex: 1 1 calc(50% - 3px);
    padding: 10px 8px;
    font-size: 12px;
  }
}

.action-primary {
  border-color: var(--accent);
  color: var(--accent);
}

.action-primary:hover {
  background: var(--accent);
  color: white;
}
</style>