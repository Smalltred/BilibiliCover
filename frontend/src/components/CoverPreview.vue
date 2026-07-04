<!--
  当前结果 modal 弹窗
  - 全屏遮罩 + 居中卡片
  - 点击遮罩关闭(背景层用 .self 修饰符,卡片内部点击不触发)
  - ESC 键关闭
  - 用 <Teleport to="body"> 渲染到 body,避免被父级 overflow/z-index 影响
-->
<template>
  <Teleport to="body">
    <div class="modal-mask" @click.self="$emit('reset')">
      <div class="modal-card" role="dialog" aria-modal="true">
        <CoverPreviewCard v-if="data" :data="data" @reset="$emit('reset')" />
        <StateCenter v-else-if="error" variant="error" :error="error" @reset="$emit('reset')" />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import CoverPreviewCard from './CoverPreviewCard.vue'
import StateCenter from './StateCenter.vue'

defineProps({
  data: { type: Object, default: null },
  error: { type: String, default: '' }
})
const emit = defineEmits(['reset'])

function onKeydown(e) {
  if (e.key === 'Escape') emit('reset')
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.7);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  animation: fade-in 0.18s ease-out;
}

.modal-card {
  position: relative;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow);
  animation: pop-in 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes pop-in {
  from {
    opacity: 0;
    transform: scale(0.94) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@media (max-width: 640px) {
  .modal-card { padding: 16px; }
  .modal-mask { padding: 12px; }
}
</style>