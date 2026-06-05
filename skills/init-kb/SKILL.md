---
name: init-kb
description: >
  初始化知识库目录结构。当用户说"创建知识库"、"初始化知识库"、"新建学术知识库"、
  "setup knowledge base"、"init kb"、或首次使用插件需要配置知识库路径时使用此 skill。
  支持全局作用域（所有项目共享）和项目作用域（仅当前项目）。
---

# 初始化知识库

> 先读取 `skills/references/shared-conventions.md` 了解作用域设计和路径约定。

## 概述

在用户指定路径创建三层架构：`raw/`（人工笔记 + 原文）+ `wiki/`（结构化知识卡）+ `outputs/`（草稿/报告）。

**关键原则**：首次使用必须由用户选择作用域和路径，插件不会自动在后台创建知识库。

## 步骤

### 1. 判断场景

| 场景 | 判断条件 | 如何处理 |
|------|---------|---------|
| **首次配置** | `${user_config.kb_path}` 为空 | 引导用户选择作用域（见步骤 2） |
| **已配置，重新初始化** | `kb_path` 已配置，但目录不存在或用户要求重建 | 使用已配置路径，直接创建 |
| **指定自定义路径** | `$ARGUMENTS` 包含路径 | 使用 `$ARGUMENTS` 指定的路径，创建后设置 userConfig |
| **Obsidian 联动** | 用户提到 Obsidian | 引导用户填入 vault 路径 |

### 2. 首次配置：引导选择作用域

如果 `${user_config.kb_path}` 为空，向用户展示：

```
⚠️ 知识库尚未配置。请选择知识库存储方式：

🟢 全局知识库 — 所有项目共享同一个知识库
   → 路径: ~/.claude/scholar-assistant/knowledge-base/
   → 适合: 单一研究方向，跨项目积累知识
   → 命令: /scholar-assistant:init-kb global

🔵 项目知识库 — 仅当前项目使用
   → 路径: ./.claude/knowledge-base/
   → 适合: 多项目并行研究，每个项目独立知识库
   → 命令: /scholar-assistant:init-kb project

🟡 自定义路径 — 如 Obsidian vault 联动
   → 命令: /scholar-assistant:init-kb <你的路径>
```

根据用户选择确定实际路径：

| 用户选择 | 实际路径 | 配置文件 |
|---------|---------|---------|
| `global` | `~/.claude/scholar-assistant/knowledge-base/` | `~/.claude/settings.json` |
| `project` | `<cwd>/.claude/knowledge-base/` | `<cwd>/.claude/settings.json` |
| 自定义路径 | 用户指定的绝对路径 | 由用户决定作用域 |

### 3. 创建目录结构

确定路径后，运行脚本：

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/init_kb.py" "<目标路径>"
```

如果 Python 不可用，手动创建：

```
<kb_root>/
├── raw/papers/        # 人工笔记或论文原文
├── raw/books/         # 人工笔记或图书章节
├── raw/materials/     # 研究收集的资料
├── raw/bib/           # BibTeX 文件
├── wiki/indexes/      # 自动生成的总索引
├── wiki/papers/       # 论文知识卡
├── wiki/theories/     # 理论/方法工具卡
├── wiki/books/        # 图书知识卡
├── wiki/info/         # 信息知识卡
├── outputs/drafts/    # 论文草稿
├── outputs/outlines/  # 论文大纲
├── outputs/health/    # 健康检查报告
└── .claude/rules/     # Claude 规则（首次编译时生成）
```

以及空索引文件：`all-papers.md`、`all-theories.md`、`all-books.md`、`all-info.md`。

### 4. 设置 userConfig

初始化完成后，提醒用户如何持久化配置：

- **全局作用域**：在 `~/.claude/settings.json` 中设置 `pluginConfigs["scholar-assistant"].kb_path`
- **项目作用域**：在 `<cwd>/.claude/settings.json` 中设置

如果用户是通过 Claude Code 插件配置 UI 启用的，则在安装时已自动弹出配置界面。如果用户是手动 `--plugin-dir` 方式加载，告知如何配置。

### 5. 报告结果

```markdown
✅ 知识库初始化完成

- 作用域：<global|project|custom>
- 路径：<绝对路径>
- 配置状态：已设置

📖 下一步：
- 摄入知识：/scholar-assistant:ingest
- 编译知识库：/scholar-assistant:compile
- 如果与 Obsidian 联动：现在可以在 Obsidian 中看到 raw/ 和 wiki/ 目录
```

### 如果知识库已存在

如果目标路径已有知识库结构，告知用户：
- 已存在 N 张论文卡、M 张理论卡、K 张图书卡、J 张信息卡
- 重新初始化**不会删除**已有知识卡
- 仅重建缺失的目录和索引文件
