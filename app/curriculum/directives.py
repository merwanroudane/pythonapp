"""Parser for the lesson-body directive syntax (blueprint §80.3).

    :::concept title="..."
    Markdown body
    :::

    :::quiz id="q1":::          <- self-closing, data lives in lesson.yaml

Text outside directives becomes ``markdown`` blocks. Directives do not nest.
"""

from __future__ import annotations

import re

from app.curriculum.schema import Block

_OPEN = re.compile(r"^:::(?P<type>[a-z][a-z0-9_]*)(?P<attrs>[^\n]*?)(?P<close>:::)?\s*$")
_ATTR = re.compile(r'([a-z_][a-z0-9_]*)="([^"]*)"')


class DirectiveError(ValueError):
    pass


def parse_attrs(raw: str) -> dict[str, str]:
    return {key: value for key, value in _ATTR.findall(raw)}


def parse(text: str) -> list[Block]:
    blocks: list[Block] = []
    markdown: list[str] = []
    markdown_start = 1
    lines = text.splitlines()
    i = 0

    def flush_markdown() -> None:
        body = "\n".join(markdown).strip()
        if body:
            blocks.append(Block(type="markdown", body=body, line=markdown_start))
        markdown.clear()

    while i < len(lines):
        line = lines[i]
        match = _OPEN.match(line.strip()) if line.startswith(":::") else None
        if match is None or line.strip() == ":::":
            if line.strip() == ":::":
                raise DirectiveError(f"line {i + 1}: closing ':::' without an opening directive")
            if not markdown:
                markdown_start = i + 1
            markdown.append(line)
            i += 1
            continue

        flush_markdown()
        start = i + 1
        block_type = match["type"]
        attrs = parse_attrs(match["attrs"])
        if match["close"]:
            blocks.append(Block(type=block_type, attrs=attrs, line=start))
            i += 1
            continue

        body: list[str] = []
        i += 1
        while i < len(lines) and lines[i].rstrip() != ":::":
            if _OPEN.match(lines[i].strip()) and lines[i].startswith(":::"):
                raise DirectiveError(f"line {i + 1}: directive opened inside '{block_type}'")
            body.append(lines[i])
            i += 1
        if i >= len(lines):
            raise DirectiveError(f"line {start}: '{block_type}' is never closed with ':::'")
        blocks.append(
            Block(type=block_type, attrs=attrs, body="\n".join(body).strip("\n"), line=start)
        )
        i += 1

    flush_markdown()
    return blocks
