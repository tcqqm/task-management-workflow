#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全自动化的任务执行循环（使用 Claude API）
真正的无限循环，直到所有功能完成
"""

import json
import os
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 尝试导入 anthropic
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("警告：未安装 anthropic 包，请运行: pip install anthropic")

# 配置
MAX_ITERATIONS = 100
SLEEP_BETWEEN_TASKS = 10
LOG_FILE = "auto-loop.log"
FEATURES_FILE = "features.json"
PROGRESS_FILE = "claude-progress.md"

# Claude API 配置
CLAUDE_MODEL = "claude-opus-4-6"
MAX_TOKENS = 8000


class AutoLoop:
    """自动循环执行器"""

    def __init__(self):
        self.client = None
        self.iteration = 0

        # 初始化 Claude API 客户端
        if HAS_ANTHROPIC:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.log_success("Claude API 客户端初始化成功")
            else:
                self.log_warning("未设置 ANTHROPIC_API_KEY 环境变量")
        else:
            self.log_warning("未安装 anthropic 包")

    def log(self, message, prefix="ℹ️"):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {prefix} {message}"
        print(log_message)

        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')

    def log_success(self, message):
        self.log(message, "✅")

    def log_error(self, message):
        self.log(message, "❌")

    def log_warning(self, message):
        self.log(message, "⚠️")

    def load_features(self):
        """加载功能列表"""
        try:
            with open(FEATURES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('features', [])
        except Exception as e:
            self.log_error(f"加载功能列表失败: {str(e)}")
            return None

    def get_pending_features(self, features):
        """获取未完成的功能"""
        return [f for f in features if not f.get('passes', False)]

    def read_file(self, filepath):
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.log_error(f"读取文件 {filepath} 失败: {str(e)}")
            return ""

    def execute_feature_with_api(self, feature):
        """使用 Claude API 执行功能"""
        if not self.client:
            self.log_error("Claude API 客户端未初始化")
            return False

        try:
            # 读取上下文文件
            claude_md = self.read_file("C:\\Users\\27546\\.claude\\CLAUDE.md")
            progress_md = self.read_file(PROGRESS_FILE)
            features_json = self.read_file(FEATURES_FILE)

            # 构建提示
            prompt = f"""
你是一个自动化任务执行代理。请严格按照 CLAUDE.md 中的工作流执行以下功能。

## 当前功能

ID: {feature['id']}
类别: {feature['category']}
描述: {feature['description']}

验证步骤:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(feature['steps']))}

## 上下文信息

### CLAUDE.md（工作流规则）
{claude_md}

### 当前进度日志
{progress_md}

### 当前功能列表
{features_json}

## 执行要求

请按照以下步骤执行：

1. **实现功能**
   - 编写必要的代码
   - 添加中文注释
   - 保持代码整洁

2. **测试功能**
   - 执行所有验证步骤
   - 确保功能正常工作
   - 记录测试结果

3. **更新状态**
   - 只修改 features.json 中该功能的 passes 和 completed 字段
   - 设置 "passes": true
   - 设置 "completed": "{datetime.now().isoformat()}"

4. **提交到 Git**
   - 使用描述性的提交消息
   - 包含 Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

5. **更新进度日志**
   - 在 claude-progress.md 中添加新的会话记录
   - 记录完成的功能、变更、测试结果

请开始执行，并在完成后报告结果。
"""

            self.log(f"调用 Claude API 执行功能: {feature['id']}")

            # 调用 Claude API
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # 获取响应
            response_text = response.content[0].text
            self.log(f"Claude 响应: {response_text[:200]}...")

            # 检查功能是否完成
            # 重新加载 features.json 检查状态
            time.sleep(2)  # 等待文件更新
            updated_features = self.load_features()
            if updated_features:
                updated_feature = next(
                    (f for f in updated_features if f['id'] == feature['id']),
                    None
                )
                if updated_feature and updated_feature.get('passes', False):
                    self.log_success(f"功能 {feature['id']} 执行成功")
                    return True

            self.log_warning(f"功能 {feature['id']} 可能未完全完成")
            return False

        except Exception as e:
            self.log_error(f"执行功能时出错: {str(e)}")
            return False

    def run(self):
        """运行自动循环"""
        self.log("=" * 60)
        self.log("完全自动化任务执行循环启动")
        self.log("=" * 60)
        self.log("")

        if not Path(FEATURES_FILE).exists():
            self.log_error(f"{FEATURES_FILE} 文件不存在")
            return

        try:
            while self.iteration < MAX_ITERATIONS:
                self.iteration += 1

                self.log("=" * 60)
                self.log(f"循环迭代 #{self.iteration}")
                self.log("=" * 60)

                # 加载功能列表
                features = self.load_features()
                if not features:
                    self.log_error("无法加载功能列表")
                    break

                # 获取未完成的功能
                pending = self.get_pending_features(features)

                if not pending:
                    self.log_success("🎉 所有功能已完成！")
                    self.log_success("项目完成，退出循环")
                    break

                self.log(f"剩余未完成功能: {len(pending)} 个")

                # 执行下一个功能
                next_feature = pending[0]
                self.log(f"执行功能: {next_feature['id']}")
                self.log(f"描述: {next_feature['description']}")
                self.log("")

                # 使用 API 执行
                if self.client:
                    success = self.execute_feature_with_api(next_feature)
                    if not success:
                        self.log_warning("功能执行失败，继续下一个")
                else:
                    self.log_error("无法执行功能：API 客户端未初始化")
                    self.log_warning("请设置 ANTHROPIC_API_KEY 环境变量")
                    break

                # 等待
                self.log(f"等待 {SLEEP_BETWEEN_TASKS} 秒...")
                time.sleep(SLEEP_BETWEEN_TASKS)

            if self.iteration >= MAX_ITERATIONS:
                self.log_warning(f"达到最大循环次数 ({MAX_ITERATIONS})")

        except KeyboardInterrupt:
            self.log_warning("收到中断信号，正在退出...")

        self.log("")
        self.log("=" * 60)
        self.log("自动循环结束")
        self.log("=" * 60)


def main():
    """主函数"""
    loop = AutoLoop()
    loop.run()


if __name__ == "__main__":
    main()
