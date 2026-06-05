---
name: search-kb
description: >
  搜索学术知识库。当用户说"查找相关资料"、"搜索知识库"、"有没有关于 X 的论文"、
  "知识库里有 Y 方法吗"、"search knowledge base"、"find papers about"、
  "检索相关文献"、"找一下之前的笔记"、"查一下收录的图书"时使用此 skill。
  按主题、关键词搜索四类知识卡（论文/理论/图书/信息），返回按相关性排序的结果。
---

# 搜索知识库

> 先读取 `skills/references/shared-conventions.md` 了解作用域约定和反上下文污染。

## 前置检查

检查 `${user_config.kb_path}` 是否已配置。如果为空，引导用户首次配置，**不继续执行**。

## 概述

在知识库中按主题/关键词查找相关的论文、理论、图书和信息卡，返回结构化结果，供学术写作引用。

## 检索优先级

1. 先读索引文件（快速全局浏览）→ `wiki/indexes/all-*.md`
2. 再读 `meta.json`（结构化字段精确匹配）→ `wiki/theories/*/meta.json`, `wiki/info/*/meta.json`
3. 最后读 `SKILL.md`（深度匹配调用场景）→ 仅对前两步中的高分候选项

## 执行流程

### 1. 解析查询意图

从 `$ARGUMENTS`（或用户的上一条消息）中提取：
- **核心主题**：用户在研究什么？（如"神经网络优化"）
- **类型偏好**：有没有指定只看论文？方法？图书？
- **约束条件**：年份范围？特定作者？语言？

### 2. 索引层搜索（快速，高召回）

读取四个索引文件：
- `wiki/indexes/all-papers.md` → 按标题、作者、年份匹配
- `wiki/indexes/all-theories.md` → 按名称、分类匹配
- `wiki/indexes/all-books.md` → 按标题、作者匹配
- `wiki/indexes/all-info.md` → 按名称、类型、标签匹配

### 3. 元数据层搜索（结构化，精确）

对于理论和信息卡，遍历 `meta.json`：
- 匹配 `name`、`description`、`category`、`tags`
- 检查 `call_conditions` 是否与用户场景吻合
- 检查 `papers` 引用链（发现间接相关论文）

### 4. 深度匹配（精读，高精度）

对前两步评分最高的候选项（通常 ≤ 10 个），读取其 `SKILL.md`：
- 匹配"何时引用/使用"章节
- 检查"与其他知识卡的关系"发现更多线索

### 5. 输出结果

按类型和相关性排序，使用以下格式：

```markdown
## 🔍 检索结果："<查询>"

### 🔧 理论/方法工具（可直接调用）
- **<名称>** → `wiki/theories/<id>/SKILL.md`
  简介：<一句话>
  匹配原因：<为什么推荐>
  关联论文：citekey1, citekey2

### 📄 论文（应引用）
- **[citekey] 标题** → `wiki/papers/<citekey>/SKILL.md`
  贡献：<核心贡献一句话>
  匹配原因：<为什么推荐>
  年份：<year>

### 📚 图书（可参考）
- **[citekey] 书名** → `wiki/books/<citekey>/SKILL.md`
  要点：<核心观点>
  匹配原因：<为什么推荐>

### 📊 信息资料（可用数据）
- **<名称>** → `wiki/info/<id>/SKILL.md`
  类型：<type> | 来源：<source>
  匹配原因：<为什么推荐>
```

## 如果无匹配结果

1. 尝试放宽搜索词（如从"多头注意力反向传播梯度分析"放宽到"注意力机制"）
2. 列出最接近的近似匹配（哪怕只有部分关键词命中）
3. 建议用户摄入相关领域的新资料：`/scholar-assistant:ingest`
4. 如果理论/方法缺失但发现多篇论文涉及，建议提取为理论工具卡
