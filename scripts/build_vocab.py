#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从当天这期日报里挑出“难点词汇”，生成 docs/vocab.html（附中文释义）。

全过程只用本地词库（ECDICT，英汉双解 CSV）做查表和规则判断，不调用任何模型，
因此不消耗任何 API token，也不会改变日报内容本身。

用法（在仓库根目录执行）：
    python scripts/build_vocab.py
词库位置：默认 data/ecdict.csv，可用环境变量 ECDICT_PATH 覆盖。
"""
from __future__ import annotations

import csv
import html
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_latest import DOCS, POSTS  # noqa: E402

FRONT_MATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.S)
LINK_MD = re.compile(r"\[([^\]]*)\]\([^)]*\)")
TOKEN = re.compile(r"[A-Za-z][A-Za-z'\-]{2,}")

# 太常见的功能词，任何词表都不该收
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "have", "has", "had", "was", "were",
    "are", "been", "will", "would", "could", "should", "there", "their", "them", "they", "his",
    "her", "its", "our", "your", "who", "what", "when", "where", "which", "while", "about",
    "into", "over", "than", "then", "also", "such", "some", "more", "most", "much", "many",
    "very", "just", "only", "even", "still", "after", "before", "during", "between", "under",
    "because", "however", "therefore", "according", "said", "says", "say", "one", "two", "new",
    "now", "now", "get", "got", "make", "made", "use", "used", "using", "may", "might", "must",
    "can", "not", "but", "you", "all", "any", "out", "off", "own", "same", "other", "these",
}

MAX_WORDS = 80


def newest_post(lang: str = "en") -> str | None:
    if not os.path.isdir(POSTS):
        return None
    files = [f for f in os.listdir(POSTS) if f.endswith(f"-summary-{lang}.md")]
    if not files:
        return None
    files.sort()
    return os.path.join(POSTS, files[-1])


def read_prose(path: str) -> str:
    text = open(path, encoding="utf-8").read()
    text = FRONT_MATTER.sub("", text)
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s == "---":
            continue
        if s.startswith("title:") or s.startswith("layout:") or s.startswith("date:"):
            continue
        if re.match(r"^\*\*(?:标签|Tags|Tag)\*\*", s):
            continue
        if s.startswith("<details") or s.startswith("</details"):
            continue
        if s.startswith("### ") or s.startswith("**") and s.endswith("**"):
            continue
        if s.startswith("> "):
            s = s[2:]
        lines.append(LINK_MD.sub(r"\1", s))
    return "\n".join(lines)


def candidates_from(text: str) -> set[str]:
    words = set()
    for m in TOKEN.finditer(text):
        w = m.group(0).strip("'-").lower()
        if len(w) < 4 or w in STOPWORDS:
            continue
        words.add(w)
        # 简单变形还原，命中就一起查
        for suf, cut in (("ing", 3), ("ied", 3), ("ies", 3), ("ed", 2), ("es", 2), ("s", 1)):
            if len(w) > cut + 3 and w.endswith(suf):
                words.add(w[:-cut])
    return words


def lookup(dict_path: str, wanted: set[str]) -> dict[str, dict]:
    """流式扫一遍词库，只保留需要的词条；同时把变形词映射回原形。"""
    hits: dict[str, dict] = {}
    if not os.path.exists(dict_path):
        return hits
    with open(dict_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            word = (row.get("word") or "").strip().lower()
            if not word:
                continue
            forms = []
            ex = row.get("exchange") or ""
            for part in ex.split("/"):
                if ":" in part:
                    forms.append(part.split(":", 1)[1].strip().lower())
            if word not in wanted and not any(f in wanted for f in forms):
                continue
            entry = {
                "word": word,
                "phonetic": (row.get("phonetic") or "").strip(),
                "translation": (row.get("translation") or "").strip(),
                "collins": (row.get("collins") or "0").strip(),
                "oxford": (row.get("oxford") or "0").strip(),
                "tag": (row.get("tag") or "").strip(),
                "frq": int((row.get("frq") or "0").strip() or 0),
            }
            hits.setdefault(word, entry)
            for f in forms:
                if f and f not in hits:
                    hits[f] = entry
    return hits


def is_hard(entry: dict) -> bool:
    if not entry["translation"]:
        return False
    if entry.get("proper"):
        return False
    trans = entry["translation"]
    for marker in ("[人名]", "[地名]", "[姓氏]", "[缩写]"):
        if trans.startswith(marker):
            return False
    tags = entry["tag"]
    if any(t in tags for t in ("zk", "gk", "cet4")):
        return False
    if (entry.get("oxford") or "0").strip() == "1":
        return False
    try:
        if int(entry["collins"] or 0) >= 2:
            return False
    except ValueError:
        pass
    frq = entry["frq"]
    # 词库里查不到词频的短词，多是变形或缩写，不算超纲词
    if frq == 0 and len(entry["word"]) < 6:
        return False
    return frq == 0 or frq >= 9000


PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<title>{title}</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>
:root{{
  --bg:#0e1320;--card:#171d2c;--fg:#e8ecf6;--muted:#8b93a7;--line:#2a3245;
  --accent:#4ea1ff;--chip:#232c3f;--shadow:0 10px 30px rgba(0,0,0,.35);
}}
*{{box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
body{{margin:0;background:var(--bg);color:var(--fg);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:16px;line-height:1.6;overflow-x:hidden}}
.wrap{{max-width:720px;margin:0 auto;padding:0 16px 60px}}
.bar{{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:10px;
  padding:12px 0;background:linear-gradient(180deg,var(--bg) 78%,transparent)}}
.back{{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:999px;
  background:var(--card);border:1px solid var(--line);color:var(--fg);text-decoration:none;font-size:14px}}
.count{{color:var(--muted);font-size:12.5px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 16px;
  box-shadow:var(--shadow);margin:0 0 10px}}
.w{{font-size:19px;font-weight:700;letter-spacing:.2px}}
.ph{{color:var(--muted);font-size:13px;margin-left:8px;font-weight:400}}
.t{{margin-top:6px;font-size:14.5px;color:#cfd6e6;white-space:pre-wrap}}
.intro{{color:var(--muted);font-size:12.5px;margin:6px 0 14px}}
footer{{margin-top:26px;text-align:center;color:var(--muted);font-size:12px;line-height:1.9}}
</style>
<div class="wrap">
  <div class="bar">
    <a class="back" href="latest.html">‹ 返回今日速递</a>
    <span class="count">{count} 个词 · {day}</span>
  </div>
  <div class="intro">从今天这期日报正文里挑出的超纲词（已在 CET-4、高中及高频词中排除），释义取自开源词库 ECDICT，全程未调用模型。</div>
  {cards}
  <footer>KIKI · 难点词汇 · 本地词库生成，非 AI 撰写</footer>
</div>
</html>
"""

CARD = """<div class="card"><span class="w">{word}</span>{ph}<div class="t">{trans}</div></div>"""


def main() -> None:
    dict_path = os.environ.get("ECDICT_PATH") or os.path.join("data", "ecdict.csv")
    post = newest_post("en")
    if not post:
        print("[skip] no english post found")
        return
    day = os.path.basename(post).split("-summary")[0]
    # 与日报页保持一致：按北京时间显示日期（UTC 22:00 跑出来的这期，文件名会早一天）
    display_day = day
    try:
        from datetime import datetime, timedelta, timezone
        post_date = datetime.strptime(day, "%Y-%m-%d").date()
        bj_date = (datetime.now(timezone.utc) + timedelta(hours=8)).date()
        if (bj_date - post_date).days == 1:
            display_day = bj_date.isoformat()
    except ValueError:
        pass
    text = read_prose(post)
    wanted = candidates_from(text)
    hits = lookup(dict_path, wanted)
    if not hits:
        print(f"[skip] dictionary not found or nothing matched: {dict_path}")
        return

    freq = Counter()
    lower_forms = Counter()
    for m in TOKEN.finditer(text):
        raw = m.group(0).strip("'-")
        freq[raw.lower()] += 1
        if raw[:1].islower():
            lower_forms[raw.lower()] += 1

    picked = []
    seen_words = set()
    for w in sorted(hits):
        e = hits[w]
        if e["word"] in seen_words:
            continue
        # 全文里只以大写字头出现过的，基本是人名/机构名，不收进词表
        if lower_forms.get(w, 0) == 0:
            continue
        if not is_hard(e):
            continue
        seen_words.add(e["word"])
        picked.append((e["frq"], -freq.get(w, 1), e))
    picked.sort(key=lambda x: (x[0] if x[0] > 0 else 10**9, x[1]))
    picked = picked[:MAX_WORDS]

    cards = []
    for _, _, e in picked:
        ph = f'<span class="ph">/{e["phonetic"]}/</span>' if e["phonetic"] else ""
        # 释义常有多行、带 [网络]/[计] 之类的专业标记，取前 3 行即可，避免卡片过长
        lines = [ln.strip() for ln in e["translation"].split("\\n") if ln.strip()]
        keep = [ln for ln in lines if not ln.startswith("[网络]")][:3] or lines[:3]
        trans = html.escape("\n".join(keep))
        cards.append(CARD.format(word=html.escape(e["word"]), ph=ph, trans=trans))

    page = PAGE.format(
        title=f"难点词汇 {display_day}",
        day=display_day,
        count=len(cards),
        cards="\n  ".join(cards) or '<div class="card">这一期没有挑出超纲词。</div>',
    )
    out = os.path.join(DOCS, "vocab.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[ok] vocab.html: {len(cards)} words from {os.path.basename(post)}")


if __name__ == "__main__":
    main()
