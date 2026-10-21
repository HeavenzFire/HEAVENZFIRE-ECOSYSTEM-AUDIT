#!/usr/bin/env python3
"""Validate local Markdown links and image paths without network access."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"!??\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")
CODE_RE = re.compile(r"(`{3,}|~{3,})")


def strip_code_fences(text: str) -> str:
    output: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = CODE_RE.match(line.lstrip())
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker[0]
            elif marker[0] == fence:
                fence = None
            output.append("")
        elif fence is None:
            output.append(line)
        else:
            output.append("")
    return "\n".join(output)


def main() -> int:
    failures: list[str] = []
    ignored_dirs = {".git", ".venv", "node_modules"}
    markdown_files = sorted(
        path for path in ROOT.rglob("*.md")
        if not any(part in ignored_dirs for part in path.relative_to(ROOT).parts)
    )

    for source in markdown_files:
        text = strip_code_fences(source.read_text(encoding="utf-8"))
        for match in LINK_RE.finditer(text):
            target = match.group(1) or match.group(2) or ""
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("//") or not parsed.path:
                continue
            candidate = (source.parent / unquote(parsed.path)).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                failures.append(f"{source.relative_to(ROOT)}: link escapes repository: {target}")
                continue
            if not candidate.exists():
                failures.append(f"{source.relative_to(ROOT)}: missing local target: {target}")

    if failures:
        print("Documentation validation failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print(f"Documentation validation passed: {len(markdown_files)} Markdown file(s) checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
