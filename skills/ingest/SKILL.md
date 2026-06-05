---
name: ingest
description: >
  摄入知识到学术知识库。人工笔记优先（反幻觉），无人笔记时LLM直接读原文，两者共存时交叉验证。
  当用户说"加入知识库"、"整理笔记/摘录"、"帮我读这篇论文"、"消化这篇文章"、"归档这本书"、
  "记录这个理论/方法"、"访谈入库"、"ingest"时使用此 skill。
---

# 摄入知识

> 先读取 `skills/references/shared-conventions.md` 了解设计哲学、作用域和反上下文污染。

## 前置检查

检查 `${user_config.kb_path}` 是否已配置。如果为空，**不继续执行**，引导用户完成首次配置：

```
⚠️ 知识库尚未配置，无法摄入知识。

请先运行 /scholar-assistant:init-kb 选择作用域：
  global  → 全局知识库（所有项目共享）
  project → 项目知识库（仅当前项目）
  自定义 → 如 Obsidian vault 路径
```

只有 `kb_path` 已配置且目录存在时才继续。

## 概述

将单条知识摄入知识库。核心原则：**人工笔记优先**——人的洞察不会被 LLM 修改或替代，LLM 的角色是结构化、关联和补充。

## 步骤 1：判断输入路径

| 输入特征 | 路径 | 可信度 |
|---------|------|--------|
| 人工写的读书笔记/摘录/书评/实验记录 | **A：人工笔记→结构化** | `human-notes` |
| 论文/图书原文（MD/文本），用户说"帮我读" | **B：LLM 直接阅读** | `llm-reading` |
| 人工笔记 + 原文都有，用户说"对照" | **C：交叉验证** | `cross-validated` |

## 步骤 2：按路径处理

> 详细处理步骤见 `skills/references/ingest-paths.md`。此处只列关键差异。

### 路径 A：人工笔记结构化

- 从笔记提取关键信息，**不做推断补充**
- 人工的批判性评论保留在"讨论"章节
- 笔记中没覆盖的章节标注 `<!-- TODO: 需补充 -->`

### 路径 B：LLM 直接阅读

- 标记 `source: llm-reading` + `trust: review-needed`
- 原文明确说的 → `[原文]`，LLM 推断的 → `[LLM推断]`
- 完成后提醒用户人工复审

### 路径 C：交叉验证

- 以人工笔记为 ground truth，逐章节对照
- 一致 → `✅ cross-validated`；不一致 → 标记差异，请用户确认
- 原文有但人工没提到 → LLM 补充，标注 `[LLM补充-请确认]`

## 步骤 3：创建知识卡

按标准结构在 `$KB_ROOT/wiki/<type>/<id>/` 下创建文件。SKILL.md frontmatter 包含 `source` 和 `trust` 标记。模板在 `${CLAUDE_PLUGIN_ROOT}/templates/` 下。

## 步骤 4：刷新索引

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/generate_index.py" "$KB_ROOT/wiki/"
```

## 步骤 5：报告结果

告知用户摄入路径、可信度标记、信息缺失项。如果 `source: llm-reading`，提醒人工复审。
