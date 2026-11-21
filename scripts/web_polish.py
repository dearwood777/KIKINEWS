"""给静态页面注入「现代 Web 视觉增强」——幂等，可反复跑。

做五件事（全部是渐进增强，老浏览器/关掉动效的用户完全无感）：

1. `<link rel="expect" href="#kiki-head" blocking="render">`：跨文档视图过渡开始前，
   等页面顶栏（hero / bar）解析完再拍快照，避免过渡动画拍到白页。
2. `<script type="speculationrules">`：同源 html 预渲染（moderate），点「难点词汇」时基本零等待。
3. 跨页过渡：有方向（`types` 静态声明）+ 共享元素（「难点词汇 ›」和「‹ 返回今日速递」是同一个
   `view-transition-name`，会在两页之间飞过去）。所有过渡伪元素都刷成页面底色 `#0e1320`，
   快照层背后那层 UA 白画布不会再露出来。
4. 卡片：日报页滚动驱动入场；词汇页改「错峰点亮」（按序号 45ms 递增延迟，像灯一盏盏亮）。
5. 细节：目标卡片描边闪一下、`<details>` 高度动画、发音键水波纹、点按去方形蓝底、焦点描边。

用法：python scripts/web_polish.py docs/latest.html docs/latest-en.html docs/vocab.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

START = "<!-- kiki-polish:start -->"
END = "<!-- kiki-polish:end -->"

BG = "#0e1320"

CSS_HEAD = """
<style id="kiki-polish-css">
/* ——— KIKI 视觉增强：纯 CSS、零 JS ——— */
*{-webkit-tap-highlight-color:transparent}

/* 1. 跨页过渡的类型与方向 */
@view-transition{navigation:auto; types: {{TYPE}}}
@media (prefers-reduced-motion: reduce){
  @view-transition{navigation:none}
}

/* 2. 白闪根治：过渡快照层背后是 UA 的白色画布，只要哪一帧快照不满/半透明就露白。
   把画布和每一层伪元素都刷成页面底色，白色结构上不可能出现。 */
html{background-color:{{BG}}}
::view-transition{background-color:{{BG}}}
::view-transition-group(root),
::view-transition-image-pair(root),
::view-transition-old(root),
::view-transition-new(root){background-color:{{BG}}}

/* 3. 共享元素：「难点词汇 ›」在日报页、「‹ 返回今日速递」在词汇页，同名 → 跨页形变飞过去 */
.back,.pill-link{view-transition-name:kiki-pill}
::view-transition-group(kiki-pill){
  animation-duration:600ms;
  animation-timing-function:cubic-bezier(.22,1,.36,1);
  z-index:2;
}

@media (prefers-reduced-motion: no-preference){
  /* 进词汇页：新页自右推入，旧页被推走 */
  :active-view-transition-type(forward)::view-transition-old(root){
    animation:kiki-out-l 520ms cubic-bezier(.4,0,.2,1) both}
  :active-view-transition-type(forward)::view-transition-new(root){
    animation:kiki-in-r 600ms cubic-bezier(.22,1,.36,1) both}
  /* 返回：镜像 */
  :active-view-transition-type(previous)::view-transition-old(root){
    animation:kiki-out-r 520ms cubic-bezier(.4,0,.2,1) both}
  :active-view-transition-type(previous)::view-transition-new(root){
    animation:kiki-in-l 600ms cubic-bezier(.22,1,.36,1) both}
  /* 无类型的同站链接：淡入淡出 */
  ::view-transition-old(root){animation:kiki-fade-out 280ms ease both}
  ::view-transition-new(root){animation:kiki-fade-in 340ms ease both}
}
/* 只做位移，不碰 opacity / filter：快照一旦半透明就会透出底层画布 */
@keyframes kiki-out-l{from{transform:none}to{transform:translateX(-20%)}}
@keyframes kiki-out-r{from{transform:none}to{transform:translateX(20%)}}
@keyframes kiki-in-r{from{transform:translateX(66%)}to{transform:none}}
@keyframes kiki-in-l{from{transform:translateX(-66%)}to{transform:none}}
@keyframes kiki-fade-out{to{opacity:0}}
@keyframes kiki-fade-in{from{opacity:0}}

/* 4. 卡片入场 */
@keyframes kiki-rise{from{opacity:.45;transform:translateY(14px)}to{opacity:1;transform:none}}
{{CARDS}}

/* 5. 目录点进去的卡片描边闪一下，让人知道跳到哪儿了 */
@media (prefers-reduced-motion: no-preference){
  .card:target{animation:kiki-target 1.1s ease-out both}
}
@keyframes kiki-target{
  0%{box-shadow:0 0 0 2px var(--accent) inset,0 0 22px rgba(120,170,255,.35)}
  100%{box-shadow:0 0 0 2px transparent inset,0 0 0 rgba(120,170,255,0)}
}

/* 6. 展开/收起平滑：Chrome 131+ 的 ::details-content 高度动画，老浏览器直接瞬开 */
:root{interpolate-size:allow-keywords}
details::details-content{height:0;overflow:hidden;
  transition:height 300ms cubic-bezier(.2,.9,.2,1),content-visibility 300ms;transition-behavior:allow-discrete}
details[open]::details-content{height:auto}

/* 7. 按钮与链接微交互 */
.pill,.back,.say,.vw,.cbtn,.cands summary,.toc a{transition:transform 150ms cubic-bezier(.2,.8,.2,1),
  box-shadow 220ms ease,border-color 220ms ease,color 150ms ease,background-color 150ms ease}
/* <summary> 本身没有圆角，点按高亮会画成方块；补上跟 .cbtn 一致的圆角 */
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

/* 8. 发音键水波纹：按下从中心扩散一圈，松开淡出 */
.say::before{content:"";position:absolute;inset:-6px;border-radius:999px;pointer-events:none;
  background:radial-gradient(circle,rgba(127,184,255,.55),rgba(127,184,255,0) 70%);
  opacity:0;transform:scale(.55);
  transition:opacity 480ms ease-out,transform 480ms cubic-bezier(.2,.8,.2,1)}
.say:active::before{opacity:1;transform:scale(1.45);transition-duration:160ms}

/* 9. 同页锚点跳转平滑 */
@media (prefers-reduced-motion: no-preference){html{scroll-behavior:smooth}}
</style>
""".strip()

# 日报页：卡片随滚动入场（滚动驱动，零 JS）
CARDS_SCROLL = """@supports (animation-timeline: view()){
  @media (prefers-reduced-motion: no-preference){
    .cards>.card{animation:kiki-rise linear both;animation-timeline:view();animation-range:entry 2% entry 40%}
  }
}"""

# 词汇页：错峰点亮（按序号递增 45ms 延迟，超 10 张就封顶，避免最后一张等太久）
def cards_stagger(n: int = 10) -> str:
    lines = ["@media (prefers-reduced-motion: no-preference){",
             "  .cards>.card{animation:kiki-rise .5s cubic-bezier(.22,1,.36,1) both;",
             "    animation-delay:calc(min(var(--kiki-i,0)," + str(n) + ") * 45ms)}"]
    for i in range(1, n + 2):
        lines.append(f"  .cards>.card:nth-child({i}){{--kiki-i:{min(i - 1, n)}}}")
    lines.append("}")
    return "\n".join(lines)


SPECULATION = ('<script type="speculationrules">'
               '{"prerender":[{"where":{"href_matches":"/*.html"},"eagerness":"moderate"}]}'
               '</script>')
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


def is_vocab(html: str) -> bool:
    return 'id="w-' in html


def polish(html: str) -> str:
    html = strip_previous(html)
    html = ensure_head_id(html)
    vocab = is_vocab(html)
    css = (CSS_HEAD.replace("{{TYPE}}", "forward" if vocab else "previous")
                    .replace("{{BG}}", BG)
                    .replace("{{CARDS}}", cards_stagger() if vocab else CARDS_SCROLL))
    parts = [START]
    # 只有真找到锚点才加 rel=expect：找不到时它会把首屏渲染一直挡到文档解析结束
    if 'id="kiki-head"' in html:
        parts.append(EXPECT)
    parts += [SPECULATION, css, END]
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
