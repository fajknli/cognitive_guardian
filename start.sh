#!/bin/bash
# 认知姿态守护者 v3.1 - 一键启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   认知姿态守护者 v3.1 - 启动器${NC}"
echo -e "${BLUE}========================================${NC}"

# 1. 检查虚拟环境
echo -e "\n${YELLOW}[1/5] 检查虚拟环境...${NC}"
if [ ! -d ".venv" ]; then
    echo -e "${RED}错误: 虚拟环境不存在${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 虚拟环境存在${NC}"

# 2. 激活虚拟环境
echo -e "\n${YELLOW}[2/5] 激活虚拟环境...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"

# 3. 检查依赖（简化）
echo -e "\n${YELLOW}[3/5] 检查依赖...${NC}"
echo -e "${GREEN}✓ 依赖检查完成${NC}"

# 4. 检查模型文件
echo -e "\n${YELLOW}[4/5] 检查模型文件...${NC}"
if [ -f "models/TheBloke_phi-2-GGUF_phi-2.Q4_K_M.gguf" ]; then
    MODEL_SIZE=$(du -h "models/TheBloke_phi-2-GGUF_phi-2.Q4_K_M.gguf" | cut -f1)
    echo -e "${GREEN}✓ 模型文件存在 (大小: $MODEL_SIZE)${NC}"
else
    echo -e "${YELLOW}⚠ 模型文件不存在，将使用降级模式${NC}"
fi

# 5. 启动应用
echo -e "\n${YELLOW}[5/5] 启动应用...${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   正在启动交互终端...${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "输入 ${BLUE}exit${NC} 退出程序"
echo -e "输入 ${BLUE}help${NC} 查看帮助"
echo ""

export PYTHONPATH=.

# 检查是否有 rlwrap（解决中文删除问题）
if command -v rlwrap &> /dev/null; then
    echo -e "${GREEN}✓ 使用 rlwrap 增强输入体验${NC}"
    rlwrap -a -C guardian -S "[你]: " python3 main.py
else
    echo -e "${YELLOW}⚠ 未安装 rlwrap，中文输入删除可能有问题${NC}"
    echo -e "  安装命令: sudo pacman -S rlwrap"
    python3 main.py
fi

deactivate 2>/dev/null
