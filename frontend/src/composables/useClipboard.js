/**
 * 剪贴板复制 composable
 *
 * 提供:
 *   - copy(text):异步复制,返回 boolean 表示成功/失败
 *   - flash(el, text):临时替换元素文字提示,1.2s 后还原
 *   - lastResult:'success' | 'failed' | '',供 UI 二次展示
 *
 * 设计原因:ResultCover 复制按钮需要「点击 → 短暂反馈 → 还原」的交互,
 * 这个交互模式未来可能复用(分享链接 / 解析其他等),抽成 composable 更整洁。
 */
import { ref } from 'vue'

export function useClipboard() {
  const lastResult = ref('')

  async function copy(text) {
    if (!text) return false
    try {
      await navigator.clipboard.writeText(text)
      lastResult.value = 'success'
      return true
    } catch {
      lastResult.value = 'failed'
      return false
    }
  }

  /**
   * 短暂替换元素的文字内容,1.2s 后还原
   * @param {HTMLElement|null} target  要修改的元素,通常传 document.activeElement
   * @param {string} text             临时文字(如 '复制成功')
   * @param {number} [durationMs=1200] 还原延迟
   */
  function flash(target, text, durationMs = 1200) {
    if (!target) return
    const original = target.textContent
    target.textContent = text
    setTimeout(() => {
      target.textContent = original
    }, durationMs)
  }

  return { copy, flash, lastResult }
}