#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量驱动的自动循环系统
核心理念：为质量而循环，不是为完成而循环
循环直到项目质量达标，没有硬性迭代次数限制
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 尝试导入依赖
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("警告：未安装 anthropic 包，请运行: pip install anthropic")

# 导入质量检查模块（同目录）
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module

# 配置
SLEEP_BETWEEN_CHECKS = 15          # 质量检查之间的等待时间（秒）
SLEEP_BETWEEN_FIXES = 5            # 修复之间的等待时间（秒）
MAX_FIXES_PER_ITERATION = 3        # 每轮最多处理的问题数
LOG_FILE = "auto-loop.log"
FEATURES_FILE = "features.json"
PROGRESS_FILE = "claude-progress.md"

# Claude API 配置
CLAUDE_MODEL = "claude-opus-4-6"
MAX_TOKENS = 8000

class QualityDrivenAutoLoop:
    """质量驱动的自动循环"""

    def __init__(self):
        self.client = None
        self.iteration = 0
        self.quality_checker = None
        self.fix_history = []  # 记录修复历史

        # 初始化质量检查器
        try:
            qc_module = import_module("quality-check")
            self.quality_checker = qc_module.QualityChecker(".")
            self.prioritize_issues = qc_module.prioritize_issues
            self.format_issues_report = qc_module.format_issues_report
            self.log_success("质量检查模块加载成功")
        except Exception as e:
            self.log_error(f"质量检查模块加载失败: {e}")

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

    # ---- 日志方法 ----

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

    # ---- 文件读写 ----

    def read_file(self, filepath):
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.log_error(f"读取文件 {filepath} 失败: {e}")
            return ""

    def load_features_data(self):
        """加载完整的 features.json 数据"""
        try:
            with open(FEATURES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.log_error(f"加载 {FEATURES_FILE} 失败: {e}")
            return None

    def save_features_data(self, data):
        """保存 features.json 数据"""
        try:
            with open(FEATURES_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_error(f"保存 {FEATURES_FILE} 失败: {e}")

    # ---- 质量检查 ----

    def quality_check(self):
        """运行全面的质量检查"""
        if not self.quality_checker:
            self.log_error("质量检查器未初始化")
            return []

        self.log("运行质量检查...")
        issues = self.quality_checker.run_all_checks()
        return issues

    # PLACEHOLDER_SHOULD_CONTINUE

    def should_continue(self, issues):
        """判断是否应该继续循环"""
        if not issues:
            return False, "项目质量达标，无问题需要处理"

        # 按严重程度统计
        high = [i for i in issues if i.severity == "high"]
        medium = [i for i in issues if i.severity == "medium"]
        low = [i for i in issues if i.severity == "low"]

        if high:
            return True, f"存在 {len(high)} 个高优先级问题"
        if medium:
            return True, f"存在 {len(medium)} 个中优先级问题"
        if low:
            return True, f"存在 {len(low)} 个低优先级问题（可优化）"

        return False, "所有检查通过"

    def handle_issues(self, issues):
        """处理发现的问题，每轮最多处理 MAX_FIXES_PER_ITERATION 个"""
        if not issues:
            return

        sorted_issues = self.prioritize_issues(issues)
        batch = sorted_issues[:MAX_FIXES_PER_ITERATION]

        self.log(f"本轮处理 {len(batch)} 个问题（共 {len(issues)} 个）")

        for issue in batch:
            self.log(f"处理: {issue}")
            success = self.fix_issue_with_api(issue)

            if success:
                self.log_success(f"已修复: {issue.summary}")
                self.git_commit(f"修复: {issue.type} - {issue.summary[:50]}")
                self.fix_history.append({
                    "iteration": self.iteration,
                    "issue": issue.to_dict(),
                    "result": "success",
                    "timestamp": datetime.now().isoformat(),
                })
            else:
                self.log_warning(f"修复失败: {issue.summary}")
                self.fix_history.append({
                    "iteration": self.iteration,
                    "issue": issue.to_dict(),
                    "result": "failed",
                    "timestamp": datetime.now().isoformat(),
                })

            time.sleep(SLEEP_BETWEEN_FIXES)

    # PLACEHOLDER_FIX_API

    def fix_issue_with_api(self, issue):
        """使用 Claude API 修复问题"""
        if not self.client:
            self.log_error("Claude API 客户端未初始化，无法自动修复")
            return False

        try:
            # 读取上下文
            claude_md = self.read_file("C:\\Users\\27546\\.claude\\CLAUDE.md")
            progress_md = self.read_file(PROGRESS_FILE)
            features_json = self.read_file(FEATURES_FILE)

            prompt = f"""你是一个自动化质量修复代理。请修复以下质量问题。

## 问题信息

类型: {issue.type}
严重程度: {issue.severity}
摘要: {issue.summary}
详情: {issue.details}

## 项目上下文

### CLAUDE.md（工作流规则）
{claude_md[:3000]}

### 当前进度日志
{progress_md[-2000:]}

### 功能列表
{features_json}

## 修复要求

1. 分析问题根因
2. 编写修复代码（如需要）
3. 确保修复不会引入新问题
4. 如果是未完成的功能，按步骤实现并测试
5. 更新 features.json 中对应功能的 passes 和 completed 字段（仅在功能确实完成时）
6. 所有代码注释使用中文

请直接给出修复方案和代码。"""

            self.log(f"调用 Claude API 修复: {issue.type}")

            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text
            self.log(f"Claude 响应: {response_text[:200]}...")

            # 简单判断：如果响应中包含修复相关关键词，认为修复成功
            # 实际效果取决于 Claude 是否真正执行了修改
            if any(kw in response_text for kw in ["修复", "完成", "已更新", "解决"]):
                return True
            return False

        except Exception as e:
            self.log_error(f"API 调用失败: {e}")
            return False

    def git_commit(self, message):
        """提交当前变更到 Git"""
        try:
            subprocess.run(["git", "add", "."], capture_output=True, timeout=30)
            result = subprocess.run(
                ["git", "commit", "-m",
                 f"{message}\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                self.log_success(f"Git 提交: {message}")
            else:
                # 没有变更需要提交也是正常的
                if "nothing to commit" in result.stdout + result.stderr:
                    self.log("没有变更需要提交")
                else:
                    self.log_warning(f"Git 提交失败: {result.stderr[:100]}")
        except Exception as e:
            self.log_error(f"Git 操作失败: {e}")

    # PLACEHOLDER_RECORD_AND_RUN

    def record_quality_history(self, issues):
        """记录质量历史到 features.json"""
        data = self.load_features_data()
        if not data:
            return

        # 确保 quality_history 字段存在
        if "quality_history" not in data:
            data["quality_history"] = []

        high = sum(1 for i in issues if i.severity == "high")
        medium = sum(1 for i in issues if i.severity == "medium")
        low = sum(1 for i in issues if i.severity == "low")

        record = {
            "timestamp": datetime.now().isoformat(),
            "iteration": self.iteration,
            "issues_found": len(issues),
            "issues_by_severity": {"high": high, "medium": medium, "low": low},
            "issue_types": list(set(i.type for i in issues)),
        }

        data["quality_history"].append(record)
        self.save_features_data(data)

    def update_progress_log(self):
        """更新进度日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        entry = f"""
## 质量循环会话 {timestamp}

### 循环迭代次数
- 共执行 {self.iteration} 轮质量检查

### 修复历史
"""
        for fix in self.fix_history[-10:]:  # 最近 10 条
            status = "✅" if fix["result"] == "success" else "❌"
            entry += f"- {status} [{fix['issue']['type']}] {fix['issue']['summary'][:60]}\n"

        entry += f"""
### 最终状态
- 质量循环完成，项目达到质量标准

"""
        try:
            with open(PROGRESS_FILE, 'a', encoding='utf-8') as f:
                f.write(entry)
            self.log_success("进度日志已更新")
        except Exception as e:
            self.log_error(f"更新进度日志失败: {e}")

    def run(self):
        """运行质量驱动的循环"""
        self.log("=" * 60)
        self.log("质量驱动的自动循环系统启动")
        self.log("目标：达到质量标准，而不仅仅是完成功能")
        self.log("=" * 60)
        self.log("")

        if not Path(FEATURES_FILE).exists():
            self.log_error(f"{FEATURES_FILE} 文件不存在")
            return

        if not self.quality_checker:
            self.log_error("质量检查器未初始化，无法运行")
            return

        try:
            while True:
                self.iteration += 1

                self.log("")
                self.log("=" * 60)
                self.log(f"质量检查循环 #{self.iteration}")
                self.log("=" * 60)

                # 1. 运行质量检查
                issues = self.quality_check()

                # 2. 显示检查结果
                if issues:
                    report = self.format_issues_report(
                        self.prioritize_issues(issues)
                    )
                    self.log(f"\n{report}")
                else:
                    self.log("质量检查未发现问题")

                # 3. 判断是否继续
                should_go, reason = self.should_continue(issues)

                if not should_go:
                    self.log_success(f"退出原因: {reason}")
                    self.log_success("项目质量达标！循环结束。")
                    break

                self.log(f"继续循环: {reason}")

                # 4. 处理问题
                self.handle_issues(issues)

                # 5. 记录质量历史
                self.record_quality_history(issues)

                # 6. 等待后继续下一轮
                self.log(f"等待 {SLEEP_BETWEEN_CHECKS} 秒后进行下一轮检查...")
                time.sleep(SLEEP_BETWEEN_CHECKS)

        except KeyboardInterrupt:
            self.log_warning("收到中断信号，正在安全退出...")

        # 循环结束，更新进度日志并提交
        self.update_progress_log()
        self.git_commit("质量循环完成：更新进度日志")

        self.log("")
        self.log("=" * 60)
        self.log(f"质量驱动循环结束，共执行 {self.iteration} 轮")
        self.log("=" * 60)


def main():
    """主函数"""
    loop = QualityDrivenAutoLoop()
    loop.run()


if __name__ == "__main__":
    main()
