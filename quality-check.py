#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量检查模块
提供多维度的项目质量检查功能：测试、代码质量、性能、安全
"""

import json
import os
import subprocess
import re
from datetime import datetime
from pathlib import Path


# 严重程度常量
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"

# 问题类型常量
TYPE_TEST_FAILURE = "test_failure"
TYPE_CODE_QUALITY = "code_quality"
TYPE_E2E_FAILURE = "e2e_failure"
TYPE_PERFORMANCE = "performance"
TYPE_SECURITY = "security"
TYPE_FEATURE_INCOMPLETE = "feature_incomplete"


class QualityIssue:
    """质量问题数据类"""

    def __init__(self, issue_type, severity, summary, details=""):
        self.type = issue_type
        self.severity = severity
        self.summary = summary
        self.details = details
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "type": self.type,
            "severity": self.severity,
            "summary": self.summary,
            "details": self.details,
            "timestamp": self.timestamp,
        }

    def __repr__(self):
        return f"[{self.severity}] {self.type}: {self.summary}"


class QualityChecker:
    """多维度质量检查器"""

    def __init__(self, project_dir="."):
        self.project_dir = Path(project_dir).resolve()
        self.features_file = self.project_dir / "features.json"
        self.quality_standards = self._load_quality_standards()

    def _load_quality_standards(self):
        """从 features.json 加载质量标准配置"""
        try:
            with open(self.features_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("quality_standards", {
                    "max_line_length": 120,
                    "max_file_lines": 500,
                    "security_checks": [
                        "no_hardcoded_secrets",
                        "input_validation",
                    ],
                })
        except Exception:
            return {}

    def run_all_checks(self):
        """运行所有质量检查，返回问题列表"""
        issues = []
        issues.extend(self.check_features_complete())
        issues.extend(self.check_tests())
        issues.extend(self.check_code_quality())
        issues.extend(self.check_security())
        return issues

    # ---- 功能完成度检查 ----

    def check_features_complete(self):
        """检查是否有未完成的功能"""
        issues = []
        try:
            with open(self.features_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            features = data.get("features", [])
            for feat in features:
                if not feat.get("passes", False):
                    issues.append(QualityIssue(
                        TYPE_FEATURE_INCOMPLETE,
                        SEVERITY_HIGH,
                        f"功能未完成: {feat['id']} - {feat['description']}",
                        json.dumps(feat, ensure_ascii=False),
                    ))
        except Exception as e:
            issues.append(QualityIssue(
                TYPE_FEATURE_INCOMPLETE,
                SEVERITY_HIGH,
                f"无法读取功能列表: {e}",
            ))
        return issues

    # ---- 测试检查 ----

    def check_tests(self):
        """运行项目测试并收集失败信息"""
        issues = []
        # 检测项目类型并运行对应测试
        if (self.project_dir / "package.json").exists():
            issues.extend(self._run_npm_tests())
        if (self.project_dir / "pytest.ini").exists() or \
           (self.project_dir / "setup.py").exists() or \
           (self.project_dir / "pyproject.toml").exists():
            issues.extend(self._run_pytest())
        # 运行自定义测试脚本
        test_runner = self.project_dir / "test-runner.sh"
        if test_runner.exists():
            issues.extend(self._run_shell_tests(test_runner))
        return issues

    def _run_npm_tests(self):
        """运行 npm test"""
        issues = []
        try:
            result = subprocess.run(
                ["npm", "test", "--", "--run"],
                cwd=str(self.project_dir),
                capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=120,
            )
            if result.returncode != 0:
                issues.append(QualityIssue(
                    TYPE_TEST_FAILURE, SEVERITY_HIGH,
                    "npm 测试失败",
                    result.stdout + "\n" + result.stderr,
                ))
        except FileNotFoundError:
            pass  # npm 不可用，跳过
        except subprocess.TimeoutExpired:
            issues.append(QualityIssue(
                TYPE_TEST_FAILURE, SEVERITY_MEDIUM,
                "npm 测试超时（120秒）",
            ))
        return issues

    def _run_pytest(self):
        """运行 pytest"""
        issues = []
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=short", "-q"],
                cwd=str(self.project_dir),
                capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=120,
            )
            if result.returncode != 0:
                issues.append(QualityIssue(
                    TYPE_TEST_FAILURE, SEVERITY_HIGH,
                    "pytest 测试失败",
                    result.stdout + "\n" + result.stderr,
                ))
        except FileNotFoundError:
            pass
        except subprocess.TimeoutExpired:
            issues.append(QualityIssue(
                TYPE_TEST_FAILURE, SEVERITY_MEDIUM,
                "pytest 测试超时（120秒）",
            ))
        return issues

    def _run_shell_tests(self, script_path):
        """运行 shell 测试脚本"""
        issues = []
        try:
            result = subprocess.run(
                ["bash", str(script_path)],
                cwd=str(self.project_dir),
                capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=120,
            )
            if result.returncode != 0:
                issues.append(QualityIssue(
                    TYPE_TEST_FAILURE, SEVERITY_HIGH,
                    "测试脚本执行失败",
                    result.stdout + "\n" + result.stderr,
                ))
        except subprocess.TimeoutExpired:
            issues.append(QualityIssue(
                TYPE_TEST_FAILURE, SEVERITY_MEDIUM,
                "测试脚本超时（120秒）",
            ))
        return issues

    # ---- 代码质量检查 ----

    def check_code_quality(self):
        """检查代码质量：行长度、文件大小、语法问题"""
        issues = []
        max_line = self.quality_standards.get("max_line_length", 120)
        max_file = self.quality_standards.get("max_file_lines", 500)

        # 扫描项目中的源代码文件
        extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".sh"}
        for filepath in self.project_dir.rglob("*"):
            if filepath.suffix not in extensions:
                continue
            # 跳过隐藏目录和 node_modules
            parts = filepath.relative_to(self.project_dir).parts
            if any(p.startswith(".") or p == "node_modules" for p in parts):
                continue

            try:
                lines = filepath.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue

            rel = str(filepath.relative_to(self.project_dir))

            # 检查文件行数
            if len(lines) > max_file:
                issues.append(QualityIssue(
                    TYPE_CODE_QUALITY, SEVERITY_LOW,
                    f"文件过长: {rel} ({len(lines)} 行，上限 {max_file})",
                ))

            # 检查超长行
            long_lines = []
            for i, line in enumerate(lines, 1):
                if len(line) > max_line:
                    long_lines.append(i)
            if long_lines:
                sample = long_lines[:5]
                issues.append(QualityIssue(
                    TYPE_CODE_QUALITY, SEVERITY_LOW,
                    f"超长行: {rel} 第 {sample} 行（上限 {max_line} 字符）",
                ))

            # Python 文件额外检查：语法
            if filepath.suffix == ".py":
                issues.extend(self._check_python_syntax(filepath, rel))

        return issues

    def _check_python_syntax(self, filepath, rel_path):
        """检查 Python 文件语法"""
        issues = []
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", str(filepath)],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=10,
            )
            if result.returncode != 0:
                issues.append(QualityIssue(
                    TYPE_CODE_QUALITY, SEVERITY_HIGH,
                    f"Python 语法错误: {rel_path}",
                    result.stderr,
                ))
        except Exception:
            pass
        return issues

    # ---- 安全检查 ----

    def check_security(self):
        """检查常见安全问题"""
        issues = []
        checks = self.quality_standards.get("security_checks", [])

        extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".sh", ".env"}
        for filepath in self.project_dir.rglob("*"):
            if filepath.suffix not in extensions:
                continue
            parts = filepath.relative_to(self.project_dir).parts
            if any(p.startswith(".") or p == "node_modules" for p in parts):
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
            except Exception:
                continue

            rel = str(filepath.relative_to(self.project_dir))

            # 检查硬编码密钥/密码
            if "no_hardcoded_secrets" in checks:
                secret_patterns = [
                    (r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
                     "硬编码密码"),
                    (r'(?i)(api_key|apikey|secret_key|secret)\s*=\s*["\'][A-Za-z0-9]{16,}["\']',
                     "硬编码密钥"),
                    (r'(?i)(token)\s*=\s*["\'][A-Za-z0-9_\-]{20,}["\']',
                     "硬编码 Token"),
                ]
                for pattern, desc in secret_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        issues.append(QualityIssue(
                            TYPE_SECURITY, SEVERITY_HIGH,
                            f"{desc}: {rel}",
                            f"匹配到 {len(matches)} 处可疑内容",
                        ))

        return issues


# ---- 工具函数 ----

def prioritize_issues(issues):
    """按严重程度排序问题列表（高 → 中 → 低）"""
    order = {SEVERITY_HIGH: 0, SEVERITY_MEDIUM: 1, SEVERITY_LOW: 2}
    return sorted(issues, key=lambda x: order.get(x.severity, 99))


def format_issues_report(issues):
    """格式化问题报告为可读字符串"""
    if not issues:
        return "没有发现质量问题。"

    lines = [f"发现 {len(issues)} 个质量问题：", ""]
    for i, issue in enumerate(issues, 1):
        lines.append(f"  {i}. [{issue.severity}] {issue.type}")
        lines.append(f"     {issue.summary}")
        if issue.details:
            detail_preview = issue.details[:200]
            if len(issue.details) > 200:
                detail_preview += "..."
            lines.append(f"     详情: {detail_preview}")
        lines.append("")
    return "\n".join(lines)


# ---- 独立运行入口 ----

if __name__ == "__main__":
    import sys
    import io

    # 修复 Windows 终端 UTF-8 输出
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    project = sys.argv[1] if len(sys.argv) > 1 else "."
    checker = QualityChecker(project)

    print("=" * 60)
    print("项目质量检查")
    print("=" * 60)
    print()

    all_issues = checker.run_all_checks()
    sorted_issues = prioritize_issues(all_issues)
    print(format_issues_report(sorted_issues))

    if all_issues:
        print(f"总计: {len(all_issues)} 个问题")
        high = sum(1 for i in all_issues if i.severity == SEVERITY_HIGH)
        med = sum(1 for i in all_issues if i.severity == SEVERITY_MEDIUM)
        low = sum(1 for i in all_issues if i.severity == SEVERITY_LOW)
        print(f"  高: {high}  中: {med}  低: {low}")
        sys.exit(1)
    else:
        print("项目质量检查全部通过！")
        sys.exit(0)
