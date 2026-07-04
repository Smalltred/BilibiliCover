#!/bin/bash
# ============================================================
# B 站封面提取 - 前端热更新(零停服,无需重启 Node)
# ============================================================
# 用法:
#   bash update-frontend.sh <frontend-zip>
#
# 示例:
#   bash update-frontend.sh blibilicover-frontend-v0.1.5.zip
#
# 原理:
#   后端用 express.static(frontend/dist) 托管前端静态资源,
#   直接覆盖 dist/ 文件,下一次 HTTP 请求就是新的。
#   Node 进程不需要重启,后端代码也不重新加载。
#
# 适用场景:
#   - 只改了 frontend/src/... 下的代码(组件 / 样式 / 文本)
#   - 没改 backend/... / server.js / package.json
#
# 不适用场景(改这些就走完整 deploy.sh):
#   - 后端逻辑、路由、新增依赖
#   - server.js / deploy.sh / start.sh 等启动文件
# ============================================================
set -e

# 颜色(仅当输出是 TTY 时)
if [ -t 1 ]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; NC=''
fi

# ---- 参数校验 ----
ZIP_FILE="${1:-}"
if [ -z "$ZIP_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} 用法: bash update-frontend.sh <frontend-zip>"
    echo "  例: bash update-frontend.sh blibilicover-frontend-v0.1.5.zip"
    exit 1
fi
if [ ! -f "$ZIP_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} 文件不存在: $ZIP_FILE"
    exit 1
fi

# ---- 定位项目根(脚本所在目录)----
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$SCRIPT_DIR"
DIST_DIR="$ROOT/frontend/dist"

if [ ! -d "$DIST_DIR" ]; then
    echo -e "${RED}[ERROR]${NC} 找不到 $DIST_DIR —— 这不是部署目录?"
    echo "  请在宝塔解压后的项目根目录下跑这个脚本。"
    exit 1
fi

# ---- 检查 zip 内容 ----
echo "==> [1/4] 校验 zip..."
NEW_VER=$(unzip -p "$ZIP_FILE" VERSION 2>/dev/null | tr -d '\r\n' || true)
if [ -z "$NEW_VER" ]; then
    echo -e "${RED}[ERROR]${NC} zip 里找不到 VERSION 文件,可能不是 frontend 包"
    exit 1
fi
echo "    新版本: v$NEW_VER"

# zip 里必须有 frontend/dist/index.html(校验 zip 结构)
if ! unzip -l "$ZIP_FILE" 2>/dev/null | grep -q "frontend/dist/index.html"; then
    echo -e "${RED}[ERROR]${NC} zip 里找不到 frontend/dist/index.html —— 不是 frontend 包?"
    exit 1
fi
echo "    ✓ zip 结构合法(包含 frontend/dist/index.html)"

# ---- 解压到临时目录 ----
TMP_DIR=$(mktemp -d -t frontend-update-XXXXXX)
echo "==> [2/4] 解压到临时目录 $TMP_DIR ..."
unzip -q -o "$ZIP_FILE" -d "$TMP_DIR"
NEW_DIST="$TMP_DIR/frontend/dist"
if [ ! -f "$NEW_DIST/index.html" ]; then
    echo -e "${RED}[ERROR]${NC} 解压后找不到 $NEW_DIST/index.html"
    rm -rf "$TMP_DIR"
    exit 1
fi

# ---- 备份旧 dist(便于回滚)----
BACKUP_DIR=""
if [ -f "$DIST_DIR/index.html" ]; then
    BACKUP_DIR="$ROOT/.staging/prev-dist-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$(dirname "$BACKUP_DIR")"
    mv "$DIST_DIR" "$BACKUP_DIR"
    echo "==> [3/4] 备份旧 dist 到 $BACKUP_DIR"
else
    echo "==> [3/4] 没有旧 dist,跳过备份"
fi

# ---- 应用新 dist ----
mkdir -p "$DIST_DIR"
# -a 保留权限和属性,trailing slash 避免同名嵌套目录问题
cp -a "$NEW_DIST"/. "$DIST_DIR"/
echo "    ✓ 新 dist 已写入 $DIST_DIR"

# ---- 清理临时目录 ----
rm -rf "$TMP_DIR"

# ---- 健康检查(Node 没动,理论上后端不受影响)----
echo "==> [4/4] 健康检查..."
# 端口从 backend/data/port.txt 读
PORT="?"
if [ -f "$ROOT/backend/data/port.txt" ]; then
    PORT=$(cat "$ROOT/backend/data/port.txt")
fi
if [ "$PORT" != "?" ]; then
    HEALTH=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://127.0.0.1:$PORT/health" 2>/dev/null || echo "000")
    if [ "$HEALTH" = "200" ]; then
        echo -e "    ${GREEN}✓${NC} /health 返回 200(后端未受影响)"
    else
        echo -e "    ${YELLOW}!${NC} /health 返回 $HEALTH,Node 可能未运行"
    fi
fi

# ---- 完成 ----
echo ""
echo "============================================================"
echo -e " ${GREEN}前端热更新完成!${NC}"
echo "============================================================"
echo " 版本:    v$NEW_VER"
echo " dist:    $DIST_DIR"
echo " 备份:    ${BACKUP_DIR:-(无)}"
echo ""
echo " 现在刷新浏览器即可看到新版本。"
echo " Node 进程未重启,后端代码保持不变。"
echo ""
if [ -n "$BACKUP_DIR" ]; then
    echo " 回滚(如有需要):"
    echo "   rm -rf $DIST_DIR"
    echo "   mv $BACKUP_DIR $DIST_DIR"
    echo ""
fi
echo " 清理超过 7 天的备份:"
echo "   find $ROOT/.staging -maxdepth 1 -name 'prev-dist-*' -mtime +7 -exec rm -rf {} +"