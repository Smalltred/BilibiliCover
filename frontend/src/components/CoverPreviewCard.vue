<!--
  当前解析的封面卡片:左侧大封面,右侧信息(标题/关键字段/简介/操作按钮)
-->
<template>
  <article class="card">
    <!-- 左侧:封面 -->
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

    <!-- 右侧:信息 -->
    <div class="card-info">
      <h3 class="card-title">{{ data.title || '无标题' }}</h3>

      <dl class="card-meta">
        <div v-if="data.bvid" class="meta-row">
          <dt>BV 号</dt>
          <dd class="mono">{{ data.bvid }}</dd>
        </div>
        <div v-if="data.avid" class="meta-row">
          <dt>AV 号</dt>
          <dd class="mono">{{ data.avid }}</dd>
        </div>
        <div v-if="data.author" class="meta-row">
          <dt>UP 主</dt>
          <dd>{{ data.author }}</dd>
        </div>
        <div v-if="data.play" class="meta-row">
          <dt>播放量</dt>
          <dd>{{ formatStat(data.play) }}</dd>
        </div>
        <div v-if="data.duration" class="meta-row">
          <dt>时长</dt>
          <dd>{{ formatDuration(data.duration) }}</dd>
        </div>
        <div v-if="data.pubdate" class="meta-row">
          <dt>发布时间</dt>
          <dd>{{ formatTime(data.pubdate) }}</dd>
        </div>
      </dl>

      <p v-if="data.description" class="card-desc">{{ data.description }}</p>

      <div class="card-actions">
        <button class="action-btn action-primary" @click="handleCopy">
          {{ copyLabel }}
        </button>
        <a
          :href="data.cover"
          :download="filename"
          target="_blank"
          rel="noopener"
          class="action-btn action-secondary"
        >下载</a>
        <a
          v-if="data.url"
          :href="data.url"
          target="_blank"
          rel="noopener"
          class="action-btn action-ghost"
        >打开 B 站 ↗</a>
        <button class="action-btn action-ghost" @click="$emit('reset')">
          重新解析
        </button>
      </div>
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
  const id = props.data?.bvid || props.data?.avid || 'cover'
  return `${id}.jpg`
})

const { copy } = useClipboard()
const copyLabel = ref('复制封面链接')
let resetTimer = null

async function handleCopy() {
  const ok = await copy(props.data.cover)
  copyLabel.value = ok ? '已复制 ✓' : '复制失败'
  if (resetTimer) clearTimeout(resetTimer)
  resetTimer = setTimeout(() => {
    copyLabel.value = '复制封面链接'
  }, 1500)
}
</script>

<style scoped>
.card {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
  gap: 28px;
}

@media (max-width: 768px) {
  .card { grid-template-columns: 1fr; }
}

/* ----- 封面 ----- */
.card-cover {
  position: relative;
  border-radius: var(--radius);
  overflow: hidden;
  aspect-ratio: 16 / 9;
  background: var(--bg-elevated);
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
  min-width: 0;
}

.card-title {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 16px;
  color: var(--text-primary);
  line-height: 1.4;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 16px;
  margin: 0 0 16px;
  padding: 14px;
  background: var(--bg-elevated);
  border-radius: var(--radius);
}

.meta-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.meta-row dt {
  font-size: 11px;
  color: var(--text-muted);
  margin: 0;
}

.meta-row dd {
  font-size: 13px;
  color: var(--text-primary);
  margin: 0;
  word-break: break-all;
}

.meta-row dd.mono {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Consolas,
    'Liberation Mono', Menlo, monospace;
  font-size: 12px;
}

.card-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 16px;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: var(--radius);
  border-left: 3px solid var(--accent);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 160px;
  overflow-y: auto;
  line-height: 1.7;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: auto;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 18px;
  border: none;
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  font-family: inherit;
  white-space: nowrap;
  transition: all var(--transition);
  min-width: 100px;
}

.action-primary {
  background: var(--accent);
  color: white;
}

.action-primary:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

.action-secondary {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.action-secondary:hover {
  border-color: var(--accent);
}

.action-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.action-ghost:hover {
  color: var(--text-primary);
  border-color: var(--text-secondary);
}
</style>