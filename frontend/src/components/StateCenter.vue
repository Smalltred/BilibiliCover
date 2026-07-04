<!--
  状态展示组件 —— 复用 result-panel 内的「空 / 错误」两种状态。
  loading 状态因为用 spinner 旋转图标,在 ResultPanel 里直接写更直观,不抽进来。
-->
<template>
  <div class="state-center">
    <p class="state-icon">{{ icon }}</p>
    <p class="state-msg">{{ message }}</p>
    <button v-if="showReset" class="btn btn-secondary" @click="$emit('reset')">
      重新输入
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 'empty' | 'error'
  variant: { type: String, required: true },
  error: { type: String, default: '' }
})
defineEmits(['reset'])

const ICONS = {
  empty: '📺',
  error: '⚠️'
}

const icon = computed(() => ICONS[props.variant] || '')

const message = computed(() => {
  if (props.variant === 'error') return props.error || '出错了'
  return '输入视频 ID 或粘贴链接开始'
})

const showReset = computed(() => props.variant === 'error')
</script>