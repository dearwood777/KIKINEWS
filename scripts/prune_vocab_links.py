# -*- coding: utf-8 -*-
"""正文页锚点守卫：只保留 vocab_manifest.json 里确实存在的词锚点。

早前删词后正文页仍链到已删除的锚点，点进去跳空。这个脚本放在 build_latest
之后跑，自动把失效的 ``<a class="vw" href="vocab.html#w-xxx">word</a>``
还原成普通文字；也可以在文章页已发布后单独拿线上 HTML 跑一遍。
用法：python scripts/prune_vocab_links.py [docs/latest.html docs/latest-en.html]
"""
from __future__ import annotations

import json
import os
import re
import sys

DOCS = "docs"
LINK = re.compile(r'<a class="vw" href="vocab\.html#([\w-]+)">(.*?)</a>')


def vocab_ids() -> set[str]:
    path = os.path.join(DOCS, "vocab_manifest.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return set()
    return {str(t.get("id") or "") for t in data.get("terms") or [] if isinstance(t, dict)}


def prune(html: str, ids: set[str]) -> tuple[str, int]:
    """返回 (修剪后的 HTML, 去掉的失效锚点条数)。"""
    removed = 0
    if not ids:
        return html, 0

    def repl(match: re.Match) -> str:
        nonlocal removed
        if match.group(1) in ids:
            return match.group(0)
        removed += 1
        return match.group(2)

    return LINK.sub(repl, html), removed


def main() -> None:
    ids = vocab_ids()
    if not ids:
        print("[skip] vocab_manifest.json 缺失或为空，不做锚点修剪")
        return
    targets = sys.argv[1:] or [os.path.join(DOCS, "latest.html"), os.path.join(DOCS, "latest-en.html")]
    for path in targets:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            html = f.read()
        out, removed = prune(html, ids)
        if removed:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(out)
            print(f"[ok] {os.path.basename(path)}: 去掉 {removed} 个失效词锚点")
        else:
            print(f"[ok] {os.path.basename(path)}: 锚点全部有效")


if __name__ == "__main__":
    main()
