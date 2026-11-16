#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 Horizon 生成的最新一期日报转成手机友好的单页 HTML。

同一张卡片里先英文、紧接着中文（上下对照，不需要切换页面）。

输入：docs/_posts/YYYY-MM-DD-summary-<lang>.md（Horizon 自动写入）
输出：docs/latest.html      —— 英文在上、中文在下，逐条对照；APK 默认加载这个
      docs/latest-en.html   —— 纯英文版（兼容/备用）
      docs/latest.json      —— 版本信息，App 用来判断是否更新

只依赖 markdown 库。
"""
from __future__ import annotations

import glob
import html
import json
import os
import re
from datetime import datetime, timedelta, timezone

import markdown

DOCS = "docs"
POSTS = os.path.join(DOCS, "_posts")

MD_EXTENSIONS = ["extra", "tables", "sane_lists", "fenced_code", "nl2br"]

FRONT_MATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.S)
SUMMARY_LINE = re.compile(r"^>\s*(.+)$", re.M)
GROUP_LINE = re.compile(r"^\*\*(.+?)\*\*$")
TOC_LINE = re.compile(
    r"^\d+\.\s*\[(.+?)\]\(#(item-[^)]+)\)\s*(?:⭐️\s*(\d+(?:\.\d+)?)\s*/\s*10)?"
)
ITEM_MARK = re.compile(r'<a id="(item-[^"]+)"></a>')
TITLE_LINE = re.compile(
    r"^###\s*\[(.+?)\]\((.+?)\)\s*(?:⭐️\s*(\d+(?:\.\d+)?)\s*/\s*10)?"
)
SCORE_TAIL = re.compile(r"⭐️?\s*(\d+(?:\.\d+)?)\s*/\s*10")
SRC_LINE = re.compile(r"^([^\s·]+)\s·\s.*")  # e.g. "rss · Simon Willison · 11月11日 15:11"
TAG_LINE = re.compile(r"^\*\*(?:标签|Tags|Tag)\*\*")
CODE_CHIP = re.compile(r"<code>(.+?)</code>")

# 中文页面（html lang="zh-CN"）下，弯引号 ’ ‘ “ ” 会被浏览器当成“东亚标点”，
# 交给中文字体渲染，字形带全角侧边距，就会出现 "China ’s" 中间空出一大块的现象
# （复制到别处又正常，因为那里用的是拉丁字体）。统一换成 ASCII 引号即可避免。
TYPO_QUOTES = {
    "\u2019": "'",  # ’
    "\u2018": "'",  # ‘
}


def plain_quotes(s: str) -> str:
    for src, dst in TYPO_QUOTES.items():
        s = s.replace(src, dst)
    return s

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0e1320">
<title>{title}</title>
<style>
/* 固定深色皮肤：词汇页本来就是深色，主页原来跟随系统（浅色设备上白底），
   两页在平板/手机上会一明一暗。现统一成同一套深色 token，亮度偏柔和不刺眼。 */
:root{{
  --bg:#0e1320; --fg:#e2e8f4; --muted:#8b93a7; --line:#242d40;
  --card:#111926; --soft:#1a2233; --accent:#5aa6ff; --accent2:#4fd1c5;
  --score:#4fd1c5; --chip:#242e42; --shadow:0 8px 24px rgba(0,0,0,.28);
}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%;scroll-behavior:smooth;overflow-x:hidden}}
body{{
  margin:0;background:var(--bg);color:var(--fg);max-width:100vw;overflow-x:hidden;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:16.5px;line-height:1.78;-webkit-font-smoothing:antialiased;
  overflow-wrap:break-word;
}}
.wrap{{max-width:720px;margin:0 auto;padding:0 16px 72px;padding-bottom:calc(72px + env(safe-area-inset-bottom));}}

/* ---------- 横屏 / 平板宽屏：正文分两栏，别留一大片空白 ---------- */
@media (min-width: 760px){{
  .wrap{{max-width:1320px;padding:0 20px 72px;padding-bottom:calc(72px + env(safe-area-inset-bottom))}}
  .hero{{margin:0 -20px 20px;padding:34px 26px 26px}}
  .hero h1{{font-size:27px}}
  .hero .meta{{font-size:13.5px}}
  .cards > .card{{margin:0 0 16px}}
  .card h3{{font-size:18.5px}}
}}


/* ---------- header ---------- */
.hero{{
  margin:0 -16px 18px;padding:30px 22px 22px;color:#fff;
  background:linear-gradient(135deg,#1b3f78 0%,#0f6560 100%);
  border-radius:0 0 22px 22px;
}}
.hero .brand{{font-size:13px;letter-spacing:.14em;text-transform:uppercase;opacity:.85}}
.hero h1{{margin:6px 0 8px;font-size:23px;line-height:1.35;font-weight:700;letter-spacing:.2px}}
.hero .meta{{font-size:12.5px;opacity:.9}}
.pillrow{{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}}
.pill{{
  font-size:12.5px;padding:5px 11px;border-radius:999px;
  background:rgba(255,255,255,.18);backdrop-filter:blur(6px);white-space:nowrap;
}}
.pill-link{{color:inherit;text-decoration:none;font-weight:700}}

/* ---------- 中文对照块 ---------- */
.zh{{
  margin-top:14px;padding-top:12px;border-top:1px dashed var(--line);
}}
.zhlabel{{
  display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.08em;
  color:var(--accent2);background:var(--chip);border:1px solid var(--line);
  border-radius:6px;padding:2px 8px;margin-bottom:8px;
}}
.zh h4{{margin:0 0 8px;font-size:16px;font-weight:600;line-height:1.5;color:var(--fg)}}

/* ---------- summary ---------- */
.summary{{
  display:flex;gap:10px;align-items:flex-start;background:var(--card);border:1px solid var(--line);
  border-radius:14px;padding:13px 15px;font-size:14.5px;color:var(--muted);margin-bottom:16px;box-shadow:var(--shadow);
}}
.summary b{{color:var(--fg)}}

/* ---------- toc ---------- */
/* 手机窄屏目录做成等宽等高的网格块：一律满宽、固定两行高度，超出两行省略，
   长短高矮不再参差；底色用与正文同等暗度的深蓝（#0f1a2e），白字对比度不变 */
.toc{{display:grid;grid-template-columns:1fr;gap:7px;margin-bottom:20px}}
@media (min-width: 760px){{
  .toc{{grid-template-columns:repeat(2,minmax(0,1fr))}}
}}
.toc a{{
  display:flex;align-items:center;min-height:46px;
  text-decoration:none;color:var(--fg);background:#0f1a2e;border:1px solid #25314b;
  padding:6px 12px;border-radius:10px;font-size:13.5px;box-sizing:border-box;
}}
.toc a .tt{{
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;
  width:100%;text-align:justify;text-justify:inter-word;hyphens:auto;-webkit-hyphens:auto;
}}
.toc a .n{{color:var(--muted);font-size:12px;margin-left:4px}}

/* ---------- group heading ---------- */
.group{{
  display:flex;align-items:center;gap:10px;margin:26px 0 12px;
  font-size:15px;font-weight:700;color:var(--fg);
}}
.group:before{{content:"";width:4px;height:16px;border-radius:2px;background:var(--accent)}}
.group span{{color:var(--muted);font-weight:500;font-size:12.5px}}

/* ---------- card ---------- */
/* 卡片底色压暗（原来是 #161d2b，比页面底色亮一档，白标题压在它上面发闷、不够跳），
   靠描边与页面区分；窄屏圆角收小，标题折两行时不再显得笨重 */
.card{{
  background:var(--card);border:1px solid var(--line);border-radius:16px;
  padding:16px 16px 6px;margin:0 0 14px;box-shadow:var(--shadow);scroll-margin-top:16px;
}}
.card h3{{margin:0 0 8px;font-size:18px;line-height:1.45;font-weight:700;text-wrap:pretty;color:#ffffff;letter-spacing:.1px}}
@media (max-width: 520px){{
  .card{{border-radius:10px;padding:13px 14px 4px}}
  .card h3{{font-size:17px;line-height:1.42}}
}}
.card h3 a{{color:var(--fg);text-decoration:none}}
.card h3 a:active{{color:var(--accent)}}
.score{{
  display:inline-flex;align-items:center;gap:3px;vertical-align:middle;
  font-size:12px;font-weight:700;color:var(--score);background:var(--chip);
  border-radius:999px;padding:2px 8px;margin-left:6px;
}}
.src{{font-size:12.5px;color:var(--muted);margin:-2px 0 10px}}
.card p{{margin:0 0 12px;font-size:15.5px;color:var(--fg);text-align:justify;text-justify:inter-word;hyphens:auto;-webkit-hyphens:auto}}
.card a{{color:var(--accent);text-decoration:none;word-break:break-word}}
.note{{
  border-radius:12px;padding:10px 12px 2px;font-size:14.5px;background:var(--soft);
  border-left:3px solid var(--accent2);margin:0 0 12px;color:var(--fg);
}}
.note .lbl{{display:block;font-size:12px;font-weight:700;letter-spacing:.04em;color:var(--accent2);margin-bottom:2px}}
.note.bg{{border-left-color:var(--accent)}}
.note.bg .lbl{{color:var(--accent)}}
.tags{{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}}
.chip{{font-size:12px;background:var(--chip);color:var(--muted);padding:3px 9px;border-radius:999px;border:1px solid var(--line)}}
.srcurl{{margin:0 0 14px;font-size:13px}}
.srcurl a{{color:var(--accent);text-decoration:none;word-break:break-all}}
.srcurl a:hover{{text-decoration:underline}}
.cands{{margin:0 0 18px}}
.cands summary{{list-style:none;cursor:pointer}}
.cands summary::-webkit-details-marker{{display:none}}
.cbtn{{display:inline-block;font-size:13px;padding:7px 14px;border-radius:999px;
  border:1px solid var(--line);background:var(--card);color:var(--accent)}}
.cands[open] .cbtn{{background:var(--chip)}}
.clist{{margin:12px 0 0;padding-left:22px;font-size:13.5px;color:var(--muted)}}
.clist li{{margin:0 0 7px}}
.clist a{{color:var(--fg);text-decoration:none}}
.clist a:hover{{text-decoration:underline}}
.clist .cm{{margin-left:6px;opacity:.6;font-size:12px}}
details{{margin:0 0 14px;font-size:13.5px}}
details summary{{color:var(--muted);cursor:pointer}}
details ul{{margin:8px 0 0;padding-left:18px}}
.card ul,.card ol{{padding-left:20px;margin:0 0 12px}}
.card li{{margin:0 0 6px}}
.card blockquote{{margin:0 0 12px;padding:8px 12px;border-left:3px solid var(--line);color:var(--muted);font-size:14px}}
.card code{{background:var(--chip);padding:2px 6px;border-radius:5px;font-size:13px}}
.card pre{{background:var(--soft);padding:12px;border-radius:10px;overflow-x:auto;font-size:13px}}
.card img{{max-width:100%;height:auto;border-radius:10px}}
.card table{{width:100%;border-collapse:collapse;font-size:14px;margin:0 0 12px}}
.card th,.card td{{border:1px solid var(--line);padding:7px 9px;text-align:left}}

footer{{margin-top:34px;text-align:center;color:var(--muted);font-size:12.5px;line-height:1.9}}
footer .dot{{opacity:.45;margin:0 6px}}
.top{{
  position:fixed;right:16px;bottom:calc(18px + env(safe-area-inset-bottom));z-index:9;
  width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:var(--card);
  color:var(--fg);font-size:18px;box-shadow:var(--shadow);cursor:pointer;display:none;align-items:center;justify-content:center;
}}
.top.show{{display:flex}}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <div class="brand">KIKI DAILY · 每日速递</div>
    <h1>{hero_title}</h1>
    <div class="meta">{updated} · 自动生成</div>
    <div class="pillrow">{pills}</div>
  </div>
  {cands}

{body}

  <footer>
    <div>由 AI 筛选与总结，可能存在偏差，请以原文为准。</div>
    <div>Generated by KIKI<span class="dot">·</span>{updated_short}</div>
  </footer>
</div>
<button class="top" id="totop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>
<script>
window.addEventListener('scroll',function(){{
  document.getElementById('totop').classList.toggle('show',window.scrollY>600);
}});

/* 宽屏瀑布流：卡片依次放进"当前最短"的那一栏，避免 Grid 同行等高造成的空档。
   宽屏时所有分组的卡片合成一条连续瀑布流、并隐藏分组标题——每组只有 3–4 张卡时，
   组内怎么摆都会在短的那栏留下几百像素空白，只有跨组连续排才真正补满。
   760px 以下仍是原来的单列 + 分组标题。 */
(function(){{
  var boxes=[].slice.call(document.querySelectorAll('.cards'));
  if(!boxes.length) return;
  var pool=new Map();
  boxes.forEach(function(b){{ pool.set(b,[].slice.call(b.children)); }});
  var heads=[].slice.call(document.querySelectorAll('.group'));

  function colsFor(){{
    var w=document.documentElement.clientWidth||window.innerWidth;
    return w<760?1:2;
  }}

  function fill(b,kids,n){{
    var gap=22, i;
    b.style.display='block';
    b.textContent='';
    var box=document.createElement('div');
    box.style.display='flex';
    box.style.alignItems='flex-start';
    b.appendChild(box);
    var cols=[];
    for(i=0;i<n;i++){{
      var c=document.createElement('div');
      c.style.flex='1 1 0';
      c.style.minWidth='0';
      if(i<n-1) c.style.marginRight=gap+'px';
      box.appendChild(c);
      cols.push(c);
    }}
    kids.forEach(function(k){{
      var best=cols[0], h=1e9;
      for(var j=0;j<cols.length;j++){{
        var ch=cols[j].getBoundingClientRect().height;
        if(ch<h){{ h=ch; best=cols[j]; }}
      }}
      best.appendChild(k);
    }});

    // 收尾：两栏底部差得多时，把高栏末尾那张"很长"的卡改成通栏放到两栏下面。
    // 它本来就是这一栏最后一张，顺序不变，但两栏下方不会再空一大片。
    for(var pass=0; pass<3; pass++){{
      var hs=cols.map(function(c){{ return c.getBoundingClientRect().height; }});
      var hi=Math.max.apply(null,hs), lo=Math.min.apply(null,hs);
      if(hi-lo<240) break;
      var col=cols[hs.indexOf(hi)], last=col.lastElementChild;
      if(!last) break;
      if(last.getBoundingClientRect().height<240) break;
      col.removeChild(last);
      b.appendChild(last);
    }}
  }}

  function run(){{
    var n=colsFor(), i;
    var sy=window.pageYOffset||document.documentElement.scrollTop||0;
    // 先把所有卡片摘回池子，恢复分组标题和容器
    boxes.forEach(function(b){{
      pool.get(b).forEach(function(k){{ if(k.parentNode) k.parentNode.removeChild(k); }});
      b.textContent='';
      b.style.display='';
    }});
    heads.forEach(function(h){{ h.style.display=''; }});

    if(n<2){{
      boxes.forEach(function(b){{ pool.get(b).forEach(function(k){{ b.appendChild(k); }}); }});
    }} else {{
      heads.forEach(function(h){{ h.style.display='none'; }});
      var all=[];
      boxes.forEach(function(b){{ all=all.concat(pool.get(b)); }});
      boxes.forEach(function(b,idx){{ if(idx) b.style.display='none'; }});
      fill(boxes[0], all, n);
    }}
    // 重排会改变内容高度，浏览器可能把滚动位置夹回顶部；这里还原，避免"上滑一下就跳回开头"
    if(sy>0){{
      window.scrollTo(0,sy);
      requestAnimationFrame(function(){{ window.scrollTo(0,sy); }});
    }}
  }}

  var timer=null, lastW=-1;
  function later(){{
    // iPad 上下滑动时工具栏收放只改变高度、不改变宽度；宽度没变就不重排，
    // 否则每次都拆了重建两栏，滚动位置会被弹回顶部。
    var w=document.documentElement.clientWidth;
    if(w===lastW) return;
    lastW=w;
    clearTimeout(timer);
    timer=setTimeout(run,120);
  }}
  function force(){{
    lastW=document.documentElement.clientWidth;
    clearTimeout(timer);
    timer=setTimeout(run,90);
  }}
  window.addEventListener('resize',later);
  window.addEventListener('load',force);
  try{{ document.addEventListener('toggle',force,true); }}catch(e){{}}
  run();
}})();
</script>
</body>
</html>
"""


def newest_post(lang: str) -> str | None:
    files = sorted(glob.glob(os.path.join(POSTS, f"*-summary-{lang}.md")))
    return files[-1] if files else None


def md(text: str) -> str:
    return markdown.markdown(text.strip(), extensions=MD_EXTENSIONS, output_format="html5")


def parse_post(path: str) -> dict:
    raw = open(path, encoding="utf-8").read()
    raw = FRONT_MATTER.sub("", raw, count=1)
    day = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    summary_m = SUMMARY_LINE.search(raw)
    summary = summary_m.group(1).strip() if summary_m else ""

    parts = ITEM_MARK.split(raw)
    head, rest = parts[0], parts[1:]

    toc: list[dict] = []
    current_group = None
    for line in head.splitlines():
        g = GROUP_LINE.match(line.strip())
        if g:
            current_group = g.group(1).strip()
            toc.append({"group": current_group, "items": []})
            continue
        t = TOC_LINE.match(line.strip())
        if t and toc:
            toc[-1]["items"].append(
                {"title": t.group(1).strip(), "anchor": t.group(2), "score": t.group(3) or ""}
            )

    items = []
    for i in range(0, len(rest), 2):
        anchor = rest[i]
        body = rest[i + 1] if i + 1 < len(rest) else ""
        # 下一个分组标题（## xxx）会混进上一条的正文尾部，切掉
        gm = re.search(r"\n##\s+\S", body)
        if gm:
            body = body[: gm.start()]
        lines = body.splitlines()
        if not lines:
            continue
        title, url, score = "", "", ""
        idx = 0
        for j, ln in enumerate(lines):
            m = TITLE_LINE.match(ln.strip())
            if m:
                title, url, score = m.group(1).strip(), m.group(2).strip(), m.group(3) or ""
                idx = j + 1
                break
        if not title:
            continue
        # 标题里可能残留星标
        sm = SCORE_TAIL.search(title)
        if sm:
            score = score or sm.group(1)
            title = SCORE_TAIL.sub("", title).strip()

        src_text = ""
        paras: list[str] = []
        notes: list[dict] = []
        tags: list[str] = []
        extra_html = ""
        buf: list[str] = []

        def flush() -> None:
            if buf:
                paras.append("\n".join(buf).strip())
                buf.clear()

        body_lines = lines[idx:]
        k = 0
        while k < len(body_lines):
            ln = body_lines[k]
            s = ln.strip()
            if s.startswith("<details"):
                flush()
                block = [ln]
                while k + 1 < len(body_lines) and "</details>" not in body_lines[k]:
                    k += 1
                    block.append(body_lines[k])
                extra_html += "\n".join(block)
                k += 1
                continue
            if s in ("", "---"):
                flush()
                k += 1
                continue
            if SRC_LINE.match(s) and not src_text and not buf:
                src_text = s
                k += 1
                continue
            if TAG_LINE.match(s):
                flush()
                tags = [t.strip("` ") for t in re.findall(r"`([^`]+)`", s)]
                if not tags:
                    tags = [x.strip() for x in re.split("[,，]", s.split("：")[-1].split(":")[-1]) if x.strip()]
                k += 1
                continue
            nm = re.match(r"^\*\*「(.+?)」\*\*\s*(.*)$", s)
            if nm:
                flush()
                note_body = [nm.group(2)]
                k += 1
                while k < len(body_lines):
                    nxt = body_lines[k].strip()
                    if not nxt or nxt == "---" or nxt.startswith("**「") or nxt.startswith("**标签") or nxt.startswith("<details"):
                        break
                    note_body.append(nxt)
                    k += 1
                notes.append({"kind": nm.group(1), "text": "\n".join(note_body).strip()})
                continue
            buf.append(ln)
            k += 1
        flush()

        items.append(
            {
                "anchor": anchor,
                "title": title,
                "url": url,
                "score": score,
                "src": src_text,
                "paras": [md(p) for p in paras if p],
                "notes": [{"kind": n["kind"], "html": md(n["text"])} for n in notes],
                "tags": tags,
                "extra": extra_html,
            }
        )

    return {"day": day.group(1) if day else "", "summary": summary, "toc": toc, "items": items}


def esc_url(u: str) -> str:
    """链接里常带 RSS 的 &amp;（markdown 源码已经转义过一次），
    直接再 escape 会变成 &amp;amp;，既难看又打坏查询参数：先还原再转义。"""
    return html.escape(html.unescape(u or ""), quote=True)


def clean_text(text: str) -> str:
    """原文里偶尔出现 &\\#x27; 这类被反斜杠挡住的实体，先还原再按 HTML 转义输出。
    同时去掉 markdown 的反斜杠转义（如标题里的 \\!），否则页面会显示成 "Jensen\\!"。"""
    text = text.replace("&\\#", "&#")
    text = re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])", r"\1", text)
    return html.escape(html.unescape(text))


def inline_md(text: str) -> str:
    """把 [文字](链接) 转成真链接，其余文本转义，避免实体和裸 markdown 漏到页面上。"""
    text = html.unescape(text)
    parts = re.split(r"\[([^\]]+)\]\((https?://[^)]+)\)", text)
    out: list[str] = []
    for i, chunk in enumerate(parts):
        m = i % 3
        if m == 0:
            out.append(html.escape(chunk))
        elif m == 1:
            href = esc_url(parts[i + 1])
            out.append(f'<a href="{href}" target="_blank" rel="noopener">{html.escape(chunk)}</a>')
    return "".join(out)


def render_lang(data: dict, lang: str) -> str:
    card_html = []
    for it in data["items"]:
        score = (
            f'<span class="score">▍{html.escape(it["score"])}/10</span>' if it["score"] else ""
        )
        plain_title = clean_text(it["title"])
        title_html = (
            f'<a href="{esc_url(it["url"])}" target="_blank" rel="noopener">{plain_title}</a>'
            if it["url"]
            else plain_title
        )
        src = f'<div class="src">{inline_md(it["src"])}</div>' if it["src"] else ""
        body = "".join(it["paras"])
        notes = ""
        for n in it["notes"]:
            cls = "note bg" if n["kind"] in ("背景", "Background") else "note"
            notes += f'<div class="{cls}"><span class="lbl">{html.escape(n["kind"])}</span>{n["html"]}</div>'
        tags = ""
        if it["tags"]:
            chips = "".join(f'<span class="chip">{html.escape(t)}</span>' for t in it["tags"])
            tags = f'<div class="tags">{chips}</div>'
        card_html.append(
            f'<article class="card" id="{it["anchor"]}">'
            f'<h3>{title_html}{score}</h3>{src}{body}{notes}{tags}{it["extra"]}</article>'
        )

    anchor_to_card: dict[str, str] = {}
    for idx, it in enumerate(data["items"]):
        anchor_to_card[it["anchor"]] = card_html[idx]

    blocks: list[str] = []
    emitted: list[str] = []

    if data["toc"]:
        nav = "".join(
            f'<a href="#{i["anchor"]}"{en_attr(i["title"])}><span class="tt">{clean_text(i["title"])}</span></a>'
            for g in data["toc"] for i in g["items"] if i["anchor"] in anchor_to_card
        )
        if nav:
            blocks.append(f'<div class="toc">{nav}</div>')

    for g in data["toc"]:
        items = [i for i in g["items"] if i["anchor"] in anchor_to_card]
        if not items:
            continue
        label = "条" if lang == "zh" else "items"
        blocks.append(
            f'<div class="group">{html.escape(g["group"])}<span>{len(items)} {label}</span></div>'
        )
        for i in items:
            blocks.append(anchor_to_card[i["anchor"]])
            emitted.append(i["anchor"])

    # 目录里没列到的条目（结构异常时）也要输出，保证不漏
    for it in data["items"]:
        if it["anchor"] not in emitted:
            blocks.append(anchor_to_card[it["anchor"]])

    if not blocks:
        blocks = card_html

    summary = ""
    if data["summary"]:
        label = "本期" if lang == "zh" else "Summary"
        summary = (
            f'<div class="summary"><span>📌</span><div><b>{label}</b> · '
            f'{html.escape(data["summary"])}</div></div>'
        )

    return (
        f'<section data-lang="{lang}" style="display:{"block" if lang == "zh" else "none"}">'
        f"{summary}{''.join(blocks)}</section>"
    )


def _group_titles(zh: dict | None, en: dict | None) -> list[str]:
    groups: list[str] = []
    zh_groups = [g["group"] for g in (zh or {}).get("toc", [])]
    en_groups = [g["group"] for g in (en or {}).get("toc", [])]
    for i, name in enumerate(zh_groups):
        other = en_groups[i] if i < len(en_groups) else ""
        groups.append(f"{name} · {other}" if other else name)
    for i in range(len(zh_groups), len(en_groups)):
        groups.append(en_groups[i])
    return groups


def en_attr(text: str) -> str:
    """文本基本是英文时返回 lang="en"，让 CSS 断词（hyphens）生效。

    页面是 lang="zh-CN"，不加这个属性时浏览器不会对英文词组断词，
    窄屏下长词（如 1.6-trillion-parameter）只能整体换行，右侧留一大片空白。
    """
    letters = [c for c in (text or "") if c.isalpha()]
    if not letters:
        return ""
    cjk = sum(1 for c in letters if "\u4e00" <= c <= "\u9fff")
    return ' lang="en"' if cjk / len(letters) < 0.2 else ""


def _card(anchor: str, en_it: dict | None, zh_it: dict | None) -> str:
    lead = en_it or zh_it
    score = (en_it or {}).get("score") or (zh_it or {}).get("score") or ""
    score_html = f'<span class="score">▍{html.escape(score)}/10</span>' if score else ""
    if en_it and en_it["url"]:
        head = f'<a href="{esc_url(en_it["url"])}" target="_blank" rel="noopener">{clean_text(en_it["title"])}</a>'
    else:
        head = clean_text(lead["title"])

    parts: list[str] = [f'<article class="card" id="{anchor}"{en_attr(lead["title"])}><h3>{head}{score_html}</h3>']

    if en_it:
        if en_it["src"]:
            parts.append(f'<div class="src">{inline_md(en_it["src"])}</div>')
        parts.append("".join(en_it["paras"]))
        for n in en_it["notes"]:
            cls = "note bg" if n["kind"] in ("背景", "Background") else "note"
            parts.append(f'<div class="{cls}"><span class="lbl">{html.escape(n["kind"])}</span>{n["html"]}</div>')

    if zh_it and _has_chinese(zh_it):
        body_zh = "".join(zh_it["paras"]) + "".join(
            f'<div class="note{" bg" if n["kind"] in ("背景", "Background") else ""}">'
            f'<span class="lbl">{html.escape(n["kind"])}</span>{n["html"]}</div>'
            for n in zh_it["notes"]
        )
        title_zh = f"<h4>{clean_text(zh_it['title'])}</h4>" if en_it else ""
        if body_zh or title_zh:
            parts.append(f'<div class="zh"><span class="zhlabel">中文</span>{title_zh}{body_zh}</div>')

    if lead.get("url"):
        url = esc_url(lead["url"])
        parts.append(
            f'<div class="srcurl">🔗 原文链接 · '
            f'<a href="{url}" target="_blank" rel="noopener">{url}</a></div>'
        )
    tags = (en_it or {}).get("tags") or (zh_it or {}).get("tags") or []
    if tags:
        chips = "".join(f'<span class="chip">{html.escape(t)}</span>' for t in tags)
        parts.append(f'<div class="tags">{chips}</div>')
    parts.append(lead.get("extra", ""))
    parts.append("</article>")
    return "".join(parts)


def _has_chinese(item: dict) -> bool:
    """判断这条「中文稿」里是否真的有中文。

    抓取/分析偶发会让中文档保留英文原文（模型没翻译），
    这种条目在中文区展示会导致「标着中文、内容是英文」。
    粗略用汉字数量判断：正文不足 20 个汉字就当作没有中文。
    """
    text = item.get("title") or ""
    text += "".join(item.get("paras") or [])
    for n in item.get("notes") or []:
        text += n.get("html") or ""
    return len(re.findall(r"[\u4e00-\u9fff]", text)) >= 20


def digest_display(docs: str = DOCS) -> tuple[str, str]:
    """返回 (页面显示日期, 更新时间文本)。

    以 candidates.json 里那次抓取的 UTC 时间（generated_at）为锚点换算北京时间，
    而不是用构建时的 now —— 这样无论隔多久重新构建，页面上的日期和时间都不会变。
    candidates.json 缺失时退化为“本期落款的次日 06:00”，仍与定时任务对齐。
    """
    anchor = None
    cand_path = os.path.join(docs, "candidates.json")
    post_day = ""
    if os.path.isdir(POSTS):
        files = sorted(f for f in os.listdir(POSTS) if re.search(r"-summary-(zh|en)\.md$", f))
        if files:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", files[-1])
            post_day = m.group(1) if m else ""
    if os.path.exists(cand_path):
        try:
            with open(cand_path, encoding="utf-8") as f:
                raw_at = json.load(f).get("generated_at", "")
            if raw_at:
                anchor = datetime.fromisoformat(raw_at)
        except (OSError, ValueError):
            anchor = None
    if anchor is None and post_day:
        try:
            anchor = datetime.strptime(post_day, "%Y-%m-%d").replace(
                hour=22, minute=0, tzinfo=timezone.utc)
        except ValueError:
            anchor = None
    if anchor is None:
        bj = datetime.now(timezone.utc) + timedelta(hours=8)
    else:
        if anchor.tzinfo is None:
            anchor = anchor.replace(tzinfo=timezone.utc)
        bj = anchor + timedelta(hours=8)
    return bj.date().isoformat(), bj.strftime("%Y-%m-%d %H:%M") + " 北京时间"


def render_candidates(cands: list[dict], src_count: str, generated_at: str = "") -> str:
    """把「从 N 条里筛出」做成可点开的面板：只列表题和原文链接，不消耗任何 token。"""
    if not cands:
        return ""
    rows = []
    for i, c in enumerate(cands, 1):
        title = clean_text(c.get("title") or "")
        url = esc_url(c.get("url") or "")
        score = html.escape(str(c.get("score") or ""))
        meta = f'<span class="cm">{score}/10 · {html.escape(c.get("profile") or "")}</span>' if score else ""
        link = f'<a href="{url}" target="_blank" rel="noopener">{title}</a>' if url else title
        rows.append(f'<li>{link}{meta}</li>')
    scored = any(c.get("score") for c in cands)
    if scored:
        head = f"全部候选 {len(cands)} 条 · 展开查看"
        if src_count and str(len(cands)) == str(src_count):
            head = f"从 {src_count} 条内容中筛出 · 展开全部 {len(cands)} 条"
    else:
        head = f"本次抓取候选 {len(cands)} 条（未评分） · 展开查看"
    if generated_at:
        head = f"{head} · {generated_at}"
    return (
        '<details class="cands"><summary>'
        f'<span class="cbtn">{head}</span></summary>'
        f'<ol class="clist">{"".join(rows)}</ol></details>'
    )


def render_bilingual(zh: dict | None, en: dict | None) -> str:
    """同一条新闻先英文、再中文，上下对照，不做语言切换。"""
    idx_en = {i["anchor"]: i for i in (en or {}).get("items", [])}
    idx_zh = {i["anchor"]: i for i in (zh or {}).get("items", [])}
    titles = _group_titles(zh, en)

    blocks: list[str] = []

    if (zh or {}).get("summary"):
        blocks.append(f'<div class="summary"><span>📌</span><div><b>本期</b> · {clean_text(zh["summary"])}</div></div>')
    elif (en or {}).get("summary"):
        blocks.append(f'<div class="summary"><span>📌</span><div><b>Summary</b> · {clean_text(en["summary"])}</div></div>')

    emitted: list[str] = []
    source_toc = (zh or {}).get("toc") or (en or {}).get("toc") or []
    if source_toc:
        nav = "".join(
            f'<a href="#{i["anchor"]}"{en_attr((idx_zh.get(i["anchor"]) or idx_en.get(i["anchor"]) or i)["title"])}><span class="tt">{clean_text((idx_zh.get(i["anchor"]) or idx_en.get(i["anchor"]) or i)["title"])}</span></a>'
            for g in source_toc for i in g["items"]
            if i["anchor"] in idx_zh or i["anchor"] in idx_en
        )
        if nav:
            blocks.append(f'<div class="toc">{nav}</div>')

    for gi, g in enumerate(source_toc):
        anchors = [i["anchor"] for i in g["items"] if i["anchor"] in idx_zh or i["anchor"] in idx_en]
        if not anchors:
            continue
        label = titles[gi] if gi < len(titles) else g["group"]
        blocks.append(f'<div class="group">{clean_text(label)}<span>{len(anchors)} 条 / items</span></div>')
        # 同一组卡片包进独立容器：宽屏时用 CSS Grid 平分两栏，窄屏时就是普通单列。
        # 不用多栏（column-count）：WebKit/Safari 对 column-span:all 的重排不稳定，
        # 会在 iPad 上出现"首次单列、往下划才变两栏"这类抖动。
        cards: list[str] = []
        for a in anchors:
            cards.append(_card(a, idx_en.get(a), idx_zh.get(a)))
            emitted.append(a)
        blocks.append('<div class="cards">' + "".join(cards) + "</div>")

    stray: list[str] = []
    for a in list(idx_zh) + list(idx_en):
        if a not in emitted:
            stray.append(_card(a, idx_en.get(a), idx_zh.get(a)))
            emitted.append(a)
    if stray:
        blocks.append('<div class="cards">' + "".join(stray) + "</div>")

    return '<div class="flow">' + "".join(blocks) + "</div>"


def main() -> None:
    posts = {}
    for lang in ("zh", "en"):
        p = newest_post(lang)
        if p:
            posts[lang] = (p, parse_post(p))
            print(f"[ok] {lang} <= {os.path.basename(p)} ({len(posts[lang][1]['items'])} items)")

    if not posts:
        print("[skip] no posts")
        return

    day = next(iter(posts.values()))[1]["day"]
    count = max(len(d["items"]) for _, d in posts.values())
    if count == 0:
        print("[skip] this run produced 0 items; keeping the previous page online")
        return
    src_count = ""
    for _, d in posts.values():
        m = re.search(r"从\s*(\d+)\s*条", d["summary"])
        if m:
            src_count = m.group(1)
            break

    body = render_bilingual(posts.get("zh", (None, None))[1], posts.get("en", (None, None))[1])

    cands = []
    cand_at = ""
    cand_path = os.path.join(DOCS, "candidates.json")
    if os.path.exists(cand_path):
        try:
            with open(cand_path, encoding="utf-8") as f:
                payload = json.load(f)
            cands = payload.get("items", [])
            raw_at = payload.get("generated_at", "")
            if raw_at:
                try:
                    # 候选时间也按北京时间显示，和页面上的其它时间保持一致
                    cand_at = (datetime.fromisoformat(raw_at) + timedelta(hours=8)).strftime("%m-%d %H:%M")
                except ValueError:
                    cand_at = raw_at[:16].replace("T", " ")
                # 候选清单必须是本次这批内容的，否则不展示，避免把上一轮的旧列表冒充本次候选
                if raw_at[:10] != day:
                    print(f"[warn] candidates.json is from {raw_at[:10]} but digest is {day}; panel disabled")
                    cands = []
                    cand_at = ""
        except Exception as exc:
            print(f"[warn] candidates.json unreadable: {exc}")
            cands = []
            cand_at = ""
    cand_block = render_candidates(cands, src_count, cand_at)

    zh_items = (posts.get("zh", (None, None))[1] or {}).get("items", [])
    bilingual = sum(1 for it in zh_items if _has_chinese(it))
    pills = f'<span class="pill">共 {count} 条精选</span>'
    if bilingual and bilingual < count:
        pills += f'<span class="pill">双语 {bilingual} 条</span>'
    if os.path.exists(os.path.join(DOCS, "vocab.html")):
        pills += '<a class="pill pill-link" href="vocab.html">难点词汇 ›</a>'

    now = datetime.now(timezone.utc)
    # 页面日期与“更新时间”都以这次抓取的 UTC 时间为锚点换算到北京时间，
    # 不随构建时刻漂移（重建不会把日期改回前一天）。
    # 注意：latest.json 里的 generated_at 仍是 UTC，guard 用它算小时数，不受影响。
    display_day, updated_text = digest_display(DOCS)
    bj_now = now + timedelta(hours=8)

    page = TEMPLATE.format(
        title=f"KIKI 每日速递 {display_day}",
        hero_title=f"{display_day} 科技 · 财经 · 国际速递",
        updated=updated_text,
        updated_short=display_day,
        pills=pills,
        cands=cand_block,
        body=body,
    )
    page = plain_quotes(page)
    with open(os.path.join(DOCS, "latest.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("[ok] latest.html (en above zh)")

    if "en" in posts:
        en_page = TEMPLATE.format(
            title=f"KIKI Daily {display_day}",
            hero_title=f"{display_day} Tech · Finance · World",
            updated=updated_text,
            updated_short=display_day,
            pills=pills,
            cands=cand_block,
            body=render_bilingual(None, posts["en"][1]),
        )
        with open(os.path.join(DOCS, "latest-en.html"), "w", encoding="utf-8") as f:
            f.write(plain_quotes(en_page))
        print("[ok] latest-en.html")

    manifest = {
        "generated_at": now.isoformat(timespec="seconds"),
        "date": display_day,
        "item_count": count,
        "items": [
            {"lang": l, "date": d["day"], "file": "latest.html" if l == "zh" else "latest-en.html",
             "source": os.path.basename(p)}
            for l, (p, d) in posts.items()
        ],
    }
    with open(os.path.join(DOCS, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("[ok] latest.json")


if __name__ == "__main__":
    main()
