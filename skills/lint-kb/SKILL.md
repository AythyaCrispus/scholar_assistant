---
description: >
  知识库健康检查与维护。当用户说"检查知识库"、"知识库健康检查"、"校验完整性"、
  "lint knowledge base"、"检查死链"、"找出孤立知识卡"、"知识库维护"、
  "我的知识库有什么问题"、"有没有过时的资料"时使用此 skill。
  校验文件完整性、交叉引用一致性、内容质量，生成健康报告并提供修复建议。
---

# 知识库健康检查

> 先读取 `skills/references/shared-conventions.md` 了解作用域约定和脚本调用。

## 前置检查

检查 `${user_config.kb_path}` 是否已配置。如果为空，引导用户首次配置，**不继续执行**。

## 概述

对知识库进行系统性健康检查，类似代码的 lint 工具——发现结构问题、引用断裂、内容缺失，生成可操作的修复建议。

## 检查维度

### 维度 1：文件完整性（自动化）

运行校验脚本：

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/validate_card.py" "$KB_ROOT/wiki/" --cross-ref
```

脚本检查每张知识卡是否包含所有必需文件：

| 知识卡类型 | 必需文件 |
|-----------|---------|
| 论文 | `reference.bib`, `fulltext.md`, `SKILL.md` |
| 理论/方法 | `meta.json`, `detail.md`, `SKILL.md` |
| 图书 | `reference.bib`, `book.md`, `SKILL.md` |
| 信息 | `meta.json`, `content.md`, `SKILL.md` |

**如果脚本不可用**（Python 缺失），手动遍历 `wiki/papers/`、`wiki/theories/`、`wiki/books/`、`wiki/info/` 检查。

### 维度 2：交叉引用一致性

1. **理论 → 论文引用**：检查每个理论卡 `meta.json` 中 `papers` 数组的每个 citekey 是否对应存在的论文卡目录
2. **理论间引用**：检查 `related_theories` 中的 theory-id 是否有效
3. **论文卡 SKILL.md 中的理论提及**：如果论文卡提到了某个理论/方法，检查该理论是否已建卡
4. **孤立检测**：标记没有任何其他卡引用的知识卡
5. **死链检测**：标记引用链中不存在的 citekey 或 theory-id

### 维度 3：内容质量

逐卡检查（先索引后深入）：

1. **SKILL.md 内容长度**：< 100 字符 → 警告"未充分填写"
2. **meta.json 必填字段**：name、description、call_conditions 是否非空
3. **图书卡页码标注**：`book.md` 中是否有 `[p.X]` 格式的页码引用
4. **BibTeX 必填字段**：author、title、year 是否齐全
5. **fulltext.md 结构化程度**：是否包含方法、实验、结论等章节

### 维度 4：时效性与冗余

1. **出版年份**：标记 > 10 年的论文（不是要删除，而是标记让用户确认仍有引用价值）
2. **重复检测**：标题或 citekey 高度相似的知识卡
3. **缺失交叉链接**：内容相似但互未引用的知识卡

## 输出健康报告

```markdown
## 🏥 知识库健康报告 — YYYY-MM-DD

### 🔴 严重问题（需立即修复）
- [缺失] `wiki/theories/xxx/meta.json` — 缺少文件
- [死链] 理论 `yyy` 引用不存在的论文 `zzz`

### 🟡 警告（建议修复）
- [内容过短] `wiki/papers/aaa/SKILL.md` — 仅 45 字符
- [缺少字段] `wiki/theories/bbb/meta.json` — call_conditions 为空
- [缺少页码] `wiki/books/ccc/book.md` — 关键句子未标注页码

### 🔵 建议（可选改进）
- [潜在链接] `wiki/papers/ddd` 和 `wiki/papers/eee` 讨论相同主题但未互引
- [过时标记] `wiki/papers/fff` 已超过 10 年，确认是否仍有引用价值
- [新理论线索] ddd、eee、ggg 均讨论注意力机制，建议创建理论工具卡

### 📊 统计
- 论文: N | 理论: M | 图书: K | 信息: J
- 健康: X | 警告: Y | 严重: Z
```

报告保存到 `$KB_ROOT/outputs/health/health-report-YYYY-MM-DD.md`。

## 修复

对于每个可自动修复的问题，询问用户是否修复：
- 补充缺失模板文件（基于已有信息推断填充）
- 移除无效引用（死链）
- 补充交叉链接（基于共有关键词）

**不自动修复的是**：内容质量问题（需要用户手动补充信息）、重复检测（需要用户判断保留哪个）。
