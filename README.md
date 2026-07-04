# bilibili-cover

B 站视频/番剧封面解析。**Node.js + Express 后端 + Vue 3 + Vite 前端**。

主页输入 BV / AV / EP / SS / MD 号或粘贴 B 站链接,一秒拿到高清封面,支持复制、下载、跳转原页面。后端 API 完全公开(主页底部"API 文档"页可看)。

## 目录结构

```
blibilicover/
├── backend/                 Node.js 后端(Express)
│   ├── src/
│   │   ├── app.js           入口(dev=3000 固定 / prod=随机端口)
│   │   ├── routes/api.js    GET / /resolve /diag + /health
│   │   ├── services/        5 种 ID 解析 + B 站 API 调用
│   │   └── utils/           端口探测、TTL 缓存
│   └── data/                port.txt + server.log(运行时生成)
├── frontend/                Vue3 前端(Vite)
│   ├── src/
│   │   ├── App.vue          视图切换(主页 / API 文档)
│   │   ├── components/      HeroInput / CoverPreview(modal)/ ApiDocs / SiteNav ...
│   │   ├── composables/     useResolver / useClipboard / useViewport
│   │   └── utils/api/       client(通用 fetch) + cover(业务)
│   └── dist/                vite build 产物(部署时用)
├── scripts/
│   └── build-release.py     Python 跨平台打包脚本
├── deploy.sh                宝塔 / Linux 一键部署
├── start.sh / stop.sh       后端启动 / 停止
├── VERSION                  根目录版本号
├── LICENSE                  MIT
└── README.md
```

## 开发模式

两个独立窗口,顺序先 backend 再 frontend:

```bash
# 窗口 1: 后端(dev 固定 3000)
cd backend
npm install
npm start

# 窗口 2: 前端(Vite 5173,代理 /api → 3000)
cd frontend
npm install
npm run dev
```

打开 `http://localhost:5173`。

## 生产部署(宝塔 / 通用 Linux)

```bash
# 1. 本地打包(跨平台,纯 Python,无 BOM 问题)
python scripts/build-release.py
# 产物在 releases/blibilicover-vX.Y.Z.zip

# 1.5 可选:自动 bump 版本号 patch +1
python scripts/build-release.py --bump
# 记得手动同步 frontend/package.json 和 VERSION

# 2. 上传 zip 到服务器,解压
unzip blibilicover-vX.Y.Z.zip
cd blibilicover-vX.Y.Z

# 3. 一键部署(装依赖 + 后台启动后端)
bash deploy.sh
# 输出端口号(如 3187),把端口写进宝塔 nginx 反代

# 4. 宝塔 nginx 站点配置
#   root <解压路径>/frontend/dist
#   location /api/  -> proxy_pass http://127.0.0.1:<端口>/
```

部署后:

```bash
bash start.sh    # 重启
bash stop.sh     # 停止
tail -f backend/data/server.log   # 看日志
```

## 接口文档

详见主页底部 **API 文档** 页,或后端代码 `backend/src/routes/api.js`。

| 端点 | 说明 |
|------|------|
| `GET /api/?url=xxx` | 解析 B 站视频/番剧,返回封面 + 标题 + UP 主 + 简介 |
| `GET /api/resolve?url=xxx` | 同上,别名 |
| `GET /api/diag?url=xxx` | 诊断输入识别,不调 B 站 API |
| `GET /api/health` | 健康检查 + uptime |

## 支持的 ID

| 类型 | URL 路径                | B 站接口                              | 说明         |
|------|------------------------|--------------------------------------|--------------|
| BV   | `/video/BVxxx`         | `/x/web-interface/view?bvid=xxx`     | 普通视频     |
| AV   | `/video/avxxx`         | `/x/web-interface/view?aid=xxx`      | 普通视频(老) |
| EP   | `/bangumi/play/epxxx`  | `/pgc/view/web/season?ep_id=xxx`     | 番剧集       |
| SS   | `/bangumi/play/ssxxx`  | `/pgc/view/web/season?season_id=xxx` | 番剧季       |
| MD   | `/bangumi/media/mdxxx` | `/pgc/view/web/media?media_id=xxx`   | 番剧条目     |

短链 `https://b23.tv/xxx` 自动跟随 redirect。

## 端口

| 场景 | 后端 | 前端 |
|------|------|------|
| dev  | 固定 3000 | 固定 5173 |
| prod | 随机 3000-3999(写到 `data/port.txt`) | 由 nginx serve `dist/` |

后端被占时自动换下一个,最多 20 次;也可用 `PORT=xxxx npm start` 指定。

## 许可

MIT License © 2026 hecady

历史:项目早期是 Python Flask 版本,完整代码保留在 `flask-legacy` 分支。