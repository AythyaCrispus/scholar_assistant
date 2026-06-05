# Scholar Assistant — Claude Code 学术写作插件

> 基于 Karpathy LLM Wiki 架构，但有一个关键区别：**知识库由人和 LLM 共同维护**。
> 人的洞察是 ground truth，LLM 负责结构化、关联和补充——用"双输入"对抗 LLM 幻觉。

## 与 Karpathy LLM Wiki 的区别

| | Karpathy LLM Wiki | Scholar Assistant |
|---|---|---|
| 📥 信息来源 | LLM 自动抓取 | **人工笔记 + LLM 直接阅读** 双输入 |
| 🔧 维护方式 | LLM 全自动 | **人 + LLM 协作** |
| 🤖 LLM 角色 | 从头生成一切 | 结构化 / 阅读 / 交叉验证 |
| 👤 人的角色 | 丢链接 | **贡献洞察，反幻觉 ground truth** |
| ✅ 可信度 | 依赖 LLM | **人工笔记 > LLM 阅读，双重可交叉验证** |
| 📊 作用域 | 无 | **全局/项目两级，避免数据污染上下文** |

## 知识库作用域

**首次使用必须由用户指定作用域**——插件不会在后台自动创建知识库。

| 作用域 | 路径 | 适用场景 |
|--------|------|---------|
| 🟢 **全局** | `~/.claude/scholar-assistant/knowledge-base/` | 单一研究方向，跨项目共享 |
| 🔵 **项目** | `<project>/.claude/knowledge-base/` | 多项目并行，各项目独立 |
| 🟡 **自定义** | 任意路径 | Obsidian vault 联动 |

## 安装

```bash
# 本地开发
claude --plugin-dir ./scholar-assistant

# 安装到用户目录
claude plugin install ./scholar-assistant
```

## 快速开始

### 1. 首次配置（必须）

插件安装后，首次使用需先初始化知识库：

```
/scholar-assistant:init-kb
```

根据提示选择作用域：
- 输入 `global` → 全局知识库，所有项目共享
- 输入 `project` → 项目知识库，仅当前项目
- 输入路径 → 自定义（如 Obsidian vault）

### 2. 写人工笔记

在 `raw/papers/` 中写论文笔记（自由格式）：

```markdown
# Attention Is All You Need - 阅读笔记

## 核心想法
用自注意力替代 RNN，可并行计算，解决长距离依赖。

## 方法要点
- Scaled Dot-Product Attention: Attention(Q,K,V) = softmax(QK^T/√d_k)V
- Multi-Head: 并行做多次 attention 再拼接

## 我的疑问
- Multi-Head 数量（8个）是经验选择还是有理论依据？
- √d_k 缩放因子为什么是必须的？[需要再查原文]
```

### 3. 编译（LLM 将笔记结构化）

```
/scholar-assistant:compile
```

LLM 扫描 raw/ → 生成结构化知识卡 → 建立交叉链接 → 标注可信度。

### 4. 写作

```
/scholar-assistant:write-paper

主题：注意力机制在 NLP 中的演进
类型：文献综述，约 5000 字
```

## 三种摄入路径

| 路径 | 输入 | LLM 做什么 | 可信度 |
|------|------|-----------|--------|
| 🟢 **路径 C** | 人工笔记 + 原文 | 交叉验证 | `cross-validated` |
| 🔵 **路径 A** | 仅人工笔记 | 结构化提取 | `human-notes` |
| 🟡 **路径 B** | 仅原文 | LLM 直接阅读 | `llm-reading` ⚠复审 |

## 命令参考

| 命令 | 用途 |
|------|------|
| `/scholar-assistant:init-kb` | 初始化知识库（首次必须） |
| `/scholar-assistant:ingest` | 单篇摄入 |
| `/scholar-assistant:compile` | 批量编译 raw/ → wiki/ |
| `/scholar-assistant:search-kb` | 搜索知识库 |
| `/scholar-assistant:write-paper` | 学术写作 |
| `/scholar-assistant:lint-kb` | 健康检查 |

## 反上下文污染

知识库内容**不会自动加载到 Claude 上下文**：
- 索引文件仅在搜索时读取
- 知识卡全文仅在命中或写作时读取
- raw/ 仅在编译时读取
- SessionStart hook 仅打印路径提示

## 知识库结构

```
<kb_root>/
├── raw/                          # 人工笔记 + 原文（工作区）
│   ├── papers/                   # *-notes.md 或 *-fulltext.md
│   ├── books/                    # 读书笔记（分章）或图书全文
│   ├── materials/                # 访谈/实验/田野资料
│   └── bib/                      # BibTeX 文件
├── wiki/                         # 结构化知识卡（编译产物）
│   ├── indexes/                  # 自动生成的总索引（all-*.md）
│   ├── papers/<citekey>/         # 论文卡: reference.bib + fulltext.md + SKILL.md
│   ├── theories/<id>/            # 理论卡: meta.json + detail.md + SKILL.md
│   ├── books/<citekey>/          # 图书卡: reference.bib + book.md + SKILL.md
│   └── info/<id>/                # 信息卡: meta.json + content.md + SKILL.md
└── outputs/                      # 论文草稿、大纲、健康报告
```

## 四类知识卡

| 类型 | 核心文件 | 特殊要求 |
|------|---------|---------|
| 📄 论文 | `reference.bib` + `fulltext.md` + `SKILL.md` | SKILL.md 标注 `source` 和 `trust` |
| 🔧 理论/方法 | `meta.json` + `detail.md` + `SKILL.md` | meta.json 含 `call_conditions` |
| 📚 图书 | `reference.bib` + `book.md` + `SKILL.md` | 关键句子**必须标页码** `[p.123]` |
| 📊 信息 | `meta.json` + `content.md` + `SKILL.md` | meta.json 含 `type`/`source`/`date` |

## 可信度标记

| 字段 | 值 | 含义 |
|------|-----|------|
| `source` | `human-notes` / `llm-reading` / `cross-validated` / `mixed` | 信息来源 |
| `trust` | `high` / `review-needed` / `partial` | 可信度 |

## 辅助脚本

| 脚本 | 用途 |
|------|------|
| `scripts/init_kb.py` | 创建目录结构 |
| `scripts/parse_bibtex.py` | BibTeX 解析（APA/MLA/GB7714） |
| `scripts/generate_index.py` | 自动索引生成 |
| `scripts/validate_card.py` | 知识卡校验 |

## 与 Obsidian 联动

```bash
/scholar-assistant:init-kb ~/Obsidian/my-research-vault/
```

`wiki/` 可在 Obsidian 中直接浏览，Graph View 可视化知识网络。

## 许可证

MIT
