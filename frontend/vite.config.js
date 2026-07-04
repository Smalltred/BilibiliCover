import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite 配置:
// - dev 阶段把 /api/* 代理到 Node 后端(默认端口 3000,可在 .env 用 VITE_BACKEND_PORT 覆盖)
// - 生产阶段用 nginx 反向代理或后端托管前端 dist/
//
// 端口约定:
//   - 前端 Vite:  5172
//   - 后端 dev:   3000(固定,方便代理对接)
//   - 后端 prod:  随机端口(通过 npm run start:prod 启动)
//
// 路径别名:@ → src/,在 .vue / .js 里直接 import xxx from '@/components/...'
const BACKEND_PORT = process.env.VITE_BACKEND_PORT || '3000'
const BACKEND_TARGET = `http://127.0.0.1:${BACKEND_PORT}`

console.log(`[vite] backend proxy target = ${BACKEND_TARGET}`)

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5172,
    open: false,
    strictPort: false,
    proxy: {
      '/api': {
        target: BACKEND_TARGET,
        changeOrigin: true
        // 后端把 apiRouter 挂在 /api 下,/api 前缀原样转发即可,不再 rewrite
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    chunkSizeWarningLimit: 600
  }
})