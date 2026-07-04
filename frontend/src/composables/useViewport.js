/**
 * 视口高度同步 composable
 *
 * 把 window.innerHeight 实时写入 CSS 变量 --app-height,
 * 让 .app { height: var(--app-height) } 跟随 DevTools 开/关、窗口缩放、
 * 移动端地址栏折叠而自动调整。
 *
 * 设计目的:比 100dvh 更兼容 —— 任何浏览器都能响应 DevTools 占用视口的情况。
 *
 * 用法:在 main.js 调一次 useViewport(),副作用会自动挂载。
 */
export function useViewport() {
  function sync() {
    document.documentElement.style.setProperty(
      '--app-height',
      `${window.innerHeight}px`
    )
  }

  window.addEventListener('resize', sync)
  window.addEventListener('orientationchange', sync)
  sync()

  // 返回 stop 函数,测试或热替换场景可用
  return () => {
    window.removeEventListener('resize', sync)
    window.removeEventListener('orientationchange', sync)
  }
}