#!/bin/bash
# ============================================================
# B 站封面提取 - 启动后端(后台)
# ============================================================
# 用法: bash start.sh
# 端口从 backend/data/port.txt 读取
# PID 写到 backend/data/server.pid
# 日志在 backend/data/server.log
# ============================================================
set -e

cd "$(dirname "$0")"
ROOT="$(pwd)"
cd "$ROOT/backend"

# 端口文件所在目录
mkdir -p data

# 装依赖(若需要)
if [ ! -d node_modules ]; then
    echo "==> 装后端依赖..."
    npm install --omit=dev
fi

# 停旧的(若存在)
if [ -f data/server.pid ]; then
    OLD_PID=$(cat data/server.pid 2>/dev/null)
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
        echo "==> 停旧服务(pid=$OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
fi

# 后台启动
echo "==> 启动后端..."
RANDOM_PORT=1 nohup node src/app.js > data/server.log 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > data/server.pid
sleep 1.5

PORT=$(cat data/port.txt 2>/dev/null || echo "?")
echo "✓ 已启动(pid=$NEW_PID, port=$PORT, log=backend/data/server.log)"
echo "  停止: bash stop.sh"