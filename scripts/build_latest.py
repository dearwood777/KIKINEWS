#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 Horizon 生成的最新一期日报转成手机友好的单页 HTML。

输入：docs/_posts/YYYY-MM-DD-summary-<lang>.md（Horizon 自动写入）
输出：docs/latest.html / docs/latest-en.html   —— APK 直接加载这个地址
      docs/latest.json                          —— 版本信息，App 用来判断是否更新

只依赖 markdown 库，在 GitHub Actions 上 pip 安装即可。
"""
from __future__ import annotations

import glob
import json
import os
import re
from datetime import datetime, timezone

import markdown

DOCS = "docs"
POSTS = os.path.join(DOCS, "_posts")

TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#111318" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<title>{title}</title>
<style>
:root{{
  --bg:#ffffff; --fg:#16181d; --muted:#6b7280; --line:#e6e8ee;
  --card:#f7f8fa; --accent:#2f6bff;
}}
@media (prefers-color-scheme: dark){{
  :root{{
    --bg:#111318; --fg:#e7e9ee; --muted:#9aa3b2; --line:#242a35;
    --card:#171a21; --accent:#7aa2ff;
  }}
}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{
  margin:0; background:var(--bg); color:var(--fg);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",
              "Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:17px; line-height:1.75;
}}
.wrap{{max-width:760px;margin:0 auto;padding:0 18px 64px;
      padding-bottom:calc(64px + env(safe-area-inset-bottom));}}
header{{
  padding:26px 18px 18px;border-bottom:1px solid var(--line);margin-bottom:22px;
}}
h1.page{{font-size:20px;margin:0 0 6px;letter-spacing:.2px}}
.meta{{color:var(--muted);font-size:13px}}
article h1{{font-size:23px;line-height:1.4;margin:4px 0 14px}}
article h2{{font-size:19px;margin:30px 0 10px;padding-left:10px;
            border-left:3px solid var(--accent)}}
article h3{{font-size:17px;margin:22px 0 8px;color:var(--fg)}}
article p{{margin:0 0 14px}}
article a{{color:var(--accent);text-decoration:none;word-break:break-word}}
article ul,article ol{{padding-left:22px;margin:0 0 16px}}
article li{{margin:0 0 8px}}
article blockquote{{margin:0 0 16px;padding:10px 14px;background:var(--card);
                   border-left:3px solid var(--line);color:var(--muted);font-size:15px}}
article code{{background:var(--card);padding:2px 6px;border-radius:5px;font-size:14px}}
article pre{{background:var(--card);padding:12px;border-radius:10px;overflow-x:auto}}
article table{{width:100%;border-collapse:collapse;margin:0 0 16px;font-size:15px}}
article th,article td{{border:1px solid var(--line);padding:8px 10px;text-align:left}}
article img{{max-width:100%;height:auto;border-radius:10px}}
article hr{{border:0;border-top:1px solid var(--line);margin:28px 0}}
footer{{margin-top:40px;color:var(--muted);font-size:13px;text-align:center}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1 class="page">{header}</h1>
    <div class="meta">更新于 {updated} · Horizon 自动生成</div>
  </header>
  <article>
{body}
  </article>
  <footer>内容由 AI 筛选与撰写，可能有误，请以原文为准。</footer>
</div>
</body>
</html>
"""

FRONT_MATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.S)

MD_EXTENSIONS = ["extra", "tables", "sane_lists", "fenced_code", "nl2br"]


def newest_post(lang: str) -> str | None:
    files = sorted(glob.glob(os.path.join(POSTS, f"*-summary-{lang}.md")))
    return files[-1] if files else None


def render(path: str, lang: str, out_name: str) -> dict | None:
    raw = open(path, encoding="utf-8").read()
    raw = FRONT_MATTER.sub("", raw, count=1)
    title_day = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    day = title_day.group(1) if title_day else ""

    html = markdown.markdown(
        raw, extensions=MD_EXTENSIONS, output_format="html5"
    )
    header = "每日速递 · " + day if lang == "zh" else "Daily Digest · " + day
    page = TEMPLATE.format(
        lang="zh-CN" if lang == "zh" else "en",
        title=("Horizon 每日速递 " + day) if lang == "zh" else ("Horizon Daily " + day),
        header=header,
        updated=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        body=html,
    )
    with open(os.path.join(DOCS, out_name), "w", encoding="utf-8") as f:
        f.write(page)
    return {"lang": lang, "date": day, "file": out_name,
            "source": os.path.basename(path)}


def main() -> None:
    written = []
    for lang, out_name in (("zh", "latest.html"), ("en", "latest-en.html")):
        p = newest_post(lang)
        if not p:
            print(f"[skip] no post for lang={lang}")
            continue
        info = render(p, lang, out_name)
        written.append(info)
        print(f"[ok] {out_name} <= {info['source']} ({info['date']})")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "items": written,
    }
    with open(os.path.join(DOCS, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("[ok] latest.json")


if __name__ == "__main__":
    main()
