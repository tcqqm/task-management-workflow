#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全自动任务执行循环脚本（Python 版本）
使用 Claude API 自动执行未完成的功能
"""

import json
import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
MAX_ITERATIONS = 100  # 最大循环次数
SLEEP_BETWEEN_TASKS = 5  # 任务之间的等待时间（秒）
LOG_FILE = "auto-loop.log"
FEATURES_FILE = "features.json"

# 颜色代码
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def log(message, color=Colors.BLUE):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{color}[{timestamp}]{Colors.NC} {message}"
    print(log_message)

    # 写入日志文件（去除颜色代码）
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        clean_message = f"[{timestamp}] {message}\n"
        f.write(clean_message)


def log_success(message):
    """成功日志"""
    log(f"✅ {message}", Colors.GREEN)


def log_error(message):
    """错误日志"""
    log(f"❌ {message}", Colors.RED)


def log_warning(message):
    """警告日志"""
    log(f"⚠️  {message}", Colors.YELLOW)


def load_features():
    """加载功能列表"""
    try:
        with open(FEATURES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('features', [])
    except FileNotFoundError:
        log_error(f"{FEATURES_FILE} 文件不存在")
        return None
    except json.JSONDecodeError:
        log_error(f"{FEATURES_FILE} 不是有效的 JSON 文件")
        return None


def get_pending_features(features):
    """获取未完成的功能列表"""
    return [f for f in features if not f.get('passes', False)]


def execute_feature_with_api(feature):
    """
    使用 Claude API 执行功能

    注意：这需要配置 ANTHROPIC_API_KEY 环境变量
    """
    try:
        # 这里需要实现 Claude API 调用
        # 示例代码（需要安装 anthropic 包）:

        # import anthropic
        # client = anthropic.Anthropic()
        #
        # prompt = f"""
        # 请实现以下功能：
        #
        # ID: {feature['id']}
        # 描述: {feature['description']}
        # 步骤:
        # {chr(10).join(f"- {step}" for step in feature['steps'])}
        #
        # 请按照 CLAUDE.md 中的工作流执行：
        # 1. 实现功能
        # 2. 测试功能
        # 3. 更新 features.json 标记完成
        # 4. 提交到 Git
        # 5. 更新进度日志
        # """
        #
        # response = client.messages.create(
        #     model="claude-opus-4-6",
        #     max_tokens=8000,
        #     messages=[{"role": "user", "content": prompt}]
        # )

        log_warning("Claude API 调用功能尚未实现")
        log_warning("请手动执行功能或配置 API")
        return False

    except Exception as e:
        log_error(f"执行功能时出错: {str(e)}")
        return False


def execute_feature_with_cli(feature):
    """
    使用 Claude Code CLI 执行功能
    """
    try:
        prompt = f"实现 {feature['id']} 功能：{feature['description']}"

        log(f"调用 Claude Code CLI: {prompt}")

        # 调用 Claude Code CLI
        # 注意：这需要 Claude Code CLI 已安装并配置
        result = subprocess.run(
            ['claude', 'code', prompt],
            capture_output=True,
            text=True,
            timeout=600  # 10 分钟超时
        )

        if result.returncode == 0:
            log_success("功能执行成功")
            return True
        else:
            log_error(f"功能执行失败: {result.stderr}")
            return False

    except FileNotFoundError:
        log_error("Claude Code CLI 未找到，请先安装")
        return False
    except subprocess.TimeoutExpired:
        log_error("功能执行超时")
        return False
    except Exception as e:
        log_error(f"执行功能时出错: {str(e)}")
        return False


def run_status_script():
    """运行状态查询脚本"""
    try:
        result = subprocess.run(
            ['bash', 'status.sh'],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        log_error(f"运行 status.sh 失败: {str(e)}")


def main():
    """主函数"""
    log("=" * 50)
    log("全自动任务执行循环启动（Python 版本）")
    log("=" * 50)
    log("")

    # 检查必要文件
    if not Path(FEATURES_FILE).exists():
        log_error(f"{FEATURES_FILE} 文件不存在，请先初始化项目")
        sys.exit(1)

    iteration = 0

    try:
        while iteration < MAX_ITERATIONS:
            iteration += 1

            log("=" * 50)
            log(f"循环迭代 #{iteration}")
            log("=" * 50)

            # 加载功能列表
            features = load_features()
            if features is None:
                log_error("无法加载功能列表")
                sys.exit(1)

            # 获取未完成的功能
            pending_features = get_pending_features(features)

            if not pending_features:
                log_success("所有功能已完成！")
                log_success("项目完成，退出循环")
                break

            log(f"剩余未完成功能：{len(pending_features)} 个")

            # 获取下一个功能
            next_feature = pending_features[0]
            log(f"准备执行功能：{next_feature['id']}")
            log(f"描述：{next_feature['description']}")
            log("")

            # 显示当前状态
            log("--- 当前项目状态 ---")
            run_status_script()
            log("")

            # 执行功能
            # 方式 1：使用 Claude API（需要配置）
            # success = execute_feature_with_api(next_feature)

            # 方式 2：使用 Claude Code CLI（需要安装）
            # success = execute_feature_with_cli(next_feature)

            # 方式 3：手动模式（提示用户）
            log_warning("自动执行模式：")
            log_warning("1. 使用 Claude API（需要配置 ANTHROPIC_API_KEY）")
            log_warning("2. 使用 Claude Code CLI（需要安装 claude-code）")
            log_warning("3. 手动模式（当前）")
            log_warning("")
            log_warning(f"请手动执行功能：{next_feature['id']}")
            log_warning("完成后按 Enter 继续...")

            try:
                input()
            except KeyboardInterrupt:
                log_warning("收到中断信号")
                break

            log("")
            log(f"等待 {SLEEP_BETWEEN_TASKS} 秒后继续...")
            time.sleep(SLEEP_BETWEEN_TASKS)

        if iteration >= MAX_ITERATIONS:
            log_warning(f"达到最大循环次数 ({MAX_ITERATIONS})，退出循环")

    except KeyboardInterrupt:
        log_warning("收到中断信号，正在退出...")
        sys.exit(130)

    log("")
    log("=" * 50)
    log("自动循环结束")
    log("=" * 50)
    log("")

    # 显示最终统计
    log("--- 最终项目状态 ---")
    run_status_script()


if __name__ == "__main__":
    main()
