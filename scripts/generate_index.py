#!/usr/bin/env python3
"""
索引自动生成脚本。
扫描 wiki/ 目录下的知识卡，自动更新 indexes/ 中的索引文件。
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path


def scan_papers(wiki_path: str) -> list:
    """扫描论文知识卡"""
    papers_dir = os.path.join(wiki_path, "papers")
    papers = []
    if not os.path.isdir(papers_dir):
        return papers

    for citekey in os.listdir(papers_dir):
        card_dir = os.path.join(papers_dir, citekey)
        if not os.path.isdir(card_dir):
            continue
        bib_path = os.path.join(card_dir, "reference.bib")
        skill_path = os.path.join(card_dir, "SKILL.md")

        entry = {"citekey": citekey, "title": citekey, "authors": "", "year": ""}

        # 读取 BibTeX
        if os.path.isfile(bib_path):
            with open(bib_path, 'r', encoding='utf-8') as f:
                content = f.read()
            import re
            title_m = re.search(r'title\s*=\s*\{(.+?)\}', content, re.DOTALL)
            author_m = re.search(r'author\s*=\s*\{(.+?)\}', content, re.DOTALL)
            year_m = re.search(r'year\s*=\s*\{(.+?)\}', content)
            if title_m:
                entry["title"] = re.sub(r'\s+', ' ', title_m.group(1)).strip()
            if author_m:
                entry["authors"] = author_m.group(1)
            if year_m:
                entry["year"] = year_m.group(1)

        # 读取 SKILL.md frontmatter
        if os.path.isfile(skill_path):
            with open(skill_path, 'r', encoding='utf-8') as f:
                skill_content = f.read()
            keywords_m = re.search(r'keywords:\s*\[(.+?)\]', skill_content)
            if keywords_m:
                entry["keywords"] = [k.strip().strip('"\'') for k in keywords_m.group(1).split(",")]

        papers.append(entry)

    return sorted(papers, key=lambda x: x.get("year", ""), reverse=True)


def scan_theories(wiki_path: str) -> list:
    """扫描理论/方法工具卡"""
    theories_dir = os.path.join(wiki_path, "theories")
    theories = []
    if not os.path.isdir(theories_dir):
        return theories

    for tid in os.listdir(theories_dir):
        card_dir = os.path.join(theories_dir, tid)
        if not os.path.isdir(card_dir):
            continue
        meta_path = os.path.join(card_dir, "meta.json")
        if os.path.isfile(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            theories.append({
                "id": tid,
                "name": meta.get("name", tid),
                "category": meta.get("category", "未分类"),
                "description": meta.get("description", ""),
                "papers": meta.get("papers", []),
                "related_theories": meta.get("related_theories", []),
            })
    return sorted(theories, key=lambda x: x.get("category", ""))


def scan_books(wiki_path: str) -> list:
    """扫描图书知识卡"""
    books_dir = os.path.join(wiki_path, "books")
    books = []
    if not os.path.isdir(books_dir):
        return books

    for citekey in os.listdir(books_dir):
        card_dir = os.path.join(books_dir, citekey)
        if not os.path.isdir(card_dir):
            continue
        bib_path = os.path.join(card_dir, "reference.bib")
        entry = {"citekey": citekey, "title": citekey, "authors": "", "year": ""}
        if os.path.isfile(bib_path):
            with open(bib_path, 'r', encoding='utf-8') as f:
                content = f.read()
            import re
            title_m = re.search(r'title\s*=\s*\{(.+?)\}', content, re.DOTALL)
            author_m = re.search(r'author\s*=\s*\{(.+?)\}', content, re.DOTALL)
            year_m = re.search(r'year\s*=\s*\{(.+?)\}', content)
            if title_m:
                entry["title"] = re.sub(r'\s+', ' ', title_m.group(1)).strip()
            if author_m:
                entry["authors"] = author_m.group(1)
            if year_m:
                entry["year"] = year_m.group(1)
        books.append(entry)
    return sorted(books, key=lambda x: x.get("year", ""), reverse=True)


def scan_info(wiki_path: str) -> list:
    """扫描信息知识卡"""
    info_dir = os.path.join(wiki_path, "info")
    info_list = []
    if not os.path.isdir(info_dir):
        return info_list

    for iid in os.listdir(info_dir):
        card_dir = os.path.join(info_dir, iid)
        if not os.path.isdir(card_dir):
            continue
        meta_path = os.path.join(card_dir, "meta.json")
        if os.path.isfile(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            info_list.append({
                "id": iid,
                "name": meta.get("name", iid),
                "type": meta.get("type", "其他"),
                "tags": meta.get("tags", []),
            })
    return sorted(info_list, key=lambda x: x.get("type", ""))


def generate_all_indexes(wiki_path: str):
    """生成所有索引文件"""
    indexes_dir = os.path.join(wiki_path, "indexes")
    os.makedirs(indexes_dir, exist_ok=True)
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- 论文索引 ---
    papers = scan_papers(wiki_path)
    lines = [
        "# 论文索引",
        "",
        f"> 最后更新: {t}",
        f"> 论文数: {len(papers)}",
        "",
    ]
    # 按年份分组
    by_year = {}
    for p in papers:
        y = p.get("year", "未知")
        by_year.setdefault(y, []).append(p)
    for y in sorted(by_year, reverse=True):
        lines.append(f"## {y}")
        for p in by_year[y]:
            lines.append(f"- **[{p['citekey']}](papers/{p['citekey']}/SKILL.md)** — {p['title']}")
            if p.get("authors"):
                lines.append(f"  *{p['authors']}*")
        lines.append("")
    with open(os.path.join(indexes_dir, "all-papers.md"), 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    # --- 理论索引 ---
    theories = scan_theories(wiki_path)
    lines = [
        "# 理论/方法工具索引",
        "",
        f"> 最后更新: {t}",
        f"> 总计: {len(theories)}",
        "",
    ]
    by_cat = {}
    for th in theories:
        cat = th.get("category", "未分类")
        by_cat.setdefault(cat, []).append(th)
    for cat in sorted(by_cat):
        lines.append(f"## {cat}")
        for th in by_cat[cat]:
            lines.append(f"- **[{th['name']}](theories/{th['id']}/SKILL.md)** — {th['description'][:100]}")
            if th.get("papers"):
                lines.append(f"  📄 论文: {', '.join(th['papers'])}")
        lines.append("")
    with open(os.path.join(indexes_dir, "all-theories.md"), 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    # --- 图书索引 ---
    books = scan_books(wiki_path)
    lines = [
        "# 图书索引",
        "",
        f"> 最后更新: {t}",
        f"> 图书数: {len(books)}",
        "",
    ]
    for b in books:
        lines.append(f"- **[{b['citekey']}](books/{b['citekey']}/SKILL.md)** — {b['title']}")
        if b.get("authors"):
            lines.append(f"  *{b['authors']}* ({b.get('year', '')})")
    with open(os.path.join(indexes_dir, "all-books.md"), 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    # --- 信息卡索引 ---
    info_list = scan_info(wiki_path)
    lines = [
        "# 信息知识卡索引",
        "",
        f"> 最后更新: {t}",
        f"> 总计: {len(info_list)}",
        "",
    ]
    by_type = {}
    for inf in info_list:
        tp = inf.get("type", "其他")
        by_type.setdefault(tp, []).append(inf)
    for tp in sorted(by_type):
        lines.append(f"## {tp}")
        for inf in by_type[tp]:
            tags_str = ", ".join(inf.get("tags", []))
            lines.append(f"- **[{inf['name']}](info/{inf['id']}/SKILL.md)** — {tags_str}")
        lines.append("")
    with open(os.path.join(indexes_dir, "all-info.md"), 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"✅ 索引已更新: {indexes_dir}")


def main():
    parser = argparse.ArgumentParser(description="生成知识库索引文件")
    parser.add_argument("wiki_path", nargs="?", default="./knowledge-base/wiki/",
                        help="wiki 目录路径")
    args = parser.parse_args()
    generate_all_indexes(os.path.abspath(args.wiki_path))


if __name__ == "__main__":
    main()
