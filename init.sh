#!/bin/bash
# 项目启动脚本
# 用途：快速启动开发环境

echo "=== 任务管理工作流系统 ==="
echo ""

# 检查是否在正确的目录
if [ ! -f "features.json" ]; then
    echo "错误：未找到 features.json 文件"
    echo "请确保在项目根目录运行此脚本"
    exit 1
fi

echo "✅ 项目文件检查通过"
echo ""

# 显示项目状态
echo "--- 项目状态 ---"
if [ -f "claude-progress.md" ]; then
    echo "📝 进度日志：存在"
else
    echo "⚠️  进度日志：缺失"
fi

if [ -f "features.json" ]; then
    echo "📋 功能列表：存在"
else
    echo "⚠️  功能列表：缺失"
fi

echo ""
echo "--- 功能统计 ---"
# 统计功能数量（简单计数）
total=$(grep -c '"id":' features.json)
completed=$(grep -c '"passes": true' features.json)
pending=$((total - completed))

echo "总功能数：$total"
echo "已完成：$completed"
echo "待完成：$pending"

echo ""
echo "=== 启动完成 ==="
echo ""
echo "提示："
echo "- 查看功能列表：cat features.json"
echo "- 查看进度日志：cat claude-progress.md"
echo "- 查看 Git 历史：git log --oneline -10"
