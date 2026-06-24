#!/usr/bin/env bash
#
# 🌍 GeoLibre Web UI — 一键启动脚本
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🌍  GeoLibre Web UI 启动器            ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Check Python ──
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "${RED}❌ 未找到 Python3，请先安装: https://www.python.org/downloads/${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python:${NC} $($PYTHON --version 2>&1)"

# ── Install deps ──
echo ""
echo -e "${YELLOW}📦 检查依赖...${NC}"
deps_ok=true
for mod in fastapi uvicorn; do
    if ! $PYTHON -c "import $mod" 2>/dev/null; then
        echo -e "   ${YELLOW}✗ $mod 未安装${NC}"
        deps_ok=false
    fi
done

if [ "$deps_ok" = false ]; then
    echo -e "${YELLOW}📥 安装缺失依赖...${NC}"
    $PYTHON -m pip install -q fastapi uvicorn python-multipart
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 所有依赖已就绪${NC}"
fi

# ── Menu ──
echo ""
echo -e "${BOLD}请选择启动方式:${NC}"
echo "  1) 🚀 启动 Web UI 服务器 (推荐)"
echo "  2) 🌐 打开静态 HTML (仅前端，无后端 API)"
echo "  3) ❌ 退出"
echo ""
read -p "输入 1/2/3: " choice

case "$choice" in
    1)
        echo ""
        echo -e "${GREEN}🚀 启动 GeoLibre Web UI...${NC}"
        echo ""
        echo -e "${CYAN}  📍 浏览器访问: http://localhost:8000${NC}"
        echo -e "${CYAN}  📊 API 文档:    http://localhost:8000/docs${NC}"
        echo -e "${CYAN}  💚 健康检查:    http://localhost:8000/api/health${NC}"
        echo ""
        cd "$SCRIPT_DIR/python"
        exec $PYTHON -m geolibre.web_app
        ;;
    2)
        echo ""
        echo -e "${GREEN}🌐 打开静态 HTML ...${NC}"
        echo -e "${YELLOW}   ⚠ 注意: 无后端 API，地图操作不持久化${NC}"
        echo ""
        open "$SCRIPT_DIR/web-ui.html"
        ;;
    3)
        echo "👋 再见"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac
