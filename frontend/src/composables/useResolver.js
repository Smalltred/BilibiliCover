/**
 * 解析请求的状态机 composable
 *
 * 把 loading/data/error 状态 + submit/reset 行为封装在一起,
 * 组件只需要拿响应式状态 + 调函数,不关心内部逻辑。
 *
 * 用法:
 *   const { loading, result, error, submit, reset } = useResolver()
 */
import { ref } from 'vue'
import { extractVideoId } from '@/utils/bilibili.js'
import { fetchCover } from '@/utils/api/cover.js'

export function useResolver() {
  const loading = ref(false)
  const result = ref(null)
  const error = ref('')

  async function submit(input) {
    if (loading.value) return

    const videoId = extractVideoId(input)
    if (!videoId) {
      error.value = '未识别到有效的视频 ID,请检查输入(支持 BV/AV/EP/SS/MD 或 B 站链接)'
      result.value = null
      return
    }

    error.value = ''
    result.value = null
    loading.value = true

    try {
      const res = await fetchCover(videoId)
      result.value = res.data
    } catch (e) {
      error.value = e.message || String(e)
    } finally {
      loading.value = false
    }
  }

  function reset() {
    result.value = null
    error.value = ''
  }

  return { loading, result, error, submit, reset }
}