/**
 * 宝塔 Node 传统项目部署 - 入口文件
 *
 * 宝塔面板配置:
 *   - 项目目录: <解压路径>
 *   - 启动文件: server.js   (即本文件)
 *   - 启动方式: node
 *   - 端口: 自定义(默认 3000,可通过 PORT 环境变量覆盖)
 *
 * 实际后端逻辑在 backend/src/app.js。
 * 这里只是把请求转过去 —— 让宝塔面板能识别到根目录的入口文件。
 *
 * 数据目录 backend/data/ 在第一次启动时自动创建,日志写到 backend/data/server.log。
 */
require('./backend/src/app.js')