# 全自动循环执行指南

本文档说明如何使用全自动循环脚本，实现真正的"无限循环"执行任务。

## 三种实现方式

### 1. 半自动模式（Bash）

**文件：** `auto-loop.sh`

**特点：**
- 自动检测未完成的功能
- 提示用户手动执行
- 适合需要人工监督的场景

**使用方法：**
```bash
bash auto-loop.sh
```

**工作流程：**
1. 检查 features.json 中的未完成功能
2. 显示下一个要执行的功能
3. 提示用户在另一个终端执行
4. 等待用户确认后继续
5. 重复直到所有功能完成

---

### 2. 半自动模式（Python）

**文件：** `auto-loop.py`

**特点：**
- Python 实现，更易扩展
- 支持多种执行模式
- 更好的错误处理

**使用方法：**
```bash
python auto-loop.py
```

**工作流程：**
与 Bash 版本类似，但提供更好的日志和错误处理。

---

### 3. 完全自动模式（Claude API）

**文件：** `auto-loop-full.py`

**特点：**
- 真正的无人值守自动执行
- 使用 Claude API 自动完成任务
- 适合长时间运行的大型项目

**前置要求：**
1. 安装 anthropic 包：
   ```bash
   pip install anthropic
   ```

2. 设置 API 密钥：
   ```bash
   # Windows
   set ANTHROPIC_API_KEY=your_api_key_here

   # Linux/Mac
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

**使用方法：**
```bash
python auto-loop-full.py
```

**工作流程：**
1. 读取 features.json 中的未完成功能
2. 读取 CLAUDE.md 工作流规则
3. 读取 claude-progress.md 进度日志
4. 构建完整的上下文提示
5. 调用 Claude API 执行功能
6. 验证功能是否完成
7. 等待一段时间后继续下一个功能
8. 重复直到所有功能完成

---

## 配置选项

### 修改循环参数

在脚本开头可以修改以下参数：

```python
MAX_ITERATIONS = 100          # 最大循环次数（防止真正的无限循环）
SLEEP_BETWEEN_TASKS = 10      # 任务之间的等待时间（秒）
LOG_FILE = "auto-loop.log"    # 日志文件路径
```

### 修改 Claude 模型

在 `auto-loop-full.py` 中：

```python
CLAUDE_MODEL = "claude-opus-4-6"  # 可改为 claude-sonnet-4-6 或其他模型
MAX_TOKENS = 8000                  # 最大 token 数
```

---

## 安全机制

### 1. 最大循环次数限制

默认最大循环 100 次，防止真正的无限循环消耗资源。

### 2. 中断信号处理

按 `Ctrl+C` 可以随时安全退出循环。

### 3. 错误处理

遇到错误时会记录日志并继续或退出，不会静默失败。

### 4. 日志记录

所有操作都会记录到 `auto-loop.log` 文件中，便于追踪和调试。

---

## 使用场景

### 场景 1：小型项目（10 个以内功能）

**推荐：** 半自动模式（Bash 或 Python）

**原因：**
- 功能较少，手动监督成本低
- 可以及时发现问题
- 节省 API 调用成本

**使用方法：**
```bash
bash auto-loop.sh
```

---

### 场景 2：中型项目（10-50 个功能）

**推荐：** 半自动模式 + 定期检查

**原因：**
- 功能较多，但仍需人工监督
- 可以分批执行
- 平衡自动化和控制

**使用方法：**
```bash
# 每天执行一次，完成 5-10 个功能
python auto-loop.py
```

---

### 场景 3：大型项目（50+ 个功能）

**推荐：** 完全自动模式（Claude API）

**原因：**
- 功能众多，手动监督成本高
- 可以长时间无人值守运行
- 适合夜间或周末执行

**使用方法：**
```bash
# 设置 API 密钥
export ANTHROPIC_API_KEY=your_api_key_here

# 启动自动循环（可以在后台运行）
nohup python auto-loop-full.py > output.log 2>&1 &
```

---

## 监控和调试

### 查看实时日志

```bash
# 实时查看日志
tail -f auto-loop.log

# 查看最近 50 行
tail -50 auto-loop.log

# 搜索错误
grep "❌" auto-loop.log
```

### 查看当前状态

```bash
# 查看功能状态
bash status.sh

# 查看进度日志
tail -50 claude-progress.md

# 查看 Git 历史
git log --oneline -10
```

### 手动干预

如果需要手动干预：

1. 按 `Ctrl+C` 停止循环
2. 手动修复问题
3. 重新启动循环

---

## 成本估算（Claude API）

### API 调用成本

假设每个功能需要：
- 输入：约 5,000 tokens（上下文 + 提示）
- 输出：约 3,000 tokens（代码 + 说明）

**Claude Opus 4.6 定价（示例）：**
- 输入：$15 / 1M tokens
- 输出：$75 / 1M tokens

**单个功能成本：**
- 输入：5,000 × $15 / 1,000,000 = $0.075
- 输出：3,000 × $75 / 1,000,000 = $0.225
- 总计：约 $0.30 / 功能

**项目成本估算：**
- 10 个功能：约 $3
- 50 个功能：约 $15
- 100 个功能：约 $30

---

## 最佳实践

### 1. 从小规模开始

先用 3-5 个简单功能测试自动循环，确保流程正确。

### 2. 定期检查

即使是完全自动模式，也建议每天检查一次进度和日志。

### 3. 备份代码

自动循环会频繁提交到 Git，建议定期推送到 GitHub：

```bash
# 每完成 10 个功能推送一次
git push origin main
```

### 4. 监控资源

长时间运行时注意监控：
- API 配额使用情况
- 磁盘空间（日志文件）
- 网络连接稳定性

### 5. 错误恢复

如果循环中断：
1. 检查日志找出原因
2. 手动修复问题
3. 重新启动循环（会自动从未完成的功能继续）

---

## 故障排除

### 问题 1：API 密钥无效

**错误：** `AuthenticationError: Invalid API key`

**解决：**
```bash
# 检查环境变量
echo $ANTHROPIC_API_KEY

# 重新设置
export ANTHROPIC_API_KEY=your_correct_api_key
```

### 问题 2：功能未标记完成

**现象：** 循环一直重复执行同一个功能

**原因：** features.json 未正确更新

**解决：**
1. 检查 features.json 中该功能的 passes 字段
2. 手动设置为 true
3. 重新启动循环

### 问题 3：循环卡住

**现象：** 长时间没有输出

**解决：**
1. 按 `Ctrl+C` 中断
2. 检查日志文件
3. 检查网络连接
4. 重新启动

### 问题 4：达到最大循环次数

**现象：** 循环在 100 次后自动退出

**解决：**
1. 检查是否有功能一直无法完成
2. 手动完成问题功能
3. 或增加 MAX_ITERATIONS 参数

---

## 高级用法

### 并行执行多个功能

如果功能之间没有依赖关系，可以并行执行：

```python
# 修改 auto-loop-full.py
# 使用 threading 或 multiprocessing 并行执行
```

### 自定义执行策略

可以根据功能的 category 或优先级自定义执行顺序：

```python
# 优先执行 technical 类型的功能
pending = sorted(
    pending,
    key=lambda f: (f['category'] != 'technical', f['id'])
)
```

### 集成 CI/CD

可以将自动循环集成到 CI/CD 流程中：

```yaml
# .github/workflows/auto-loop.yml
name: Auto Loop

on:
  schedule:
    - cron: '0 0 * * *'  # 每天午夜运行

jobs:
  auto-loop:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run auto loop
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python auto-loop-full.py
```

---

## 总结

全自动循环系统提供了三种模式：

1. **半自动（Bash）**：适合小型项目，需要人工监督
2. **半自动（Python）**：更好的错误处理和日志
3. **完全自动（API）**：真正的无人值守，适合大型项目

选择合适的模式，配置好参数，就可以实现"无限循环"执行任务，直到项目完成！
