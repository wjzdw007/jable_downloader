#!/bin/bash
# 加载 .env 文件中的环境变量

if [ -f .env ]; then
    echo "✓ 正在加载 .env 文件..."
    export $(grep -v '^#' .env | xargs)
    echo "✓ 环境变量已加载"
else
    echo "⚠️  .env 文件不存在"
    echo "   请复制 .env.example 为 .env 并填入你的配置："
    echo "   cp .env.example .env"
    echo "   nano .env"
fi
