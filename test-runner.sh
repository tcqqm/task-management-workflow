#!/bin/bash
# 测试运行脚本
# 用途：运行项目中所有测试并生成报告
# 退出码：0 = 全部通过，1 = 有失败

set -o pipefail

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
REPORT=""

log() { echo -e "${BLUE}[测试]${NC} $1"; }
pass() { echo -e "${GREEN}[通过]${NC} $1"; PASS_COUNT=$((PASS_COUNT + 1)); REPORT+="✅ $1\n"; }
fail() { echo -e "${RED}[失败]${NC} $1"; FAIL_COUNT=$((FAIL_COUNT + 1)); REPORT+="❌ $1\n"; }
skip() { echo -e "${YELLOW}[跳过]${NC} $1"; SKIP_COUNT=$((SKIP_COUNT + 1)); REPORT+="⏭️ $1\n"; }

echo "============================================"
echo "  项目测试运行器"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"
echo ""

# 1. 检查核心文件是否存在
log "检查核心文件..."
for f in features.json claude-progress.md init.sh; do
    if [ -f "$f" ]; then
        pass "文件存在: $f"
    else
        fail "文件缺失: $f"
    fi
done

# 2. 检查 features.json 格式
log "检查 features.json 格式..."
if python -c "import json; json.load(open('features.json', encoding='utf-8'))" 2>/dev/null; then
    pass "features.json 是有效的 JSON"
else
    fail "features.json JSON 格式错误"
fi

# 3. 检查 Python 文件语法
log "检查 Python 文件语法..."
for pyfile in *.py; do
    if [ -f "$pyfile" ]; then
        if python -m py_compile "$pyfile" 2>/dev/null; then
            pass "Python 语法正确: $pyfile"
        else
            fail "Python 语法错误: $pyfile"
        fi
    fi
done

# 4. 检查 Shell 脚本语法
log "检查 Shell 脚本语法..."
for shfile in *.sh; do
    if [ -f "$shfile" ]; then
        if bash -n "$shfile" 2>/dev/null; then
            pass "Shell 语法正确: $shfile"
        else
            fail "Shell 语法错误: $shfile"
        fi
    fi
done

# 5. 运行 pytest（如果存在）
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    log "运行 pytest..."
    if python -m pytest --tb=short -q 2>/dev/null; then
        pass "pytest 测试通过"
    else
        fail "pytest 测试失败"
    fi
else
    skip "pytest（未检测到测试配置）"
fi

# 6. 运行 npm test（如果存在）
if [ -f "package.json" ]; then
    log "运行 npm test..."
    if npm test --run 2>/dev/null; then
        pass "npm 测试通过"
    else
        fail "npm 测试失败"
    fi
else
    skip "npm test（未检测到 package.json）"
fi

# 7. 检查 Git 状态
log "检查 Git 状态..."
if git status >/dev/null 2>&1; then
    pass "Git 仓库正常"
    # 检查是否有未提交的变更
    if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
        pass "工作区干净，无未提交变更"
    else
        fail "存在未提交的变更"
    fi
else
    skip "Git 检查（非 Git 仓库）"
fi

# 输出报告
echo ""
echo "============================================"
echo "  测试报告"
echo "============================================"
echo -e "$REPORT"
echo "--------------------------------------------"
TOTAL=$((PASS_COUNT + FAIL_COUNT + SKIP_COUNT))
echo -e "总计: $TOTAL  ${GREEN}通过: $PASS_COUNT${NC}  ${RED}失败: $FAIL_COUNT${NC}  ${YELLOW}跳过: $SKIP_COUNT${NC}"
echo "============================================"

# 退出码
if [ $FAIL_COUNT -gt 0 ]; then
    exit 1
else
    exit 0
fi
