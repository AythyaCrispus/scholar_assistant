---
name: compile
description: >
  批量编译知识库——扫描 raw/ 中所有资料，将人工笔记和/或原文批量转化为结构化的 wiki/ 知识卡。
  当用户说"编译知识库"、"处理笔记"、"整理 raw 里的资料"、"更新知识库"、"批量生成知识卡"、
  "compile"、"build wiki"时使用此 skill。人工笔记优先（反幻觉），无人笔记时LLM直接读原文，两者共存时交叉验证。
---

# 编译知识库

> 先读取 `skills/references/shared-conventions.md` 了解设计哲学和反上下文污染。
> 路径 A/B/C 的详细处理步骤见 `skills/references/ingest-paths.md`。

## 前置检查

检查 `${user_config.kb_path}` 是否已配置。如果为空，引导用户首次配置（同 init-kb），**不继续执行**。只有 `kb_path` 已配置且 `raw/` 和 `wiki/` 目录存在时才继续。

## 概述

批量扫描 `raw/` 中的所有资料，按优先级处理：
1. **人工笔记 + 原文共存** → 交叉验证（路径 C，最高可信度）
2. **只有人工笔记** → 结构化提取（路径 A）
3. **只有原文（无笔记）** → LLM 直接阅读（路径 B，标注 `review-needed`）

## 步骤 1：扫描与分类

遍历 `$KB_ROOT/raw/`，对每个 citekey/material 判断：

| raw/ 中存在 | wiki/ 中状态 | 操作 |
|------------|-------------|------|
| `*-notes.md` + `*-fulltext.md` | 无对应卡 | **路径 C**：交叉验证 |
| `*-notes.md`（无全文） | 无对应卡 | **路径 A**：人工笔记结构化 |
| `*-fulltext.md`（无笔记） | 无对应卡 | **路径 B**：LLM 直接阅读 |
| 笔记或全文已更新 | 已有卡 | **重新编译**，保留人工编辑部分 |
| 无变化 | 已有卡 | **跳过** |

向用户报告扫描结果：

```markdown
## 📋 扫描结果

### 路径 C — 交叉验证（人工笔记 + 原文）
- `citekey-1` — 有人工笔记和全文

### 路径 A — 人工笔记结构化
- `citekey-2-notes.md` — 有笔记无全文

### 路径 B — LLM 直接阅读（⚠ 需人工复审）
- `citekey-3-fulltext.md` — 无人工笔记

### 已更新（待重新编译）
- `citekey-4` — 笔记 YYYY-MM-DD 更新

### 跳过（无变化）
- `citekey-5`
```

## 步骤 2：按路径批量处理

> 每条路径的详细处理步骤见 `skills/references/ingest-paths.md`。编译时逐条处理，但遵循以下批量原则：

- **路径 A**：完全基于人的笔记，LLM 不做推断补充。标记 `source: human-notes`。
- **路径 B**：LLM 直接阅读原文。标记 `source: llm-reading` + `trust: review-needed`。对每张卡输出 ⚠ 提醒。
- **路径 C**：同时阅读笔记和原文，以人工笔记为 ground truth 逐章节对照。产出交叉验证报告嵌入 `fulltext.md`/`book.md` 末尾。

## 步骤 3：交叉链接

LLM 的核心价值——发现人可能忽略的知识网络：

1. 多篇论文/图书共同讨论的概念 → 建议创建理论工具卡
2. 论文之间的引用关系 → 在 SKILL.md 中建立链接
3. 图书与论文的对话 → 建立跨类型链接
4. 输出链接发现报告

## 步骤 4：刷新索引

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/generate_index.py" "$KB_ROOT/wiki/"
```

## 步骤 5：生成编译报告

```markdown
## 📊 编译报告 — YYYY-MM-DD

### 本次编译
| 路径 | 数量 | 可信度 |
|------|------|--------|
| 🟢 交叉验证 (C) | N | high |
| 🔵 人工笔记 (A) | N | human-notes |
| 🟡 LLM阅读 (B) | N | review-needed |

### 需人工关注的项
- 🟡 `citekey` — LLM 生成，建议人工复审
- ⚠ `citekey` — 有 LLM 补充内容，请确认

### 💡 建议
- 为"<概念>"创建理论工具卡（被 citekey1, citekey2 讨论）
```
