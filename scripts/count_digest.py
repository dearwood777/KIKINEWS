#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数一数最新一期日报有多少条（用于判断是否需要切换备用 API）。"""
import glob
import re
import sys
from datetime import date

ANCHOR = re.compile(r'<a id="item-')
TITLE = re.compile(r"^###\s*\[", re.M)


def latest_file() -> str | None:
    files = sorted(glob.glob("docs/_posts/*-summary-zh.md"))
    return files[-1] if files else None


def main() -> None:
    import os
    import time

    path = latest_file()
    if not path:
        print(0)
        return
    # 只认本轮刚生成的文件（2 小时内），避免把仓库里遗留的旧稿当成新产出
    if time.time() - os.path.getmtime(path) > 7200:
        print(0)
        return
    text = open(path, encoding="utf-8").read()
    n = max(len(TITLE.findall(text)), len(ANCHOR.findall(text)))
    print(n)


if __name__ == "__main__":
    main()
