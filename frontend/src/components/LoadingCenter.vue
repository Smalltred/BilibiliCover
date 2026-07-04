<!--
  加载状态组件 —— 跟 StateCenter 对称,统一 result-panel 内的状态展示。
  只展示 spinner + 提示文字,不涉及数据渲染。
-->
<template>
  <div class="state-center">
    <div class="spinner"></div>
    <p class="state-msg">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: '正在获取封面…' }
})
</script>