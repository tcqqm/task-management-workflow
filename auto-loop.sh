#!/bin/bash
# 全自动任务执行循环脚本
# 用途：自动循环执行未完成的功能，直到所有功能完成

set -e  # 遇到错误立即退出

# 配置
MAX_ITERATIONS=100          # 最大循环次数（防止真正的无限循环）
SLEEP_BETWEEN_TASKS=5       # 任务之间的等待时间（秒）
LOG_FILE="auto-loop.log"    # 日志文件

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

# 检查是否有未完成的功能
has_pending_features() {
    if [ ! -f "features.json" ]; then
        log_error "features.json 文件不存在"
        return 1
    fi

    local pending_count=$(grep -c '"passes": false' features.json || echo "0")
    echo "$pending_count"
}

# 获取下一个未完成的功能 ID
get_next_feature() {
    grep -B 2 '"passes": false' features.json | grep '"id"' | head -1 | sed 's/.*"id": "\(.*\)".*/\1/'
}

# 主循环
main() {
    log "=========================================="
    log "全自动任务执行循环启动"
    log "=========================================="
    log ""

    # 检查必要文件
    if [ ! -f "features.json" ]; then
        log_error "features.json 文件不存在，请先初始化项目"
        exit 1
    fi

    local iteration=0

    while [ $iteration -lt $MAX_ITERATIONS ]; do
        iteration=$((iteration + 1))

        log "=========================================="
        log "循环迭代 #$iteration"
        log "=========================================="

        # 检查未完成的功能数量
        local pending_count=$(has_pending_features)

        if [ "$pending_count" -eq 0 ]; then
            log_success "所有功能已完成！"
            log_success "项目完成，退出循环"
            break
        fi

        log "剩余未完成功能：$pending_count 个"

        # 获取下一个功能
        local next_feature=$(get_next_feature)

        if [ -z "$next_feature" ]; then
            log_error "无法获取下一个功能 ID"
            exit 1
        fi

        log "准备执行功能：$next_feature"
        log ""

        # 显示当前状态
        log "--- 当前项目状态 ---"
        bash status.sh | tee -a "$LOG_FILE"
        log ""

        # 这里是关键：调用 Claude 执行任务
        # 方式 1：使用 Claude Code CLI（如果可用）
        # 方式 2：使用 Claude API
        # 方式 3：提示用户手动执行

        log_warning "请在另一个终端执行以下命令："
        log_warning "  claude code '实现 $next_feature 功能'"
        log_warning ""
        log_warning "或者按 Ctrl+C 退出自动循环"
        log ""

        # 等待用户确认或自动继续
        read -t 30 -p "按 Enter 继续，或等待 30 秒自动继续..." || true

        log ""
        log "等待 $SLEEP_BETWEEN_TASKS 秒后继续..."
        sleep $SLEEP_BETWEEN_TASKS

    done

    if [ $iteration -ge $MAX_ITERATIONS ]; then
        log_warning "达到最大循环次数 ($MAX_ITERATIONS)，退出循环"
    fi

    log ""
    log "=========================================="
    log "自动循环结束"
    log "=========================================="
    log ""

    # 显示最终统计
    log "--- 最终项目状态 ---"
    bash status.sh | tee -a "$LOG_FILE"
}

# 捕获 Ctrl+C
trap 'log_warning "收到中断信号，正在退出..."; exit 130' INT

# 运行主函数
main
