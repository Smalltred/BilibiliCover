#!/bin/bash
# ============================================================
# B 站封面提取 - 停止后端
# ============================================================
# 优先读 server.pid,fallback 读 port.txt 用 lsof 找进程
# ============================================================
set -e

cd "$(dirname "$0")"
ROOT="$(pwd)"
cd "$ROOT/backend"

PID=""

# 优先用 pid 文件
if [ -f data/server.pid ]; then
    PID=$(cat data/server.pid 2>/dev/null)
fi

# fallback:用 port 找
if [ -z "$PID" ] && [ -f data/port.txt ]; then
    PORT=$(cat data/port.txt 2>/dev/null)
    PID=$(lsof -ti :"$PORT" 2>/dev/null || true)
fi

if [ -z "$PID" ]; then
    echo "没找到运行中的服务(pid 文件和端口都没有)"
    exit 1
fi

if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    echo "✓ 已停止 (pid=$PID)"
    rm -f data/server.pid
else
    echo "进程 $PID 不存在,清理 pid 文件"
    rm -f data/server.pid
fi