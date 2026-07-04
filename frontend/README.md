# B 站封面提取 - 前端

Vue 3 + Vite 单页应用,提取 B 站视频的封面、标题、UP 主、播放量等信息。

## 当前阶段

**仅前端**,后端 API 暂未实现。

- dev 阶段通过 **Vite 代理**直接调 B 站公开接口(`api.bilibili.com`),能拿到真实数据
- API 调用失败 / 生产环境 fallback 到 **mock 数据**,前端体验不中断
- 等后端实现后,改 `frontend/src/utils/api.js` 的 `API_BASE` 即可对接

## 启动

```bash
cd frontend
npm install
npm run dev
```

默认端口 `5173`,浏览器打开 http://localhost:5173

## 构建生产包

```bash
npm run build
```

产物在 `frontend/dist/`,纯静态文件,任何静态服务器都能托管。

## 支持的输入格式

| 类型 | 示例 | 备注 |
|---|---|---|
| BV 号 | `BV1xx411c7mD` | 优先匹配 |
| AV 号 | `av170001` | 需后端转换 |
| EP 号 | `ep12345` | 番剧分集 |
| SS 号 | `ss12345` | 番剧 season |
| MD 号 | `md12345` | 番剧媒体 |
| 完整 URL | `https://www.bilibili.com/video/BV1xx411c7mD` | 自动抽取 ID |
| b23.tv 短链 | `https://b23.tv/xxxxx` | 前端无法 redirect,后端处理 |

## 目录结构

```
frontend/
├── src/
│   ├── App.vue               根组件
│   ├── main.js               入口
│   ├── components/
│   │   ├── InputPanel.vue    输入框 + 解析按钮
│   │   └── ResultPanel.vue   封面展示 + 信息
│   ├── utils/
│   │   ├── bilibili.js       ID 提取正则
│   │   └── api.js            API 调用层(代理 + mock fallback)
│   └── styles/
│       └── main.css          全局样式(深色主题 + B 站粉)
├── index.html
├── vite.config.js            Vite + B 站 API 反代配置
└── package.json
```