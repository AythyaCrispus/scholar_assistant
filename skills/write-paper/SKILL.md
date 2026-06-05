---
description: >
  学术论文写作主流程。当用户说"写论文"、"开始写作"、"写文献综述"、"帮我写引言"、
  "起草论文"、"write paper"、"draft article"、"写一篇关于 X 的论文"、
  "整理成学术文章"、"写会议论文"、"写毕业论文章节"时使用此 skill。
  按 skill 调用逻辑串联：搜索知识库→调取理论/方法→引用文献→使用数据→生成论文草稿。
---

# 学术写作

> 先读取 `skills/references/shared-conventions.md` 了解作用域约定和反上下文污染。

## 前置检查

检查 `${user_config.kb_path}` 是否已配置。如果为空，引导用户首次配置，**不继续执行**。

## 概述

将知识库中的素材编织为结构完整的学术论文。核心思路：**像调用 skill 一样调用理论/方法工具，像引用库一样引用论文和图书，像使用数据源一样使用信息卡**。

## 写作六阶段

### 阶段 0：确认写作目标

与用户确认（不要假设，不要跳过）：
1. **研究问题**：一句话，这论文要回答什么问题？
2. **论文类型**：研究论文 / 文献综述 / 技术报告 / 学位论文 / 会议论文
3. **目标期刊/会议**（可选，影响风格和格式）
4. **参考结构**：用户是否有预期的章节大纲？如果没有，根据类型推荐
5. **引用格式**：`${user_config.default_citation_style}`（默认 APA）
6. **作者信息**：`${user_config.author_name_en}`（如有配置）

### 阶段 1：文献调研

用 Grep/Read 工具搜索知识库：
1. 读 `$KB_ROOT/wiki/indexes/all-papers.md`、`all-theories.md` — 获取全貌
2. 搜索主题关键词 → 找到相关条目
3. 对高分候选项，读取其 `SKILL.md` 确认相关性
4. 整理"写作素材清单"：

```markdown
## 写作素材清单
### 将调用的理论/方法
- theory-id-1: 用于分析 X
### 将引用的论文
- citekey-1: 支撑论点 Y
### 将参考的图书
- citekey-2: 提供背景 Z
### 将使用的信息
- info-id-1: 数据支撑
```

> **必须与用户确认素材清单再继续**。

### 阶段 2：生成大纲

根据写作目标 + 素材清单，生成详细大纲：

```markdown
## 论文大纲

### 1. 引言
- 研究背景与动机
- 研究问题
- 本文贡献
- 📄 引用: citekey-1, citekey-2

### 2. 相关工作 / 文献综述
- 子主题 A → 📄 citekey-3, citekey-4
- 子主题 B → 🔧 theory-id-1, 📄 citekey-5

### 3. 方法
- 🔧 theory-id-1 的应用步骤
- 📄 citekey-6 的改进

### ...
```

> **必须与用户确认大纲后再开始写作**。

### 阶段 3：逐章节写作

对每个章节，按以下模式写作：

1. **读取该章节需要的全部知识卡全文**（不只是 SKILL.md，还包括 detail.md、fulltext.md、book.md、content.md）
2. **使用 `academic-writer` agent** 或直接写作
3. **写作原则**：
   - 每个学术主张必须有引用支撑 — 使用 `[@citekey]` 标记
   - 方法部分严格遵循理论卡 `detail.md` 中的步骤
   - 数据和论证来自信息卡的 `content.md`
   - 保持学术语体，段落间要有逻辑过渡
   - 中文论文：中文撰写，英文术语首次出现时标注原文
4. 每写完一章，停下来让用户审阅

### 阶段 4：生成参考文献

1. 扫描全文收集所有 `[@citekey]` 标记
2. 对每个 citekey，读取 `wiki/papers/<citekey>/reference.bib` 或 `wiki/books/<citekey>/reference.bib`
3. 用脚本生成格式化引用：

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/parse_bibtex.py" <bib文件> --format citation --style "APA"
```

4. 将格式化后的参考文献列表附加到论文末尾

### 阶段 5：完整性自查

- [ ] 每个 `[@citekey]` 在参考文献中都有对应条目
- [ ] 每个调用的理论/方法在文中都有说明
- [ ] 结论回应了引言中的研究问题
- [ ] 章节之间逻辑连贯（检查过渡句）
- [ ] 没有孤立的段落（每段都有明确的论点+支撑）

### 阶段 6：保存输出

将完整论文保存到 `$KB_ROOT/outputs/drafts/<topic-slug>-YYYY-MM-DD.md`

同时输出到当前工作目录（如果用户要求）。
