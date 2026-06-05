#!/usr/bin/env python3
"""
BibTeX 解析工具。
解析标准 BibTeX 条目，支持结构化输出和多种引用格式。
"""

import re
import json
import sys
import argparse
from typing import Dict, List, Optional


def parse_bibtex_entry(entry_text: str) -> Optional[Dict]:
    """解析单个 BibTeX 条目"""
    type_match = re.match(r'@(\w+)\s*\{\s*([^,]+),', entry_text.strip())
    if not type_match:
        return None

    entry_type = type_match.group(1).lower()
    citekey = type_match.group(2).strip()
    result = {"type": entry_type, "citekey": citekey}

    field_pattern = re.compile(
        r'(\w+)\s*=\s*(\{((?:[^{}]|\{[^{}]*\})*)\}|\"((?:[^\"\\]|\\.)*)\")',
        re.DOTALL
    )

    fields_text = entry_text[type_match.end():]
    for match in field_pattern.finditer(fields_text):
        field_name = match.group(1).lower()
        field_value = match.group(3) if match.group(3) is not None else match.group(4)
        if field_value:
            field_value = re.sub(r'\s+', ' ', field_value).strip()
            result[field_name] = field_value

    return result


def parse_bibtex_file(filepath: str) -> List[Dict]:
    """解析整个 BibTeX 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = []
    raw_entries = re.split(r'(?=@\w+\s*\{)', content)
    for raw in raw_entries:
        raw = raw.strip()
        if not raw:
            continue
        entry = parse_bibtex_entry(raw)
        if entry:
            entries.append(entry)

    return entries


def format_apa(entry: Dict) -> str:
    """APA 格式引用"""
    authors = entry.get("author", "Unknown Author")
    year = entry.get("year", "n.d.")
    title = entry.get("title", "Untitled")
    journal = entry.get("journal", "")
    booktitle = entry.get("booktitle", "")
    publisher = entry.get("publisher", "")
    volume = entry.get("volume", "")
    number = entry.get("number", "")
    pages = entry.get("pages", "")
    doi = entry.get("doi", "")

    author_list = [a.strip() for a in authors.split(" and ")]
    if len(author_list) >= 3:
        author_str = f"{author_list[0].split(',')[0].strip()} et al."
    elif len(author_list) == 2:
        a1, a2 = author_list[0].split(",")[0].strip(), author_list[1].split(",")[0].strip()
        author_str = f"{a1} & {a2}"
    else:
        author_str = author_list[0].split(",")[0].strip()

    result = f"{author_str} ({year}). {title}."

    if entry["type"] == "article" and journal:
        result += f" *{journal}*"
        if volume:
            result += f", {volume}"
            if number:
                result += f"({number})"
        if pages:
            result += f", {pages}"

    elif entry["type"] == "book":
        if publisher:
            result += f" {publisher}."

    elif entry["type"] in ("inproceedings", "incollection"):
        if booktitle:
            result += f" In *{booktitle}*"
        if pages:
            result += f" (pp. {pages})"
        if publisher:
            result += f". {publisher}"

    if doi:
        result += f" https://doi.org/{doi}"

    return result


def format_gb7714(entry: Dict) -> str:
    """GB/T 7714 格式引用（中文常用）"""
    authors = entry.get("author", "Unknown Author")
    year = entry.get("year", "n.d.")
    title = entry.get("title", "Untitled")
    journal = entry.get("journal", "")
    volume = entry.get("volume", "")
    number = entry.get("number", "")
    pages = entry.get("pages", "")

    author_list = [a.strip() for a in authors.split(" and ")]
    if len(author_list) <= 3:
        author_str = ", ".join(a.split(",")[0].strip() for a in author_list)
    else:
        author_str = ", ".join(a.split(",")[0].strip() for a in author_list[:3]) + ", et al."

    result = f"{author_str}. {title}[J]."
    if journal:
        result += f" {journal},"
    result += f" {year}"
    if volume:
        result += f", {volume}"
        if number:
            result += f"({number})"
    if pages:
        result += f": {pages}"
    return result


def format_mla(entry: Dict) -> str:
    """MLA 格式引用"""
    authors = entry.get("author", "Unknown Author")
    title = entry.get("title", "Untitled")
    journal = entry.get("journal", "")
    year = entry.get("year", "n.d.")
    pages = entry.get("pages", "")

    author_list = [a.strip() for a in authors.split(" and ")]
    if len(author_list) >= 3:
        author_str = f"{author_list[0].split(',')[0].strip()}, et al."
    elif len(author_list) == 2:
        a1, a2 = author_list[0].split(",")[0].strip(), author_list[1].split(",")[0].strip()
        author_str = f"{a1}, and {a2}"
    else:
        author_str = author_list[0].split(",")[0].strip()

    result = f'{author_str}. "{title}."'
    if journal:
        result += f" *{journal}*"
    result += f", {year}"
    if pages:
        result += f", pp. {pages}"
    return result


def format_citation(entry: Dict, style: str = "APA") -> str:
    """根据风格生成格式化引用"""
    formatters = {"APA": format_apa, "MLA": format_mla, "GB7714": format_gb7714}
    return formatters.get(style, format_apa)(entry)


def entry_to_bib(entry: Dict) -> str:
    """将条目还原为 BibTeX"""
    lines = [f"@{entry['type']}{{{entry['citekey']},"]
    for key, value in entry.items():
        if key in ("type", "citekey"):
            continue
        lines.append(f"  {key} = {{{value}}},")
    lines.append("}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="解析 BibTeX 文件并输出结构化信息")
    parser.add_argument("bibtex_file", help="BibTeX 文件路径")
    parser.add_argument("--format", choices=["json", "citation", "bib"], default="json",
                        help="输出格式: json/citation/bib")
    parser.add_argument("--style", choices=["APA", "MLA", "GB7714"], default="APA",
                        help="引用格式")
    parser.add_argument("--citekey", help="仅输出指定 citekey 的条目")
    args = parser.parse_args()

    try:
        entries = parse_bibtex_file(args.bibtex_file)
    except FileNotFoundError:
        print(f"文件不存在: {args.bibtex_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    if args.citekey:
        entries = [e for e in entries if e["citekey"] == args.citekey]

    if args.format == "json":
        print(json.dumps(entries, ensure_ascii=False, indent=2))
    elif args.format == "citation":
        for entry in entries:
            print(format_citation(entry, args.style))
            print()
    elif args.format == "bib":
        for entry in entries:
            print(entry_to_bib(entry))
            print()


if __name__ == "__main__":
    main()
