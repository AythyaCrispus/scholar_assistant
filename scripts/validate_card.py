#!/usr/bin/env python3
"""
知识卡完整性校验脚本。
检查每张知识卡的必选文件和必填字段。
"""

import os
import json
import argparse
from typing import List, Tuple


REQUIRED_PAPER_FILES = ["reference.bib", "fulltext.md", "SKILL.md"]
REQUIRED_THEORY_FILES = ["meta.json", "detail.md", "SKILL.md"]
REQUIRED_BOOK_FILES = ["reference.bib", "book.md", "SKILL.md"]
REQUIRED_INFO_FILES = ["meta.json", "content.md", "SKILL.md"]

REQUIRED_THEORY_META_FIELDS = ["name", "description", "call_conditions", "papers"]
REQUIRED_INFO_META_FIELDS = ["name", "description", "type", "source"]


def check_file_exists(path: str) -> bool:
    return os.path.isfile(path)


def check_json_file(path: str) -> Tuple[bool, str]:
    """检查 JSON 文件是否可解析"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, "OK"
    except json.JSONDecodeError as e:
        return False, f"JSON 解析错误: {e}"
    except FileNotFoundError:
        return False, "文件不存在"
    except Exception as e:
        return False, str(e)


def validate_paper_card(card_dir: str, citekey: str) -> List[str]:
    """校验论文知识卡"""
    issues = []
    for filename in REQUIRED_PAPER_FILES:
        path = os.path.join(card_dir, filename)
        if not check_file_exists(path):
            issues.append(f"[缺失] {citekey}: 缺少 {filename}")
        elif filename == "SKILL.md":
            if os.path.getsize(path) < 50:
                issues.append(f"[内容过短] {citekey}: SKILL.md 内容不足")
    return issues


def validate_theory_card(card_dir: str, tid: str) -> List[str]:
    """校验理论工具卡"""
    issues = []
    for filename in REQUIRED_THEORY_FILES:
        path = os.path.join(card_dir, filename)
        if not check_file_exists(path):
            issues.append(f"[缺失] {tid}: 缺少 {filename}")
            continue

    # 校验 meta.json 必填字段
    meta_path = os.path.join(card_dir, "meta.json")
    if check_file_exists(meta_path):
        ok, msg = check_json_file(meta_path)
        if not ok:
            issues.append(f"[格式错误] {tid}: meta.json - {msg}")
        else:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            for field in REQUIRED_THEORY_META_FIELDS:
                if field not in meta:
                    issues.append(f"[缺少字段] {tid}: meta.json 缺少 '{field}'")
    return issues


def validate_book_card(card_dir: str, citekey: str) -> List[str]:
    """校验图书知识卡"""
    issues = []
    for filename in REQUIRED_BOOK_FILES:
        path = os.path.join(card_dir, filename)
        if not check_file_exists(path):
            issues.append(f"[缺失] {citekey}: 缺少 {filename}")
        elif filename == "SKILL.md":
            if os.path.getsize(path) < 50:
                issues.append(f"[内容过短] {citekey}: SKILL.md 内容不足")
    return issues


def validate_info_card(card_dir: str, iid: str) -> List[str]:
    """校验信息知识卡"""
    issues = []
    for filename in REQUIRED_INFO_FILES:
        path = os.path.join(card_dir, filename)
        if not check_file_exists(path):
            issues.append(f"[缺失] {iid}: 缺少 {filename}")

    meta_path = os.path.join(card_dir, "meta.json")
    if check_file_exists(meta_path):
        ok, msg = check_json_file(meta_path)
        if not ok:
            issues.append(f"[格式错误] {iid}: meta.json - {msg}")
        else:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            for field in REQUIRED_INFO_META_FIELDS:
                if field not in meta:
                    issues.append(f"[缺少字段] {iid}: meta.json 缺少 '{field}'")
    return issues


def validate_all(wiki_path: str) -> List[str]:
    """校验所有知识卡"""
    all_issues = []

    # 论文卡
    papers_dir = os.path.join(wiki_path, "papers")
    if os.path.isdir(papers_dir):
        for citekey in os.listdir(papers_dir):
            card_dir = os.path.join(papers_dir, citekey)
            if os.path.isdir(card_dir):
                all_issues.extend(validate_paper_card(card_dir, citekey))

    # 理论卡
    theories_dir = os.path.join(wiki_path, "theories")
    if os.path.isdir(theories_dir):
        for tid in os.listdir(theories_dir):
            card_dir = os.path.join(theories_dir, tid)
            if os.path.isdir(card_dir):
                all_issues.extend(validate_theory_card(card_dir, tid))

    # 图书卡
    books_dir = os.path.join(wiki_path, "books")
    if os.path.isdir(books_dir):
        for citekey in os.listdir(books_dir):
            card_dir = os.path.join(books_dir, citekey)
            if os.path.isdir(card_dir):
                all_issues.extend(validate_book_card(card_dir, citekey))

    # 信息卡
    info_dir = os.path.join(wiki_path, "info")
    if os.path.isdir(info_dir):
        for iid in os.listdir(info_dir):
            card_dir = os.path.join(info_dir, iid)
            if os.path.isdir(card_dir):
                all_issues.extend(validate_info_card(card_dir, iid))

    return all_issues


def check_cross_references(wiki_path: str) -> List[str]:
    """检查交叉引用的完整性"""
    issues = []

    # 收集所有已知的 citekey 和 theory-id
    papers = set()
    books = set()
    theories = set()

    papers_dir = os.path.join(wiki_path, "papers")
    if os.path.isdir(papers_dir):
        papers = {d for d in os.listdir(papers_dir) if os.path.isdir(os.path.join(papers_dir, d))}

    books_dir = os.path.join(wiki_path, "books")
    if os.path.isdir(books_dir):
        books = {d for d in os.listdir(books_dir) if os.path.isdir(os.path.join(books_dir, d))}

    theories_dir = os.path.join(wiki_path, "theories")
    if os.path.isdir(theories_dir):
        theories = {d for d in os.listdir(theories_dir) if os.path.isdir(os.path.join(theories_dir, d))}

    # 检查理论卡中的论文引用
    if os.path.isdir(theories_dir):
        for tid in theories:
            meta_path = os.path.join(theories_dir, tid, "meta.json")
            if os.path.isfile(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                for ref in meta.get("papers", []):
                    if ref not in papers and ref not in books:
                        issues.append(f"[死链] 理论 '{tid}' 引用了不存在的论文: '{ref}'")

    return issues


def main():
    parser = argparse.ArgumentParser(description="校验知识卡完整性")
    parser.add_argument("wiki_path", nargs="?", default="./knowledge-base/wiki/",
                        help="wiki 目录路径")
    parser.add_argument("--cross-ref", action="store_true",
                        help="同时检查交叉引用完整性")
    args = parser.parse_args()

    wiki_path = os.path.abspath(args.wiki_path)
    print(f"正在校验: {wiki_path}\n")

    issues = validate_all(wiki_path)

    if args.cross_ref:
        issues.extend(check_cross_references(wiki_path))

    if not issues:
        print("✅ 所有知识卡校验通过，没有发现问题。")
    else:
        print(f"⚠️  发现 {len(issues)} 个问题：\n")
        for issue in sorted(issues):
            print(f"  {issue}")

    print(f"\n📊 统计:")
    for label, d in [("论文", "papers"), ("理论", "theories"), ("图书", "books"), ("信息", "info")]:
        d_path = os.path.join(wiki_path, d)
        count = 0
        if os.path.isdir(d_path):
            count = sum(1 for x in os.listdir(d_path) if os.path.isdir(os.path.join(d_path, x)))
        print(f"  {label}知识卡: {count}")


if __name__ == "__main__":
    main()
