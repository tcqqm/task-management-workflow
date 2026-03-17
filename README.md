# 任务管理工作流系统

基于 Anthropic 文章《Effective Harnesses for Long-Running Agents》实现的任务管理系统。

## 项目简介

本项目实现了一个用于长期运行代理的任务管理工作流系统，采用双代理架构，通过状态工件（功能列表、进度日志、Git 历史）实现跨多个上下文窗口的一致进展。

## 核心特点

- **双代理架构**：初始化代理 + 工作代理
- **增量式开发**：一次只做一个功能
- **状态追踪**：使用 JSON 格式防止意外修改
- **端到端测试**：使用 Playwright MCP 进行测试
- **清洁状态**：每次会话结束时代码可合并到主分支

## 文件结构

```
.
├── features.json           # 功能追踪文件（核心）
├── claude-progress.md      # 进度日志文件
├── init.sh                 # 启动脚本
├── status.sh               # 功能状态查询脚本
├── .gitignore              # Git 忽略规则
└── README.md               # 本文档
```

### features.json - 功能追踪文件

记录所有功能的状态，每个功能包含：
- `id`: 唯一标识符
- `category`: 类别（functional/technical/documentation）
- `description`: 功能描述
- `steps`: 验证步骤
- `passes`: 是否通过测试（只能修改此字段）
- `created`: 创建时间
- `completed`: 完成时间（只能修改此字段）

**重要规则**：只能修改 `passes` 和 `completed` 字段，不能删除或修改功能描述。

### claude-progress.md - 进度日志

记录每次会话的工作内容：
- 工作的功能
- 完成的变更
- 测试结果
- Git 提交
- 下一步计划

### init.sh - 启动脚本

快速启动开发环境，显示项目状态和功能统计。

### status.sh - 状态查询脚本

快速查看未完成的功能列表和完成进度。

## 使用方法

### 会话开始

```bash
# 1. 确认当前位置
pwd

# 2. 启动开发环境
bash init.sh

# 3. 查看功能状态
bash status.sh

# 4. 查看最近的工作
tail -50 claude-progress.md

# 5. 查看 Git 历史
git log --oneline -10
```

### 工作过程

1. **选择功能**：从 `features.json` 中选择一个 `"passes": false` 的功能
2. **实现功能**：编写代码，添加中文注释
3. **测试功能**：使用 Playwright MCP 进行端到端测试
4. **更新状态**：只修改 `passes` 和 `completed` 字段

### 会话结束

```bash
# 1. 提交代码
git add .
git commit -m "功能描述

- 变更点 1
- 变更点 2

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

# 2. 更新进度日志
# 编辑 claude-progress.md 添加新的会话记录

# 3. 备份到 GitHub（可选）
# 使用 GitHub MCP 推送代码
```

## 快速命令

```bash
# 查看未完成的功能
cat features.json | grep '"passes": false'

# 查看已完成的功能
cat features.json | grep '"passes": true'

# 统计功能数量
bash status.sh

# 查看最近的进度
tail -30 claude-progress.md

# 查看最近的提交
git log --oneline -10
```

## 最佳实践

1. **增量式开发**：一次只做一个功能
2. **清洁状态**：每次会话结束时代码应该可以合并
3. **充分测试**：使用 Playwright MCP 进行端到端测试
4. **清晰记录**：git 提交消息和进度日志要详细
5. **防止意外**：只修改 features.json 中的 `passes` 和 `completed` 字段

## 工作流原理

本系统基于 Anthropic 文章中的四大失败模式及解决方案：

| 问题 | 解决方案 |
|------|---------|
| 过早宣布项目完成 | 使用功能列表文件，一次只选择一个功能 |
| 留下有 bug 的环境 | 使用 git 和进度日志，会话开始时运行测试 |
| 过早标记功能完成 | 自我验证所有功能，充分测试后才标记 |
| 需要时间弄清楚如何运行 | 使用 init.sh 脚本快速启动 |

## 参考资料

- Anthropic 文章：《Effective Harnesses for Long-Running Agents》
- CLAUDE.md：完整的工作流文档

## 许可证

本项目用于学习和实践目的。
