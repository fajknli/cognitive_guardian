#!/bin/bash
# 模型下载脚本

set -e

cd "$(dirname "$0")"

echo "========================================"
echo "   认知姿态守护者 - 模型下载工具"
echo "========================================"
echo ""

# 创建模型目录
mkdir -p models

# 选择模型
echo "请选择要下载的模型:"
echo "1) TinyLlama-1.1B Q4 (约650MB, 推荐)"
echo "2) TinyLlama-1.1B Q2 (约250MB, 快速)"
echo "3) Phi-2 Q4 (约800MB, 高质量)"
echo "4) 跳过"
echo ""
read -p "请选择 [1-4]: " choice

case $choice in
    1)
        echo "下载 TinyLlama-1.1B Q4..."
        cd models
        wget --continue https://hf-mirror.com/TheBloke/TinyLlama-1.1B-GGUF/resolve/main/tinyllama-1.1b.Q4_K_M.gguf
        ;;
    2)
        echo "下载 TinyLlama-1.1B Q2..."
        cd models
        wget --continue https://hf-mirror.com/TheBloke/TinyLlama-1.1B-GGUF/resolve/main/tinyllama-1.1b.Q2_K.gguf
        ;;
    3)
        echo "下载 Phi-2 Q4..."
        cd models
        wget --continue https://hf-mirror.com/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf
        ;;
    4)
        echo "跳过下载"
        ;;
    *)
        echo "无效选择，跳过下载"
        ;;
esac

echo ""
echo "下载完成！"
