<!--
  顶部导航条
  - sticky 在视口顶部,滚动时一直可见
  - 半透明 + backdrop blur,跟 dark theme 配合
  - 左:Logo / 站名(可点击回主页)
  - 右:视图切换按钮(主页 / API 文档),当前页高亮
-->
<template>
  <header class="site-nav">
    <div class="nav-inner">
      <button class="brand" @click="$emit('navigate', 'home')">
        <span class="brand-logo">🎬</span>
        <span class="brand-text">Bilibili Cover</span>
      </button>

      <nav class="nav-actions">
        <button
          class="nav-btn"
          :class="{ active: view === 'home' }"
          @click="$emit('navigate', 'home')"
        >主页</button>
        <button
          class="nav-btn"
          :class="{ active: view === 'docs' }"
          @click="$emit('navigate', 'docs')"
        >API 文档</button>
      </nav>
    </div>
  </header>
</template>

<script setup>
defineProps({
  view: { type: String, default: 'home' }
})
defineEmits(['navigate'])
</script>

<style scoped>
.site-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(13, 17, 23, 0.7);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}

.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-family: inherit;
  transition: opacity var(--transition);
}

.brand:hover {
  opacity: 0.8;
}

.brand-logo {
  font-size: 20px;
  line-height: 1;
}

.brand-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.01em;
}

.nav-actions {
  display: flex;
  gap: 6px;
}

.nav-btn {
  padding: 6px 14px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  font-family: inherit;
  transition: all var(--transition);
}

.nav-btn:hover {
  color: var(--text-primary);
  background: var(--bg-elevated);
}

.nav-btn.active {
  color: var(--accent);
  background: rgba(251, 114, 153, 0.1);
  border-color: var(--accent);
}
</style>