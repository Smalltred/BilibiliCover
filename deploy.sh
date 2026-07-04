#!/bin/bash
# ============================================================
# B 站封面提取 - 一键部署(宝塔 / 通用 Linux)
# ============================================================
# 用法:
#   1. 上传 blibilicover-vX.Y.Z.zip 到服务器任一目录
#   2. unzip blibilicover-vX.Y.Z.zip
#   3. cd blibilicover-vX.Y.Z
#   4. bash deploy.sh
#
# 部署步骤:
#   - 装后端依赖(若未装)
#   - 装前端依赖 + 构建 dist/(若 zip 里没有)
#   - 后台启动后端,随机端口(端口写到 backend/data/port.txt)
# ============================================================

set -e

cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "==> [1/4] 检查环境..."
command -v node >/dev/null 2>&1 || { echo "[ERROR] 需要 Node.js >= 20"; exit 1; }
NODE_VER=$(node -v)
echo "    Node.js: $NODE_VER"

echo "==> [2/4] 安装后端依赖..."
cd "$ROOT/backend"
if [ ! -d node_modules ]; then
    npm install --omit=dev
    echo "    ✓ 后端依赖安装完成"
else
    echo "    - 跳过(node_modules 已存在)"
fi

echo "==> [3/4] 安装前端依赖 + 构建(若需要)..."
cd "$ROOT/frontend"
if [ ! -d dist ]; then
    npm install
    npm run build
    echo "    ✓ 前端构建完成"
else
    echo "    - 跳过(dist/ 已存在)"
fi

echo "==> [4/4] 后台启动后端..."
cd "$ROOT/backend"
# 先停旧的(如果存在)
if [ -f data/port.txt ]; then
    OLD_PORT=$(cat data/port.txt 2>/dev/null)
    OLD_PID=$(lsof -ti :"$OLD_PORT" 2>/dev/null || true)
    if [ -n "$OLD_PID" ]; then
        echo "    - 停止旧服务(port=$OLD_PORT, pid=$OLD_PID)"
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
fi

# 后台启动新服务(RANDOM_PORT=1 让后端选随机端口)
RANDOM_PORT=1 nohup node src/app.js > data/server.log 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > data/server.pid
sleep 2

NEW_PORT=$(cat data/port.txt 2>/dev/null || echo "?")
echo "    ✓ 后端已启动 (pid=$NEW_PID, port=$NEW_PORT)"

echo ""
echo "============================================================"
echo " 部署完成"
echo "============================================================"
echo " 后端端口:    $NEW_PORT"
echo " 前端静态:    $ROOT/frontend/dist"
echo " 日志:        $ROOT/backend/data/server.log"
echo ""
echo " 宝塔 nginx 站点配置参考:"
echo "   server {"
echo "     listen 80;"
echo "     server_name your.domain.com;"
echo "     root $ROOT/frontend/dist;"
echo "     index index.html;"
echo "     location / { try_files \$uri /index.html; }"
echo "     location /api/ {"
echo "       proxy_pass http://127.0.0.1:$NEW_PORT/;"
echo "       proxy_set_header Host \$host;"
echo "     }"
echo "   }"
echo ""
echo " 停止服务:  bash stop.sh"