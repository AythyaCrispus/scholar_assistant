#!/usr/bin/env python3
"""
知识库目录结构初始化脚本。
在用户指定的知识库根目录下创建三层架构（raw/ + wiki/ + outputs/）。
"""

import os
import argparse
from datetime import datetime


def create_dir(path):
    """创建目录（如果不存在）"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"  [创建] {path}")
    else:
        print(f"  [已存在] {path}")


def write_file(path, content):
    """写入文件（如果不存在）"""
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [创建] {path}")
    else:
        print(f"  [已存在] {path}")


def init_knowledge_base(kb_root):
    """初始化知识库目录结构"""
    print(f"\n正在初始化知识库: {kb_root}\n")

    create_dir(kb_root)

    # ==================== raw/ 原始资料目录 ====================
    create_dir(os.path.join(kb_root, "raw"))
    create_dir(os.path.join(kb_root, "raw", "papers"))
    create_dir(os.path.join(kb_root, "raw", "books"))
    create_dir(os.path.join(kb_root, "raw", "materials"))

    # ==================== wiki/ 编译产物目录 ====================
    create_dir(os.path.join(kb_root, "wiki"))
    create_dir(os.path.join(kb_root, "wiki", "indexes"))
    create_dir(os.path.join(kb_root, "wiki", "papers"))
    create_dir(os.path.join(kb_root, "wiki", "theories"))
    create_dir(os.path.join(kb_root, "wiki", "books"))
    create_dir(os.path.join(kb_root, "wiki", "info"))

    # ==================== outputs/ 运行时输出 ====================
    create_dir(os.path.join(kb_root, "outputs"))
    create_dir(os.path.join(kb_root, "outputs", "drafts"))
    create_dir(os.path.join(kb_root, "outputs", "outlines"))
    create_dir(os.path.join(kb_root, "outputs", "health"))

    # ==================== .claude/ 规则目录 ====================
    create_dir(os.path.join(kb_root, ".claude"))
    create_dir(os.path.join(kb_root, ".claude", "rules"))

    # ==================== 初始索引文件 ====================
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    write_file(os.path.join(kb_root, "wiki", "indexes", "all-papers.md"),
        f"# 论文索引\n\n> 最后更新: {t}\n> 此文件由 scholar-assistant 插件自动维护\n\n## 论文列表\n\n暂无。使用 `/scholar-assistant:ingest` 添加论文。\n\n## 按主题\n\n（待填充）\n\n## 按年份\n\n（待填充）\n")

    write_file(os.path.join(kb_root, "wiki", "indexes", "all-theories.md"),
        f"# 理论/方法工具索引\n\n> 最后更新: {t}\n> 此文件由 scholar-assistant 插件自动维护\n\n## 理论/方法列表\n\n暂无。使用 `/scholar-assistant:ingest` 添加。\n\n## 按类别\n\n- 统计方法\n- 机器学习\n- 形式逻辑\n- 优化方法\n- 因果推断\n- 自然语言处理\n- 计算机视觉\n- 其他\n")

    write_file(os.path.join(kb_root, "wiki", "indexes", "all-books.md"),
        f"# 图书索引\n\n> 最后更新: {t}\n> 由 scholar-assistant 插件自动维护\n\n## 图书列表\n\n暂无。使用 `/scholar-assistant:ingest` 添加图书。\n\n## 按学科\n\n（待填充）\n")

    write_file(os.path.join(kb_root, "wiki", "indexes", "all-info.md"),
        f"# 信息知识卡索引\n\n> 最后更新: {t}\n> 由 scholar-assistant 插件自动维护\n\n## 信息卡列表\n\n暂无。使用 `/scholar-assistant:ingest` 添加信息资料。\n\n## 按类型\n\n- 实验数据\n- 田野笔记\n- 访谈记录\n- 统计资料\n- 其他\n")

    write_file(os.path.join(kb_root, ".claude", "rules", "scholar-assistant.md"),
        f"# 学术写作助手规则\n\n> 初始化: {t}\n\n## 知识库结构\n\n| 目录 | 用途 | 修改权限 |\n|------|------|---------|\n| `raw/` | 原始资料 | 只进不改 |\n| `wiki/` | 编译产物 | LLM 维护 |\n| `outputs/` | 运行时输出 | 自动生成 |\n\n## 四类知识卡\n\n1. **论文卡** `wiki/papers/<citekey>/`: reference.bib + fulltext.md + SKILL.md\n2. **理论卡** `wiki/theories/<id>/`: meta.json + detail.md + SKILL.md\n3. **图书卡** `wiki/books/<citekey>/`: reference.bib + book.md + SKILL.md\n4. **信息卡** `wiki/info/<id>/`: meta.json + content.md + SKILL.md\n\n## 核心命令\n\n| 命令 | 用途 |\n|------|------|\n| `/scholar-assistant:init-kb` | 初始化知识库 |\n| `/scholar-assistant:ingest` | 摄入新知识 |\n| `/scholar-assistant:compile` | 编译知识库 |\n| `/scholar-assistant:search-kb` | 检索知识 |\n| `/scholar-assistant:write-paper` | 学术写作 |\n| `/scholar-assistant:lint-kb` | 健康检查 |\n")

    write_file(os.path.join(kb_root, ".gitignore"),
        "# 知识库 gitignore\n# raw/ 和 outputs/ 可按需纳入版本控制\noutputs/drafts/\noutputs/outlines/\noutputs/health/\n*.tmp\n*.bak\n~*\n")

    print(f"\n✅ 知识库初始化完成! {os.path.abspath(kb_root)}")
    print("\n📖 下一步: 使用 /scholar-assistant:ingest 开始摄入知识")
    return kb_root


def main():
    parser = argparse.ArgumentParser(description="初始化 scholar-assistant 知识库目录结构")
    parser.add_argument("kb_path", nargs="?", default="./knowledge-base/",
                        help="知识库根目录（默认 ./knowledge-base/）")
    args = parser.parse_args()
    kb_path = os.path.abspath(args.kb_path)
    init_knowledge_base(kb_path)


if __name__ == "__main__":
    main()
