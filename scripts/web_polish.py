"""给静态页面注入「现代 Web 视觉增强」——幂等，可反复跑。

做四件事（全部是渐进增强，老浏览器/关掉动效的用户完全无感）：

1. `<link rel="expect" href="#kiki-head" blocking="render">`：跨文档视图过渡开始前，
   等页面顶栏（hero / bar）解析完再拍快照，避免过渡动画拍到白页（mwg: consistent-cross-document-transitions）。
2. `<script type="speculationrules">`：同源 html 预渲染（moderate），点「难点词汇」时基本零等待。
3. 一段 CSS：`@view-transition` 跨页淡入淡出 + 卡片滚动驱动入场 + 按钮微交互。
   只动 opacity / transform，全部在合成层，不占主线程；`prefers-reduced-motion: reduce` 时逐条关掉。
4. 给顶栏元素补 `id="kiki-head"`（页面里没有可用锚点，只在第一个 .hero / .bar 上加）。

用法：python scripts/web_polish.py docs/latest.html docs/latest-en.html docs/vocab.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

START = "<!-- kiki-polish:start -->"
END = "<!-- kiki-polish:end -->"

CSS = """
<style id="kiki-polish-css">
/* ——— KIKI 视觉增强：纯 CSS、零 JS、全部跑在合成层 ——— */
@view-transition{navigation:auto}
@media (prefers-reduced-motion: reduce){
  @view-transition{navigation:none}
}
/* 跨页衔接：旧页轻微上浮淡出，新页自下淡入。念「难点词汇」和「返回」都走这条 */
@media (prefers-reduced-motion: no-preference){
  ::view-transition-old(root){animation:kiki-out 240ms cubic-bezier(.32,.72,.24,1) both}
  ::view-transition-new(root){animation:kiki-in 300ms cubic-bezier(.22,.82,.26,1) both}
}
@keyframes kiki-out{from{opacity:1;transform:none}to{opacity:0;transform:translateY(-10px)}}
@keyframes kiki-in{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}

/* 卡片随滚动入场：滚动驱动动画，不监听 scroll，不影响滚动流畅度 */
@supports (animation-timeline: view()){
  @media (prefers-reduced-motion: no-preference){
    .card{animation:kiki-rise linear both;animation-timeline:view();animation-range:entry 2% entry 40%}
  }
}
@keyframes kiki-rise{from{opacity:.4;transform:translateY(16px)}to{opacity:1;transform:none}}

/* 按钮与链接微交互：只改 transform / 阴影 / 颜色 */
.pill,.back,.say,.vw{transition:transform 150ms cubic-bezier(.2,.8,.2,1),box-shadow 220ms ease,
  border-color 220ms ease,color 150ms ease,background-color 150ms ease}
@media (hover: hover){
  .pill:hover,.back:hover{transform:translateY(-2px);box-shadow:0 10px 20px rgba(0,0,0,.28)}
  .vw:hover{color:#8fc4ff;background:rgba(90,166,255,.12);border-radius:5px}
}
.pill:active,.back:active{transform:translateY(0) scale(.97)}
.vw{border-radius:5px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:8px}

/* 同页锚点跳转（词卡互链）平滑滚动 */
@media (prefers-reduced-motion: no-preference){html{scroll-behavior:smooth}}
</style>
""".strip()

SPECULATION = '<script type="speculationrules">{"prerender":[{"where":{"href_matches":"/*.html"},"eagerness":"moderate"}]}</script>'
EXPECT = '<link rel="expect" href="#kiki-head" blocking="render">'


def strip_previous(html: str) -> str:
    """去掉上一次注入的块，保证幂等。"""
    html = re.sub(re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S)
    html = re.sub(r'<style id="kiki-polish-css">.*?</style>', "", html, flags=re.S)
    html = re.sub(r'<link rel="expect" href="#kiki-head" blocking="render">\n?', "", html)
    html = re.sub(r'<script type="speculationrules">.*?</script>\n?', "", html, flags=re.S)
    return html


def ensure_head_id(html: str) -> str:
    """给顶栏补 id（只在第一个 .hero / .bar 上），供 view-transition / rel=expect 锚定。"""
    if re.search(r'id="kiki-head"', html):
        return html
    for cls in ("hero", "bar"):
        pat = re.compile(r'<div class="' + cls + r'">')
        if pat.search(html):
            return pat.sub(f'<div class="{cls}" id="kiki-head">', html, count=1)
    return html


def polish(html: str) -> str:
    html = strip_previous(html)
    html = ensure_head_id(html)
    # 只有真找到锚点才加 rel=expect：找不到时它会把首屏渲染一直挡到文档解析结束
    parts = [START]
    if 'id="kiki-head"' in html:
        parts.append(EXPECT)
    parts += [SPECULATION, CSS, END]
    block = "\n".join(parts) + "\n"
    if "</head>" in html:
        return html.replace("</head>", block + "</head>", 1)
    # 词汇页没写 <head>/</head>（隐式 head），退回到第一个 <style> 之后插入，效果等价
    if "</style>" in html:
        return html.replace("</style>", "</style>\n" + block, 1)
    return html


def main(argv: list[str]) -> int:
    files = [Path(p) for p in argv[1:]] or [
        Path("docs/latest.html"),
        Path("docs/latest-en.html"),
        Path("docs/vocab.html"),
    ]
    for path in files:
        if not path.exists():
            print(f"skip (missing): {path}")
            continue
        src = path.read_text(encoding="utf-8")
        out = polish(src)
        if out != src:
            path.write_text(out, encoding="utf-8")
            print(f"polished: {path} ({len(out) - len(src):+d} bytes)")
        else:
            print(f"unchanged: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
