#!/bin/bash
# 功能状态查询脚本
# 用途：快速查看未完成的功能列表和完成进度

echo "=== 功能状态查询 ==="
echo ""

# 检查 features.json 是否存在
if [ ! -f "features.json" ]; then
    echo "错误：未找到 features.json 文件"
    exit 1
fi

# 统计功能数量
total=$(grep -c '"id":' features.json)
completed=$(grep -c '"passes": true' features.json)
pending=$((total - completed))

echo "📊 功能统计"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "总功能数：$total"
echo "已完成：$completed"
echo "待完成：$pending"

if [ $total -gt 0 ]; then
    percentage=$((completed * 100 / total))
    echo "完成率：$percentage%"
fi

echo ""
echo "📋 未完成的功能"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 提取未完成的功能（简化版本）
awk '
    /"id":/ { id = $0; gsub(/.*"id": "|".*/, "", id) }
    /"description":/ { desc = $0; gsub(/.*"description": "|".*/, "", desc) }
    /"passes": false/ { print "- " id ": " desc }
' features.json

echo ""
echo "✅ 已完成的功能"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 提取已完成的功能
awk '
    /"id":/ { id = $0; gsub(/.*"id": "|".*/, "", id) }
    /"description":/ { desc = $0; gsub(/.*"description": "|".*/, "", desc) }
    /"passes": true/ { print "- " id ": " desc }
' features.json

echo ""
echo "提示：使用 'cat features.json' 查看完整的功能列表"
