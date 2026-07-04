<!--
  Hero 区:大标题 + 副标题 + 输入框 + 渐变背景
  整页最具视觉冲击力的部分,把核心交互(输入 + 解析)放在这里
-->
<template>
  <section class="hero">
    <div class="hero-content">
      <h1 class="hero-title">
        <span class="hero-title-main">哔哩哔哩封面提取</span>
        <span class="hero-title-sub">一键获取视频 / 番剧的高清封面</span>
      </h1>

      <form class="hero-form" @submit.prevent="handleSubmit">
        <div class="input-wrap">
          <input
            v-model="input"
            type="text"
            class="hero-input"
            placeholder="粘贴 BV 号 / AV 号 / EP / SS / MD,或完整 B 站链接"
            :disabled="loading"
            spellcheck="false"
            autocomplete="off"
            @keydown.esc="input = ''"
          />
          <button
            v-if="input"
            type="button"
            class="input-clear"
            :disabled="loading"
            @click="input = ''"
            aria-label="清空输入"
          >×</button>
        </div>
        <button
          type="submit"
          class="hero-submit"
          :disabled="loading || !input.trim()"
        >
          <span v-if="loading" class="hero-submit-loading">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </span>
          <span v-else>{{ input.trim() ? '解析封面 →' : '请输入 ID' }}</span>
        </button>
      </form>

      <p class="hero-hint">
        支持:
        <code>BV1xxxxxxxxx</code> · <code>av12345</code> · <code>ep12345</code> ·
        <code>ss12345</code> · <code>md12345</code> · 完整 URL · b23.tv 短链
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  loading: { type: Boolean, default: false }
})
const emit = defineEmits(['submit'])

const input = ref('')

function handleSubmit() {
  const value = input.value.trim()
  if (!value) return
  emit('submit', value)
}
</script>

<style scoped>
.hero {
  padding: 96px 24px 48px;
}

.hero-content {
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
}

.hero-title {
  margin: 0 0 32px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hero-title-main {
  font-size: 40px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--accent);
}

.hero-title-sub {
  font-size: 16px;
  color: var(--text-secondary);
  font-weight: 400;
}

.hero-form {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.input-wrap {
  position: relative;
  flex: 1;
  min-width: 0;
}

.hero-input {
  width: 100%;
  padding: 14px 40px 14px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-primary);
  font-size: 15px;
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
  font-family: inherit;
}

.hero-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(251, 114, 153, 0.15);
}

.hero-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hero-input::placeholder {
  color: var(--text-muted);
}

.input-clear {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border: none;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
}

.input-clear:hover:not(:disabled) {
  background: var(--accent);
  color: white;
}

.hero-submit {
  padding: 14px 24px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  white-space: nowrap;
  transition: all var(--transition);
  min-width: 140px;
}

.hero-submit:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-light);
}

.hero-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hero-submit-loading {
  display: inline-flex;
  gap: 4px;
  align-items: center;
}

.hero-submit-loading .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: white;
  animation: dot-bounce 1.4s infinite ease-in-out both;
}

.hero-submit-loading .dot:nth-child(1) { animation-delay: -0.32s; }
.hero-submit-loading .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.hero-hint {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.8;
}

.hero-hint code {
  background: var(--bg-elevated);
  padding: 1px 6px;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Consolas, monospace;
  font-size: 12px;
  color: var(--text-secondary);
}

@media (max-width: 640px) {
  .hero { padding: 40px 16px 32px; }
  .hero-title-main { font-size: 28px; }
  .hero-title-sub { font-size: 14px; }
  .hero-form { flex-direction: column; }
  .hero-submit { width: 100%; }
}
</style>