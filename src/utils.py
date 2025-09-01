# utils_markdown.py
import re
from typing import List, Dict
from html import unescape

MERMAID_BLOCK_RE = re.compile(
    r"""
    (?:^|\n)                   # start of string or a newline
    (?P<indent>[ \t]*)         # optional indentation (captured to match close)
    (?P<fence>`{3,}|~{3,})     # fence of 3+ backticks or tildes
    [ \t]*mermaid\b[^\n]*\n    # 'mermaid' (case-insensitive) + rest of line
    (?P<body>.*?)              # the body of the mermaid block, non-greedy
    (?:\n(?P=indent)(?P=fence)[ \t]*(?=\r?\n|$))  # closing fence w/ same indent & chars
    """,
    re.IGNORECASE | re.DOTALL | re.VERBOSE,
)


def split_markdown_into_segments(md: str) -> list[dict[str, str]]:
    segments: list[dict[str, str]] = []
    last_end = 0

    for match in MERMAID_BLOCK_RE.finditer(md):
        start, end = match.span()

        if start > last_end:
            segments.append({"type": "text", "content": md[last_end:start]})

        code = match.group("body").strip("\n")
        segments.append({"type": "mermaid", "content": code})

        last_end = end

    if last_end < len(md):
        segments.append({"type": "text", "content": md[last_end:]})

    return segments


def fix_escaped_html_tags(mermaid_code: str) -> str:
    # Replace common escaped HTML entities
    # replacements = {
    #     r'--&gt;': '-->',
    #     r'--&gt;&gt;': '-->>',
    #     r'--&lt;': '--<',
    #     r'&lt;--': '<--',
    #     r'&lt;--&lt;': '<<--',
    #     r'&gt;': '>',
    #     r'&lt;': '<',
    #     r'&amp;': '&',
    # }
 
    # for pattern, replacement in replacements.items():
    #     mermaid_code = re.sub(pattern, replacement, mermaid_code)
 
    return unescape(mermaid_code)