#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从当天这期日报里挑出“难点词汇”，生成 docs/vocab.html。

每张卡片包含：单词 + 音标 + 一键发音 + 词性 + 稀有度 + 中文释义 + 英文释义/例句
+ 这个词在当天新闻里的原文语境句（高亮）。

释义只用本地词库（ECDICT，英汉双解 CSV）查表，英文释义/例句来自免费公开词典接口
（dictionaryapi.dev，Wiktionary 数据，无需密钥、不产生任何模型 token）。
接口不通时自动降级，页面照常生成。

用法（在仓库根目录执行）：
    python scripts/build_vocab.py
词库位置：默认 data/ecdict.csv，可用环境变量 ECDICT_PATH 覆盖。
关闭联网补全：VOCAB_NO_NET=1
"""
from __future__ import annotations

import csv
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_latest import DOCS, POSTS  # noqa: E402

FRONT_MATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.S)
LINK_MD = re.compile(r"\[([^\]]*)\]\([^)]*\)")
TOKEN = re.compile(r"[A-Za-z][A-Za-z'\-]{2,}")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

# 太常见的功能词，任何词表都不该收
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "have", "has", "had", "was", "were",
    "are", "been", "will", "would", "could", "should", "there", "their", "them", "they", "his",
    "her", "its", "our", "your", "who", "what", "when", "where", "which", "while", "about",
    "into", "over", "than", "then", "also", "such", "some", "more", "most", "much", "many",
    "very", "just", "only", "even", "still", "after", "before", "during", "between", "under",
    "because", "however", "therefore", "according", "said", "says", "say", "one", "two", "new",
    "now", "get", "got", "make", "made", "use", "used", "using", "may", "might", "must",
    "can", "not", "but", "you", "all", "any", "out", "off", "own", "same", "other", "these",
}

MAX_WORDS = 80
ENRICH_CACHE = os.path.join("data", "vocab_enrich.json")


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
        # 清掉正文里的标记残留：来源前缀、HTML 标签、Markdown 粗体、零宽字符
        s = re.sub(r"^\s*rss\s*·.*?·\s*[A-Za-z]{3,9}\s*\d{1,2},\s*\d{2}:\d{2}\s*", "", s)
        s = re.sub(r"<[^>]*>", "", s)
        s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
        s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
        s = s.replace("\u200b", "").replace("\xa0", " ").replace("\u2011", "-")
        s = LINK_MD.sub(r"\1", s)
        lines.append(s)
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
                "pos": (row.get("pos") or "").strip(),
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


# ---------- 联网补全（免费公开词典，无需密钥，不产生模型 token） ----------

def load_cache() -> dict:
    if os.path.exists(ENRICH_CACHE):
        try:
            with open(ENRICH_CACHE, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}
    return {}


def save_cache(cache: dict) -> None:
    try:
        os.makedirs(os.path.dirname(ENRICH_CACHE) or ".", exist_ok=True)
        with open(ENRICH_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=0)
    except OSError:
        pass


def fetch_enrich(word: str, timeout: int = 8) -> dict:
    """取英文释义、例句、词性、发音音频地址；失败返回空 dict。"""
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + urllib.parse.quote(word)
    req = urllib.request.Request(url, headers={"User-Agent": "kikinews-vocab/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return {}
    if not isinstance(data, list) or not data:
        return {}
    first = data[0]
    out = {}
    for ph in first.get("phonetics") or []:
        if ph.get("audio"):
            out["audio"] = ph["audio"]
            break
    meanings = first.get("meanings") or []
    for m in meanings:
        pos = (m.get("partOfSpeech") or "").strip()
        for d in m.get("definitions") or []:
            if d.get("definition"):
                out.setdefault("en", d["definition"].strip())
                out.setdefault("pos", pos)
            if d.get("example") and "example" not in out:
                out["example"] = d["example"].strip()
        if out.get("en"):
            break
    return out


def enrich_words(words: list[str], use_net: bool) -> dict:
    cache = load_cache()
    todo = [w for w in words if w not in cache]
    if use_net:
        for w in todo:
            cache[w] = fetch_enrich(w)
        if todo:
            save_cache(cache)
    return {w: cache.get(w) or {} for w in words}


# ---------- 语境句 ----------

def sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text)
    out = []
    for s in SENT_SPLIT.split(flat):
        s = s.strip()
        # 正文里的小标题（「Impact」「Prerequisite Context」）不是句子，去掉
        s = re.sub(r"^[「『\"']?[^」』\"']{0,30}[」』\"']\s*", "", s) if re.match(r"^[「『]", s) else s
        s = s.strip()
        if len(s) < 25:
            continue
        # 标题行常带评分/标签残留，不适合当语境句
        if "⭐" in s or re.search(r"\b\d+\.\d/10\b", s):
            continue
        out.append(s)
    return out


def tts_url(word: str) -> str:
    """有道的公开发音接口（https，直接返回 mp3，无需密钥），比 WebView 自带 TTS 可靠。"""
    return "https://dict.youdao.com/dictvoice?audio=" + urllib.parse.quote(word) + "&amp;type=2"


def context_for(word: str, sents: list[str]) -> str:
    pat = re.compile(r"\b" + re.escape(word) + r"[a-z]{0,3}\b", re.I)
    for s in sents:
        if pat.search(s):
            s2 = html.escape(html.unescape(s), quote=False)
            # 词本身是 ASCII，转义不影响高亮
            s2 = pat.sub(lambda m: "<b>" + m.group(0) + "</b>", s2, count=1)
            if len(s2) > 280:
                s2 = s2[:277].rsplit(" ", 1)[0] + "…"
            return s2
    return ""


# ---------- 渲染 ----------

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
.card{{position:relative;background:var(--card);border:1px solid var(--line);border-radius:16px;
  padding:13px 16px 14px;box-shadow:var(--shadow);margin:0 0 10px;overflow:hidden}}
.card::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--accent);opacity:.55}}
.hdr{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.w{{font-size:19px;font-weight:700;letter-spacing:.2px}}
.ph{{color:var(--muted);font-size:13px;font-weight:400}}
.meta{{display:flex;align-items:center;gap:8px;margin-top:3px;flex-wrap:wrap}}
.pos{{font-size:11.5px;color:var(--fg);background:var(--chip);border-radius:6px;padding:2px 7px}}
.stars{{font-size:11.5px;color:#ffc861;letter-spacing:1px}}
.say{{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;
  border-radius:999px;border:1px solid var(--line);background:var(--chip);color:var(--fg);
  font-size:14px;cursor:pointer;padding:0}}
.say:active{{transform:scale(.94)}}
.say.on{{border-color:var(--accent);color:var(--accent)}}
.t{{margin-top:7px;font-size:14.5px;color:#cfd6e6;white-space:pre-wrap}}
.en{{margin-top:5px;font-size:13.5px;color:#a9b4cc;font-style:italic}}
.ex{{margin-top:4px;font-size:13px;color:var(--muted)}}
.ctx{{margin-top:9px;padding:9px 11px;border-left:2px solid #3b4a6b;background:rgba(78,161,255,.07);
  border-radius:0 10px 10px 0;font-size:13.5px;color:#c3cddf}}
.ctx b{{color:#7fb8ff;font-weight:700}}
.ctx .lb{{display:block;font-size:11px;color:var(--muted);margin-bottom:3px;letter-spacing:.4px}}
.intro{{color:var(--muted);font-size:12.5px;margin:6px 0 14px}}
footer{{margin-top:26px;text-align:center;color:var(--muted);font-size:12px;line-height:1.9}}
</style>
<div class="wrap">
  <div class="bar">
    <a class="back" href="latest.html">‹ 返回今日速递</a>
    <span class="count">{count} 个词 · {day}</span>
  </div>
  <div class="intro">从今天这期日报英文正文里挑出的超纲词（已排除四六级/高中/高频核心词）。点 🔊 跟读发音，看「原文语境」回忆当时那句话。</div>
  {cards}
  <footer>KIKI · 难点词汇 · 释义取自开源词库 ECDICT 与公开词典接口</footer>
</div>
<script>
(function(){{
  var doc = document;
  function tts(word){{
    try {{
      if (!window.speechSynthesis) return;
      var u = new SpeechSynthesisUtterance(word);
      u.lang = 'en-US'; u.rate = 0.92;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
    }} catch (e) {{}}
  }}
  function speak(word, src){{
    if (!src) {{ tts(word); return; }}
    try {{
      var a = new Audio(src);
      a.onerror = function(){{ tts(word); }};
      var p = a.play();
      if (p && p.catch) {{ p.catch(function(){{ tts(word); }}); }}
    }} catch (e) {{ tts(word); }}
  }}
  doc.addEventListener('click', function(ev){{
    var btn = ev.target.closest ? ev.target.closest('.say') : null;
    if (!btn) return;
    var self = this;
    btn.classList.add('on');
    setTimeout(function(){{ btn.classList.remove('on'); }}, 600);
    speak(btn.getAttribute('data-w'), btn.getAttribute('data-a'));
  }}, false);
}})();
</script>
</html>
"""

CARD = """<div class="card">
    <div class="hdr"><span class="w">{word}</span><button class="say" data-w="{word}" data-a="{audio}">🔊</button>{ph}</div>
    <div class="meta">{pos}{stars}</div>
    <div class="t">{trans}</div>{en}{ex}{ctx}
  </div>"""

POS_MAP = [
    ("n.", "n."), ("vt.", "v."), ("vi.", "v."), ("v.", "v."),
    ("a.", "adj."), ("adj.", "adj."), ("ad.", "adv."), ("adv.", "adv."),
    ("prep.", "prep."), ("conj.", "conj."), ("pron.", "pron."),
]


def stars_for(frq: int) -> str:
    if frq == 0:
        return "★★★★★"
    if frq >= 16000:
        return "★★★★"
    if frq >= 12000:
        return "★★★"
    return "★★"


def short(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + "…"


def pos_of(entry: dict, enrich: dict) -> str:
    raw = (enrich.get("pos") or "").strip()
    if raw:
        short = {"noun": "n.", "verb": "v.", "adjective": "adj.", "adverb": "adv.",
                 "preposition": "prep.", "conjunction": "conj.", "pronoun": "pron."}.get(raw, raw)
        return f'<span class="pos">{html.escape(short)}</span>'
    first = entry["translation"].strip().split()[0] if entry["translation"].strip() else ""
    for src, short in POS_MAP:
        if first == src:
            return f'<span class="pos">{short}</span>'
    return ""


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

    words = [e["word"] for _, _, e in picked]
    use_net = os.environ.get("VOCAB_NO_NET") != "1"
    enriched = enrich_words(words, use_net) if words else {}
    sents = sentences(text)

    cards = []
    for _, _, e in picked:
        w = e["word"]
        en = enriched.get(w) or {}
        audio = tts_url(w)
        ph = (f'<span class="ph">/{html.escape(e["phonetic"], quote=False)}/</span>'
              if e["phonetic"] else "")
        # 词库释义用字面量 "\n" 分行，且常带 [网络]/[计] 之类的专业标记
        raw_lines = e["translation"].replace("\\n", "\n").split("\n")
        lines = [ln.strip() for ln in raw_lines if ln.strip()]
        keep = [ln for ln in lines if not ln.startswith("[网络]")][:3] or lines[:3]
        trans = html.escape("\n".join(keep), quote=False)
        en_bit = (f'<div class="en">{html.escape(short(en["en"], 150), quote=False)}</div>'
                  if en.get("en") else "")
        ex_bit = (f'<div class="ex">e.g. {html.escape(short(en["example"], 150), quote=False)}</div>'
                  if en.get("example") else "")
        ctx = context_for(w, sents)
        ctx_bit = f'<div class="ctx"><span class="lb">原文语境</span>{ctx}</div>' if ctx else ""
        cards.append(CARD.format(
            word=html.escape(w, quote=False), audio=audio, ph=ph,
            pos=pos_of(e, en), stars=f'<span class="stars">{stars_for(e["frq"])}</span>',
            trans=trans, en=en_bit, ex=ex_bit, ctx=ctx_bit,
        ))

    page = PAGE.format(
        title=f"难点词汇 {display_day}",
        day=display_day,
        count=len(cards),
        cards="\n  ".join(cards) or '<div class="card">这一期没有挑出超纲词。</div>',
    )
    out = os.path.join(DOCS, "vocab.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[ok] vocab.html: {len(cards)} words from {os.path.basename(post)} "
          f"(enrich: {sum(1 for w in words if enriched.get(w))})")


if __name__ == "__main__":
    main()
