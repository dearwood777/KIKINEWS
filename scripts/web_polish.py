"""给静态页面注入「现代 Web 视觉增强」——幂等，可反复跑。

只做四类事（全部是渐进增强，老浏览器/关掉动效的用户完全无感）：

1. `<link rel="expect" href="#kiki-head" blocking="render">`：跨文档视图过渡开始前，
   等页面顶栏（hero / bar）解析完再拍快照，避免过渡动画拍到白页。
2. `<script type="speculationrules">`：同源 html 预渲染（moderate），点「难点词汇」时基本零等待。
3. 一段 CSS：
   - 有方向的整页推进（进词汇页 = 新页自右滑入、旧页左移变暗；返回 = 镜像），靠 `types` 静态区分；
   - 卡片滚动驱动入场、目标卡片高亮、按钮微交互；
   - `<details>` 展开高度动画、去掉点按时的方形蓝色高亮。
4. 给顶栏元素补 `id="kiki-head"`（页面里没有可用锚点，只在第一个 .hero / .bar 上加）。

用法：python scripts/web_polish.py docs/latest.html docs/latest-en.html docs/vocab.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

START = "<!-- kiki-polish:start -->"
END = "<!-- kiki-polish:end -->"

CSS_BASE = """
<style id="kiki-polish-css">
/* ——— KIKI 视觉增强：纯 CSS、零 JS、全部跑在合成层 ——— */
/* 0. 去掉安卓 WebView 默认的方形蓝色点按高亮（它按 <summary> 的方盒画，不看子元素圆角） */
*{-webkit-tap-highlight-color:transparent}
/* 1. 跨页过渡：两个方向都声明类型，动画放在 :active-view-transition-type() 里 */
@view-transition{navigation:auto; types: {{TYPE}}}
@media (prefers-reduced-motion: reduce){
  @view-transition{navigation:none}
}
@media (prefers-reduced-motion: no-preference){
  /* 进词汇页：新页从右侧推入，旧页被推走并压暗 */
  :active-view-transition-type(forward)::view-transition-old(root){
    animation:kiki-out-l 420ms cubic-bezier(.32,.72,.24,1) both}
  :active-view-transition-type(forward)::view-transition-new(root){
    animation:kiki-in-r 460ms cubic-bezier(.2,.9,.2,1) both}
  /* 返回：方向镜像 */
  :active-view-transition-type(previous)::view-transition-old(root){
    animation:kiki-out-r 420ms cubic-bezier(.32,.72,.24,1) both}
  :active-view-transition-type(previous)::view-transition-new(root){
    animation:kiki-in-l 460ms cubic-bezier(.2,.9,.2,1) both}
  /* 没有类型的导航（同站其它链接）走淡入淡出 */
  ::view-transition-old(root){animation:kiki-fade-out 260ms ease both}
  ::view-transition-new(root){animation:kiki-fade-in 320ms ease both}
}
@keyframes kiki-out-l{from{transform:none;filter:none}to{transform:translateX(-18%);filter:brightness(.82)}}
@keyframes kiki-out-r{from{transform:none;filter:none}to{transform:translateX(18%);filter:brightness(.82)}}
@keyframes kiki-in-r{from{transform:translateX(68%);opacity:.75}to{transform:none;opacity:1}}
@keyframes kiki-in-l{from{transform:translateX(-68%);opacity:.75}to{transform:none;opacity:1}}
@keyframes kiki-fade-out{to{opacity:0}}
@keyframes kiki-fade-in{from{opacity:0}}

/* 2. 卡片随滚动入场：滚动驱动动画，不监听 scroll，不影响滚动流畅度 */
@supports (animation-timeline: view()){
  @media (prefers-reduced-motion: no-preference){
    .card{animation:kiki-rise linear both;animation-timeline:view();animation-range:entry 2% entry 40%}
  }
}
@keyframes kiki-rise{from{opacity:.45;transform:translateY(14px)}to{opacity:1;transform:none}}

/* 3. 目录点进去的卡片闪一下边框，让人知道跳到哪儿了 */
@media (prefers-reduced-motion: no-preference){
  .card:target{animation:kiki-target 1.1s ease-out both}
}
@keyframes kiki-target{
  0%{box-shadow:0 0 0 2px var(--accent) inset, 0 0 22px rgba(120,170,255,.35)}
  100%{box-shadow:0 0 0 2px transparent inset, 0 0 0 rgba(120,170,255,0)}
}

/* 4. 展开/收起平滑：Chrome 131+ 的 ::details-content 高度动画，老浏览器直接瞬开 */
:root{interpolate-size:allow-keywords}
details::details-content{height:0;overflow:hidden;
  transition:height 280ms cubic-bezier(.2,.9,.2,1),content-visibility 280ms;transition-behavior:allow-discrete}
details[open]::details-content{height:auto}

/* 5. 按钮与链接微交互：只改 transform / 阴影 / 颜色 */
.pill,.back,.say,.vw,.cbtn,.cands summary,.toc a{transition:transform 150ms cubic-bezier(.2,.8,.2,1),
  box-shadow 220ms ease,border-color 220ms ease,color 150ms ease,background-color 150ms ease}
/* <summary> 本身没有圆角，点按高亮会画成方块；给它补上跟 .cbtn 一致的圆角 */
.cands summary{border-radius:999px}
@media (hover: hover){
  .pill:hover,.back:hover{transform:translateY(-2px);box-shadow:0 10px 20px rgba(0,0,0,.28)}
  .vw:hover{color:#8fc4ff;background:rgba(90,166,255,.12);border-radius:5px}
  .cbtn:hover{border-color:var(--accent)}
}
.pill:active,.back:active{transform:translateY(0) scale(.97)}
.cbtn:active{transform:scale(.98);background:var(--chip)}
.vw{border-radius:5px}
/* 焦点描边只加 outline，不改元素自己的圆角（否则胶囊会瞬间变方） */
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}

/* 6. 同页锚点跳转平滑 */
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


def nav_type(html: str) -> str:
    """目标页声明过渡类型：词汇页是「进入」，日报页是「返回」。"""
    return "forward" if 'id="w-' in html else "previous"


def polish(html: str) -> str:
    html = strip_previous(html)
    html = ensure_head_id(html)
    parts = [START]
    # 只有真找到锚点才加 rel=expect：找不到时它会把首屏渲染一直挡到文档解析结束
    if 'id="kiki-head"' in html:
        parts.append(EXPECT)
    parts += [SPECULATION, CSS_BASE.replace("{{TYPE}}", nav_type(html)), END]
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
