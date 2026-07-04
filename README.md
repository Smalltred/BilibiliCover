# bilibili-cover

B 站视频/番剧封面解析。Node.js 后端 + Vue3 前端。

## 目录结构

```
blibilicover/
├── backend/                Node.js 后端 (Express)
│   ├── src/
│   │   ├── app.js          入口 (随机端口启动)
│   │   ├── routes/api.js   GET /api 和 /diag 端点
│   │   ├── services/bilibili.js   5 种 ID 解析 + B 站 API 调用
│   │   └── utils/          端口探测、TTL 缓存
│   ├── scripts/start.js    后台启动脚本
│   └── data/port.txt       启动后写入当前端口
└── frontend/               Vue3 前端 (Vite)
    ├── src/utils/api.js    调用后端 /api
    └── vite.config.js      代理 /api → 后端端口
```

## 启动

**两个独立窗口** (顺序:先 backend,再 frontend)

```bash
# 窗口 1: 后端
cd backend
npm install          # 第一次需要
npm start            # 或者: node scripts/start.js

# 窗口 2: 前端
cd frontend
npm install          # 第一次需要
npm run dev          # Vite 默认 5173 端口
```

Vite 启动时会读 `backend/data/port.txt`,把 `/api/*` 代理到后端随机端口。

## 接口

后端:
- `GET /?url=BV1xx` 或 `?url=https://...` —— 解析,返回统一结构
- `GET /diag?url=...` —— 不调 B 站 API,只看识别结果(调试用)
- `GET /health` —— 健康检查

返回结构:
```json
{
  "ok": true,
  "input": "md28223043",
  "type": "bangumi",
  "rawType": "MD",
  "data": {
    "id": "md28223043",
    "title": "凡人修仙传",
    "cover": "https://i0.hdslb.com/...",
    "url": "https://www.bilibili.com/bangumi/media/md28223043",
    ...
  }
}
```

## 支持的 ID

| 类型 | URL 路径                | B 站接口                              | 说明         |
|------|------------------------|--------------------------------------|--------------|
| BV   | /video/BVxxx          | /x/web-interface/view?bvid=xxx       | 普通视频     |
| AV   | /video/avxxx          | /x/web-interface/view?aid=xxx        | 普通视频(老) |
| EP   | /bangumi/play/epxxx   | /pgc/view/web/season?ep_id=xxx       | 番剧集       |
| SS   | /bangumi/play/ssxxx   | /pgc/view/web/season?season_id=xxx   | 番剧季       |
| MD   | /bangumi/media/mdxxx  | /pgc/view/web/media?media_id=xxx     | 番剧条目     |

短链 `https://b23.tv/xxx` 自动跟随 redirect。

## 端口

- **后端**:随机 3000-3999,启动后写到 `backend/data/port.txt`
- **前端 (Vite)**:固定 5173 (`strictPort: false`,被占也换)
- 后端被占时自动换下一个,最多 20 次
- 也可用 `PORT=xxxx npm start` 指定后端端口

## 停止后端

```bash
# 方法 1:用启动脚本时输出的 PID
taskkill /F /PID <pid>

# 方法 2:全部 node 进程里找
tasklist | findstr node
```