# 质量驱动的自动循环系统指南

本文档说明如何使用质量驱动的自动循环系统。

## 核心理念

**为质量而循环，不是为完成而循环。**

旧模式：功能未完成 → 实现功能 → 标记完成 → 下一个功能
新模式：运行质量检查 → 发现问题 → 修复/优化 → 再次检查 → 循环直到质量达标

| 维度 | 旧模式 | 新模式 |
|------|--------|--------|
| 目标 | 完成所有功能 | 达到质量标准 |
| 循环条件 | 有未完成功能 | 有问题或可优化 |
| 退出条件 | 所有功能完成 | 测试全通过且无优化空间 |
| 迭代次数 | 固定上限（100次） | 无上限，直到质量达标 |
| 关注点 | 功能数量 | 代码质量 |

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `auto-loop-full.py` | 质量驱动的主循环（使用 Claude API） |
| `quality-check.py` | 多维度质量检查模块 |
| `test-runner.sh` | 测试运行脚本 |
| `auto-loop.py` | 半自动模式（Python） |
| `auto-loop.sh` | 半自动模式（Bash） |
| `features.json` | 功能列表 + 质量标准 + 质量历史 |

---

## 快速开始

### 1. 安装依赖

```bash
pip install anthropic
```

### 2. 设置 API 密钥

```bash
# Windows
set ANTHROPIC_API_KEY=your_api_key_here

# Linux/Mac
export ANTHROPIC_API_KEY=your_api_key_here
```

### 3. 运行质量循环

```bash
python auto-loop-full.py
```

### 4. 单独运行质量检查（不修复）

```bash
python quality-check.py
```

### 5. 运行测试

```bash
bash test-runner.sh
```

---

## 质量检查维度

系统会从以下维度检查项目质量：

### 功能完成度（高优先级）
- 检查 `features.json` 中是否有 `passes: false` 的功能
- 未完成的功能会被优先处理

### 测试（高优先级）
- 自动检测项目类型（npm / pytest / shell 脚本）
- 运行对应的测试命令
- 收集失败信息

### 代码质量（低-高优先级）
- Python 语法检查
- 文件行数检查（默认上限 500 行）
- 行长度检查（默认上限 120 字符）

### 安全检查（高优先级）
- 硬编码密码检测
- 硬编码 API 密钥检测
- 硬编码 Token 检测

---

## 质量标准配置

在 `features.json` 中配置质量标准：

```json
{
  "quality_standards": {
    "max_line_length": 120,
    "max_file_lines": 500,
    "security_checks": [
      "no_hardcoded_secrets",
      "input_validation"
    ]
  }
}
```

---

## 循环工作流

```
启动 → 质量检查 → 有问题？
                    ├─ 是 → 按优先级排序 → 修复最严重的问题 → 提交 → 等待 → 回到质量检查
                    └─ 否 → 更新进度日志 → 提交 → 结束
```

每轮最多处理 3 个问题（`MAX_FIXES_PER_ITERATION`），避免单轮修复过多导致混乱。

---

## 配置参数

在 `auto-loop-full.py` 开头修改：

```python
SLEEP_BETWEEN_CHECKS = 15    # 质量检查之间的等待时间（秒）
SLEEP_BETWEEN_FIXES = 5      # 修复之间的等待时间（秒）
MAX_FIXES_PER_ITERATION = 3  # 每轮最多处理的问题数
CLAUDE_MODEL = "claude-opus-4-6"  # Claude 模型
MAX_TOKENS = 8000                  # 最大 token 数
```

---

## 安全机制

- **Ctrl+C 安全退出**：随时可中断，退出前会更新进度日志并提交
- **增量提交**：每次修复后立即 git commit，避免丢失进度
- **详细日志**：所有操作记录到 `auto-loop.log`
- **质量历史**：每轮检查结果记录到 `features.json` 的 `quality_history`

---

## 监控

```bash
# 实时查看日志
tail -f auto-loop.log

# 查看质量历史
python -c "import json; d=json.load(open('features.json')); [print(h) for h in d.get('quality_history',[])]"

# 查看最近提交
git log --oneline -10
```

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| API 密钥无效 | 检查 `ANTHROPIC_API_KEY` 环境变量 |
| 质量检查模块加载失败 | 确保 `quality-check.py` 与 `auto-loop-full.py` 在同一目录 |
| 循环不退出 | 检查是否有持续产生的问题；按 Ctrl+C 中断 |
| 修复无效 | Claude API 返回的是建议而非直接执行，需要配合 Claude Code CLI |
