# 学术写作插件共享约定

## 设计哲学：双输入反幻觉知识库

**与 Karpathy LLM Wiki 的关键区别**：

| | Karpathy LLM Wiki | Scholar Assistant |
|---|---|---|
| 信息来源 | LLM 自动抓取网页/播客 | **人工笔记 + LLM 直接阅读** 双输入 |
| 维护方式 | LLM 全自动维护 | **人+LLM 共同维护** |
| LLM 角色 | 从头生成摘要和概念 | **①直接阅读 ②人工笔记结构化 ③交叉验证** |
| 人的角色 | 只丢入链接 | **贡献洞察，提供反幻觉 ground truth** |
| 可信度 | 依赖 LLM 准确性 | **人工笔记 > LLM 阅读，双重输入可交叉验证** |

## 知识库作用域与路径

### 两层作用域

首次使用插件时必须先配置知识库路径。插件不会自动创建知识库——由用户决定数据存放在哪里。

| 作用域 | 配置文件位置 | 建议路径 | 适用场景 |
|--------|------------|---------|---------|
| `global` | `~/.claude/settings.json` | `~/.claude/scholar-assistant/knowledge-base/` | 单一研究方向，所有项目共享同一个知识库 |
| `project` | `<project>/.claude/settings.json` | `<project>/.claude/knowledge-base/` | 多项目并行研究，每个项目独立的知识库 |
| `custom` | 取决于 scope | 用户指定（如 Obsidian vault 路径） | 需要和 Obsidian 等外部工具联动 |

### 首次配置流程

当用户第一次使用任何 skill（`/scholar-assistant:ingest`、`/scholar-assistant:compile` 等）时：

1. **检测** `kb_path` 是否已配置
2. 如果未配置，引导用户选择作用域：

```
⚠️ 知识库尚未配置。请选择知识库存储方式：

🟢 全局知识库 — 所有项目共享（适合单一研究方向）
   → 路径: ~/.claude/scholar-assistant/knowledge-base/
   → 命令: /scholar-assistant:init-kb --scope global

🔵 项目知识库 — 仅当前项目使用（适合多项目并行）
   → 路径: ./.claude/knowledge-base/
   → 命令: /scholar-assistant:init-kb --scope project

🟡 自定义路径 — 如 Obsidian vault 联动
   → 命令: /scholar-assistant:init-kb <你的路径>
```

3. 执行 `/scholar-assistant:init-kb` 创建目录结构并设置 `userConfig.kb_path`

### 获取知识库路径

所有 skill 的第一步：确定 `$KB_ROOT`。按优先级：
1. `${user_config.kb_path}` — 已配置的值
2. 如果为空 → 触发首次配置流程（见上）
3. `$ARGUMENTS` — 用户临时指定的路径（仅当前操作生效）

### 反上下文污染

知识库内容**不会自动加载到 Claude 上下文**。原则：
- **索引文件**（`wiki/indexes/all-*.md`）很小（仅标题+摘要），搜索时选择性读取
- **知识卡全文**仅在用户明确需要时读取（写作、搜索命中、编译时）
- **raw/ 中的原始资料**仅在编译时读取
- **Hook 不加载知识库内容**——SessionStart 仅打印路径提示

## 可信度标记

| 标记 | 含义 | 场景 |
|------|------|------|
| `source: human-notes` | 基于人工笔记，人工洞察为 ground truth | raw/ 中有详细笔记 |
| `source: llm-reading` | LLM 直接阅读原文生成 | 没写笔记，LLM 直接读原文 |
| `source: cross-validated` | 人工笔记 + LLM 阅读交叉验证通过 | 两个来源一致 |
| `source: mixed` | 部分人工，部分 LLM 补充 | 人工笔记不完整 |
| `trust: review-needed` | 建议人工复审 | LLM 阅读中不确定性 |

## raw/ 的语义：人工笔记 + 可被 LLM 直接读的原文

```
raw/
├── papers/        # 人工论文笔记 或 论文原文
│   ├── vaswani2017attention-notes.md     # 人工笔记（优先采用）
│   └── vaswani2017attention-fulltext.md  # 论文原文（LLM 可直接读）
├── books/         # 人工读书笔记 或 图书章节
│   ├── goodfellow2016deep-ch1-notes.md   # 人工笔记
│   └── goodfellow2016deep-fulltext.md    # 图书全文
├── materials/     # 人收集的研究资料
│   ├── interview-prof-zhang-2024-06.md
│   └── field-notes-siteA-spring.md
└── bib/           # BibTeX 文件（可含多条）
    └── references.bib
```

**优先级**：人工笔记 > LLM 阅读。两者共存 → 交叉验证。

> 三条路径（A/B/C）的详细处理步骤见 `skills/references/ingest-paths.md`。`ingest` 和 `compile` skill 均引用此文件。

## 知识卡目录命名

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 论文 | BibTeX citekey | `vaswani2017attention` |
| 理论 | kebab-case | `self-attention-mechanism` |
| 图书 | BibTeX citekey | `goodfellow2016deep` |
| 信息 | kebab-case + 日期 | `interview-zhang-202406` |

## 脚本调用约定

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/<script_name>.py" <args>
```

前置检查 Python 3.8+。

## 模板文件

位于 `${CLAUDE_PLUGIN_ROOT}/templates/`。

## 错误处理

- **kb_path 未配置** → 触发首次配置引导
- **Python 不可用** → 手动执行逻辑
- **知识库目录不存在** → 提示 `/scholar-assistant:init-kb`
- **BibTeX 解析失败** → 要求手动提供 author/title/year
- **wiki/ 已存在且人工笔记未更新** → 不覆盖
- **LLM 阅读与人工笔记冲突** → 标记 `trust: review-needed`，以人工为准
