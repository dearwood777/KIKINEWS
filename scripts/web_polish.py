"""给静态页面注入「现代 Web 视觉增强」——幂等，可反复跑。

做这几件事（全部是渐进增强，老浏览器/关掉动效的用户完全无感）：

1. `<link rel="expect" href="#kiki-head" blocking="render">`：跨文档视图过渡开始前，
   等页面顶栏（hero / bar）解析完再拍快照，避免过渡动画拍到白页。
2. 跨页过渡：**旧页不动，只有新页整幅从侧边盖过来**。旧页一旦被平移，画面边缘就会露出
   过渡层底下那层画布（WebView 里就是白的，来回快速点几次必现）；旧页原地不动、新页完全
   覆盖到位，中间没有任何"露底"的时机 —— 白闪从结构上消灭，不再依赖给伪元素刷底色。
3. 共享元素：`.pill-link`（难点词汇 ›）与 `.back`（‹ 返回今日速递）共用
   `view-transition-name: kiki-pill`，会跨页飞过去。
4. 卡片：**抖绸带**——整列像一块布被提起来再往下甩，波峰顺着卡片往下走（`.kiki-wave`，
   按序号每隔 72ms 递增）；卡片落地/滚进画面时外框爆一圈水波纹。
5. 细节：目标卡片连扩两圈、`<details>` 高度动画、发音键「一圈一圈」的水波纹（真环形扩展）、
   点按去方形蓝底、焦点描边。
6. 一段极小的内联 JS：绸带波纹的编号与触发（跨页过渡结束后才起跑，所以不会和转场快照打架）、
   外框水波纹元素生成、发音键水波纹、连续点击去抖（防止 700ms 内反复触发跨页过渡）。

用法：python scripts/web_polish.py docs/latest.html docs/latest-en.html docs/vocab.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

START = "<!-- kiki-polish:start -->"
END = "<!-- kiki-polish:end -->"

BG = "#0e1320"

CSS_TEMPLATE = """
<style id="kiki-polish-css">
/* ——— KIKI 视觉增强 ——— */
*{-webkit-tap-highlight-color:transparent}

/* 1. 过渡类型（目标页静态声明方向） */
@view-transition{navigation:auto; types: {{TYPE}}}
@media (prefers-reduced-motion: reduce){
  @view-transition{navigation:none}
}

/* 2. 画布兜底色：页面本身、过渡层、根分组全部铺满底色，任何一帧都不会露出 WebView 的白 */
html{background-color:{{BG}}}
::view-transition{background-color:{{BG}}}
::view-transition-group(root),
::view-transition-image-pair(root),
::view-transition-old(root),
::view-transition-new(root){background-color:{{BG}}}

/* 3. 共享元素胶囊：跨页飞过去 */
.back,.pill-link{view-transition-name:kiki-pill}
::view-transition-group(kiki-pill){
  animation-duration:620ms;
  animation-timing-function:cubic-bezier(.22,1,.36,1);
}

/* 4. 关键：旧页原地不动，只有新页整幅覆盖进来。
   旧页一平移就会在边缘露出底下画布（白闪的根源），不移动就永远不会露出。 */
@media (prefers-reduced-motion: no-preference){
  :active-view-transition-type(forward)::view-transition-old(root),
  :active-view-transition-type(previous)::view-transition-old(root){animation:none}
  :active-view-transition-type(forward)::view-transition-new(root){
    animation:kiki-cover-r 620ms cubic-bezier(.32,.86,.3,1) both}
  :active-view-transition-type(previous)::view-transition-new(root){
    animation:kiki-cover-l 620ms cubic-bezier(.32,.86,.3,1) both}
  /* 无类型的同站链接：极短淡入，快照全程不透明 */
  ::view-transition-old(root){animation:none}
  ::view-transition-new(root){animation:kiki-fade-in 200ms ease both}
}
@keyframes kiki-cover-r{from{transform:translateX(100%)}to{transform:none}}
@keyframes kiki-cover-l{from{transform:translateX(-100%)}to{transform:none}}
@keyframes kiki-fade-in{from{opacity:0}to{opacity:1}}

/* 5. 卡片「抖绸带」入场：整列像一块布被提起再往下甩，波峰顺着卡片往下走。
   只动 transform，卡片本体不淡入不出场，所以不会和跨页转场快照打架（也就不会抖） */
@keyframes kiki-ribbon{
  0%{transform:translateY(0) rotate(0deg)}
  20%{transform:translateY(-15px) rotate(-.7deg)}
  46%{transform:translateY(7px) rotate(.35deg)}
  68%{transform:translateY(-2.5px) rotate(-.12deg)}
  86%{transform:translateY(1px)}
  100%{transform:translateY(0) rotate(0deg)}
}
.kiki-wave{animation:kiki-ribbon 940ms cubic-bezier(.3,.72,.22,1) both;
  animation-delay:calc(min(var(--kiki-i,0),12) * 72ms);will-change:transform}
/* 卡片外框水波纹：真的空心圆环从卡片边缘往外扩一圈再淡掉（和发音键同一套视觉语言） */
@keyframes kiki-halo-rip{
  0%{opacity:.92;transform:scale(1)}
  55%{opacity:.5}
  100%{opacity:0;transform:scale(1.075)}
}
/* 卡片「点亮」：一层冷蓝光洗过卡面，不动位置、不改尺寸 */
@keyframes kiki-wash{0%{opacity:0}32%{opacity:.9}100%{opacity:0}}
/* 卡片外框水波纹（由内联 JS 生成，日报页滚动到卡片 / 词汇页卡片落地时触发） */
.kiki-halo{position:absolute;inset:0;border-radius:inherit;pointer-events:none;opacity:0;
  border:2px solid rgba(127,184,255,.9);box-shadow:0 0 18px rgba(127,184,255,.5);
  animation:kiki-halo-rip 880ms cubic-bezier(.2,.7,.3,1) forwards}
/* 卡面被蓝光洗过一层（也由 JS 生成，插在卡片最前面，所以压在文字底下） */
.kiki-glow{position:absolute;inset:0;border-radius:inherit;pointer-events:none;opacity:0;
  background:linear-gradient(158deg,rgba(127,184,255,.22),rgba(127,184,255,0) 58%);
  animation:kiki-wash 1100ms ease forwards}
{{CARDS}}

/* 6. 目录跳转后的卡片：外框连扩两圈（水波纹），同时底色扫过，2.4s 收尾 */
@media (prefers-reduced-motion: no-preference){
  .card:target{animation:kiki-target 2400ms cubic-bezier(.2,.8,.2,1) both}
  .card:target::after{animation:kiki-halo-rip 900ms cubic-bezier(.2,.7,.3,1) 2 both}
}
@keyframes kiki-target{
  0%{box-shadow:0 0 0 3px var(--accent) inset,0 0 34px rgba(120,170,255,.5);
     background-color:rgba(120,170,255,.10)}
  55%{box-shadow:0 0 0 2px rgba(120,170,255,.35) inset,0 0 18px rgba(120,170,255,.18);
     background-color:rgba(120,170,255,.04)}
  100%{box-shadow:0 0 0 2px transparent inset,0 0 0 rgba(120,170,255,0);
      background-color:transparent}
}

/* 7. 展开/收起平滑：Chrome 131+ 的 ::details-content 高度动画，老浏览器直接瞬开 */
:root{interpolate-size:allow-keywords}
details::details-content{height:0;overflow:hidden;
  transition:height 300ms cubic-bezier(.2,.9,.2,1),content-visibility 300ms;transition-behavior:allow-discrete}
details[open]::details-content{height:auto}

/* 8. 按钮与链接微交互 */
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

/* 9. 发音键水波纹：真的空心圆环，一层层往外扩（由内联 JS 生成 ring 元素） */
.kiki-ring{position:absolute;inset:0;border-radius:999px;pointer-events:none;
  border:2px solid rgba(127,184,255,.8);opacity:0;
  animation:kiki-rip 760ms cubic-bezier(.2,.7,.3,1) forwards}
@keyframes kiki-rip{
  0%{opacity:.9;transform:scale(.6)}
  60%{opacity:.45}
  100%{opacity:0;transform:scale(2)}
}

/* 10. 同页锚点跳转平滑 */
@media (prefers-reduced-motion: no-preference){html{scroll-behavior:smooth}}
</style>
""".strip()

CARDS_SCROLL = """/* 日报卡：入场交给 JS 的「抖绸带」（.kiki-wave 按顺序延迟），这里只留外框水波纹容器 */
.cards>.card{position:relative}
.cards>.card::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;
  border:2px solid rgba(127,184,255,.9);box-shadow:0 0 18px rgba(127,184,255,.5);opacity:0}"""


def cards_stagger(n: int = 10) -> str:
    """词汇页卡片：本体在跨页转场期间保持完全静止（以前是自己从右侧滑进来，
    转场快照拍到"滑到一半"的卡，转场结束切回实时页面状态对不上 → 第一张卡抖一下）。

    入场改由内联 JS 触发 `.kiki-wave`（抖绸带）+ 落地爆一圈水波纹，全部只动 transform / opacity。
    """
    return ("/* 词汇卡：入场由 JS 的抖绸带驱动，这里只保留波纹容器 */\n"
            ".cards>.card{position:relative}")


JS = """
<script id="kiki-polish-js">
(function () {
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 1) 发音键水波纹：点一次发两圈，先后 140ms
  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('.say') : null;
    if (!btn) return;
    [0, 140].forEach(function (delay) {
      var ring = document.createElement('span');
      ring.className = 'kiki-ring';
      ring.style.animationDelay = delay + 'ms';
      btn.appendChild(ring);
      setTimeout(function () { ring.remove(); }, 1000 + delay);
    });
  }, true);

  // 2) 连续点击去抖：700ms 内只允许发起一次跨页跳转。
  var last = 0;
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    if (a.target === '_blank' || a.hasAttribute('download')) return;
    var href = a.getAttribute('href') || '';
    if (href.charAt(0) === '#' || href.indexOf('javascript:') === 0) return;
    var now = Date.now();
    if (now - last < 700) { e.preventDefault(); e.stopPropagation(); return; }
    last = now;
  }, true);

  if (reduce) return;

  // 3) 跨页过渡（620ms）收尾后才开始入场特效。
  //    以前特效跟转场同时起跑，转场快照拍到的是"动到一半"的画面，切回实时页面就会抖一下。
  //    现在卡片本体一动不动，只让发光元素在过渡结束后依次出现。
  function pop(card, delay) {
    setTimeout(function () {
      var glow = document.createElement('span');
      glow.className = 'kiki-glow';
      card.insertBefore(glow, card.firstChild);
      setTimeout(function () { glow.remove(); }, 1300);
      [0, 200].forEach(function (d) {
        setTimeout(function () {
          var halo = document.createElement('span');
          halo.className = 'kiki-halo';
          card.appendChild(halo);
          setTimeout(function () { halo.remove(); }, 1100);
        }, d);
      });
    }, delay || 0);
  }

  function start() {
    var cards = document.querySelectorAll('.cards > .card');
    var isVocab = !!document.querySelector('.back');

    // 抖绸带：给每个元素编号 --kiki-i，CSS 按编号递增延迟 → 波峰顺着列表往下走
    function ribbon(nodes, cap) {
      Array.prototype.forEach.call(nodes, function (el, i) {
        el.style.setProperty('--kiki-i', Math.min(i, cap));
        el.classList.add('kiki-wave');
        setTimeout(function () { el.classList.remove('kiki-wave'); },
          1100 + Math.min(i, cap) * 72);
      });
    }

    if (isVocab) {
      // 词汇页：整列卡片抖一次绸带，每张落地时爆一圈水波纹
      ribbon(cards, 12);
      Array.prototype.forEach.call(cards, function (c, i) {
        pop(c, Math.min(i, 12) * 72 + 430);
      });
    } else {
      // 日报页：摘要、目录卡与正文卡一起抖一次
      var blocks = document.querySelectorAll('.flow > .summary, .toc, .cards > .card');
      ribbon(blocks, 8);

      // 往下滚时，卡片进画面再爆一圈水波纹（时间驱动，和发音键同一套观感）
      if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) {
            if (!en.isIntersecting) return;
            io.unobserve(en.target);
            pop(en.target, 0);
          });
        }, { threshold: 0.35 });
        Array.prototype.forEach.call(cards, function (c) { io.observe(c); });
      }
    }
  }
  var wait = 640;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { setTimeout(start, wait); });
  } else {
    setTimeout(start, wait);
  }
})();
</script>
""".strip()

SPECULATION = ('<script type="speculationrules">'
               '{"prerender":[{"where":{"href_matches":"/*.html"},"eagerness":"moderate"}]}'
               '</script>')
EXPECT = '<link rel="expect" href="#kiki-head" blocking="render">'


def strip_previous(html: str) -> str:
    """去掉上一次注入的块，保证幂等。"""
    html = re.sub(re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S)
    html = re.sub(r'<style id="kiki-polish-css">.*?</style>', "", html, flags=re.S)
    html = re.sub(r'<script id="kiki-polish-js">.*?</script>', "", html, flags=re.S)
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
    css = (CSS_TEMPLATE.replace("{{TYPE}}", "forward" if vocab else "previous")
                       .replace("{{BG}}", BG)
                       .replace("{{CARDS}}", cards_stagger() if vocab else CARDS_SCROLL))
    parts = [START]
    # 只有真找到锚点才加 rel=expect：找不到时它会把首屏渲染一直挡到文档解析结束
    if 'id="kiki-head"' in html:
        parts.append(EXPECT)
    parts += [SPECULATION, css, JS, END]
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
