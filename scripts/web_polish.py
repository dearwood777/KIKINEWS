"""给静态页面注入「现代 Web 视觉增强」——幂等，可反复跑。

做这几件事（全部是渐进增强，老浏览器/关掉动效的用户完全无感）：

1. `<link rel="expect" href="#kiki-head" blocking="render">`：跨文档视图过渡开始前，
   等页面顶栏（hero / bar）解析完再拍快照，避免过渡动画拍到白页。
2. 跨页过渡：**旧页不动，只有新页整幅从侧边盖过来**。旧页一旦被平移，画面边缘就会露出
   过渡层底下那层画布（WebView 里就是白的，来回快速点几次必现）；旧页原地不动、新页完全
   覆盖到位，中间没有任何"露底"的时机 —— 白闪从结构上消灭，不再依赖给伪元素刷底色。
3. 共享元素：`.pill-link`（难点词汇 ›）与 `.back`（‹ 返回今日速递）共用
   `view-transition-name: kiki-pill`，会跨页飞过去。
4. 卡片：滚进视野时外框爆一圈水波纹（首屏已有的卡不参与，避免一进来就"依次闪下去"）；
   目录跳转到目标卡时连扩两圈 + 底色扫过。
5. 细节：`<details>` 高度动画、发音键「一圈一圈」的水波纹（真环形扩展）、
   点按去方形蓝底、焦点描边。
6. 一段极小的内联 JS：外框水波纹元素生成 + 发音键水波纹 + 连续点击去抖。

用法：python scripts/web_polish.py docs/latest.html docs/latest-en.html docs/vocab.html
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

START = "<!-- kiki-polish:start -->"
END = "<!-- kiki-polish:end -->"

BG = "#0e1320"

# 报头字形轮廓（由 scripts/build_head_glyphs.py 从 docs/fonts/kiki-head-700.woff2 导出）。
# 缺这个文件时小人整体不启用，其余特效照常。
try:
    GLYPHS = json.loads((Path(__file__).with_name("head_glyphs.json")).read_text(encoding="utf-8"))
    GLYPHS_JS = json.dumps(GLYPHS, ensure_ascii=False, separators=(",", ":"))
except Exception:  # noqa: BLE001
    GLYPHS = None
    GLYPHS_JS = "null"

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

/* 5. 卡片水波纹：和发音键**完全同一套**——几圈细线同时往外荡，最外圈先到边、里圈依次接上，
   最后一起淡掉。卡片自己的子元素会被 overflow:hidden 裁掉，所以环挂在卡片外面（.cards 里），
   按卡片的实际位置摆好，随页面一起滚动。线宽恒定 1.5px，外扩总量 9px（小于 10px 卡片间距）。 */
@keyframes kiki-cring-rip{
  0%{opacity:.82;transform:scale(1)}
  55%{opacity:.42}
  100%{opacity:0;transform:scale(var(--kx,1.06),var(--ky,1.06))}
}
.kiki-cring{position:absolute;pointer-events:none;opacity:0;
  border:1px solid rgba(127,184,255,.7);
  animation:kiki-cring-rip 2000ms cubic-bezier(.3,.4,.4,1) forwards;will-change:transform,opacity}
.cards{position:relative}
@keyframes kiki-wash{0%{opacity:0}30%{opacity:.75}100%{opacity:0}}
.kiki-glow{position:absolute;inset:0;border-radius:inherit;pointer-events:none;opacity:0;
  background:linear-gradient(158deg,rgba(127,184,255,.16),rgba(127,184,255,0) 60%);
  animation:kiki-wash 1150ms ease forwards}

/* 5c. 边缘流光（Border Beam）：**一条**光沿胶囊描边绕行一圈。
   演进过三版，前两版都废了，别回头：
   ① conic-gradient 旋转 —— 胶囊是又扁又长的"体育场"形，锥形渐变转同一角度，落点在直边和
      两端圆弧上走的距离差好几倍，几何上不可能匀速（"慢慢走、唰一下冲过弧"）。
   ② offset-path 沿路径 —— 实机 WebView 里整条光渲染不出来，直接消失。
   ③ 线性渐变横扫 —— 匀速了，但上下两条边同时亮，是"两束光"而不是"一道光溜边"。
   定版：SVG 描边 + stroke-dashoffset。路径按胶囊实际宽高生成，一段短亮线沿轮廓匀速走完，
   拖一条暗尾；几何上天然匀速，只可能出现一条光。 */
.cbtn{position:relative}
.kiki-beam{position:absolute;top:-1px;left:-1px;pointer-events:none;overflow:visible}
/* 路径本身不动，靠每层自己的 animation-delay 决定它在亮头后面多远（延迟由 JS 按路径长度算） */
.kiki-beam path{animation:kiki-beam-run 6000ms linear infinite both}
@keyframes kiki-beam-run{from{stroke-dashoffset:0}to{stroke-dashoffset:calc(-1 * var(--len))}}

/* 5d. 卡片入场淡入已下掉：`animation ... both` 会让卡片先被按到 opacity 0 再淡上来，
   快速滑到中途触发时反而是"整张卡消失一下又回来"，看着比不动更闪。 */

/* 5e. 数字递增用的数字容器：等宽数字 + 预留 2 位宽度，
   这样从 7 数到 12 时不会把右边的内容（比如「难点词汇 ›」）顶出去 */
.kiki-num{display:inline-block;font-variant-numeric:tabular-nums;text-align:center;vertical-align:baseline}

/* 5b. 背景星尘视差：极淡光点，随滚动反向慢移 */
@keyframes kiki-drift{to{transform:translateY(-96px)}}

/* 5d. 顶部阅读进度光条 */
@keyframes kiki-progress{to{transform:scaleX(1)}}
.kiki-progress{position:fixed;top:0;left:0;right:0;height:3px;z-index:9997;pointer-events:none;
  transform-origin:0 50%;transform:scaleX(0);opacity:0;
  background:linear-gradient(90deg,rgba(90,166,255,.55),rgba(127,184,255,.95),rgba(210,235,255,.9));
  box-shadow:0 0 12px rgba(127,184,255,.45)}
{{CARDS}}

/* 6. 跳转到某张卡：等滚动真的停下来之后再发水波纹（之前一改 hash 就开始播，
   等滚到位时动画已经只剩最后一帧了，等于白播） */

/* 6b. 滚动驱动 / 时间驱动的高级特效（Chrome 115+ 支持滚动时间线，不支持就完全不出现） */
@supports (animation-timeline: scroll()){
  @media (prefers-reduced-motion: no-preference){
    /* 背景星尘：负 z-index 让它压在本页背景之上、内容之下 */
    body::before{content:"";position:fixed;inset:-20% -10%;z-index:-1;pointer-events:none;opacity:.55;
      background:
        radial-gradient(1px 1px at 18% 26%,rgba(150,195,255,.55),transparent 60%),
        radial-gradient(1px 1px at 72% 62%,rgba(150,195,255,.45),transparent 60%),
        radial-gradient(1.6px 1.6px at 42% 84%,rgba(120,170,255,.34),transparent 60%),
        radial-gradient(1px 1px at 88% 18%,rgba(185,215,255,.42),transparent 60%),
        radial-gradient(1px 1px at 56% 44%,rgba(140,180,255,.28),transparent 60%);
      background-size:460px 460px;
      animation:kiki-drift linear both;animation-timeline:scroll(root)}
    .kiki-progress{opacity:1;animation:kiki-progress linear both;animation-timeline:scroll(root)}
  }
}
/* 滚动驱动的 3D 归正已下掉：它的进度跟着手指走，快速滑动时会在中途"停住再弹回"，很尬。 */

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

/* 9. 发音键水波纹：一条**极细**的空心圆环一圈圈往外扩（由内联 JS 生成 ring 元素）
   线宽 1.5px 且不随缩放变粗多少，保持精致感 */
.kiki-ring{position:absolute;inset:0;border-radius:999px;pointer-events:none;
  border:1.5px solid rgba(127,184,255,.75);opacity:0;
  animation:kiki-rip 860ms cubic-bezier(.2,.6,.3,1) forwards}
@keyframes kiki-rip{
  0%{opacity:.85;transform:scale(.72)}
  55%{opacity:.38}
  100%{opacity:0;transform:scale(2.02)}
}

/* 10. 同页锚点跳转平滑 */
@media (prefers-reduced-motion: no-preference){html{scroll-behavior:smooth}}

/* 11. 报头小人骨架
   报头字体换成为此专门打包的子集（Noto Sans SC 700，只含"科技·财经国际速递"这几个字，2.6KB，
   OFL 授权可自由分发）。换字体的意义是：字形轮廓由我们自己掌握，隐藏层里画的轮廓
   和屏幕上真正渲染的轮廓来自同一份数据，才会"脚踩在笔画上"。不换字体就只能拿字框近似。 */
@font-face{font-family:'KikiHead';src:url('fonts/kiki-head-700.woff2') format('woff2');
  font-weight:700;font-style:normal;font-display:swap}
.hero h1{font-family:'KikiHead',-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC',
  'Hiragino Sans GB','Microsoft YaHei',sans-serif;position:relative}
/* 逐字拆成 inline-block 只为能单独颤一下那个间隔点；字距仍由 h1 的 letter-spacing 控制。
   white-space:pre 是关键：否则只含一个空格的 span 会把空格折叠掉，"科技·财经"两侧的
   间隙就消失，整行比原来窄 28px（实测 331→303）。 */
.hero h1 .kch{display:inline-block;white-space:pre;transform-origin:50% 100%;will-change:transform}
.hero h1 .kch.kiki-dot-hit{animation:kiki-dot 300ms cubic-bezier(.3,.7,.4,1)}
@keyframes kiki-dot{
  0%{transform:translateY(0) scaleY(1)}
  28%{transform:translateY(1.2px) scaleY(.86)}
  62%{transform:translateY(-.8px) scaleY(1.05)}
  100%{transform:translateY(0) scaleY(1)}
}
/* 小人层：绝对定位盖在报头上，不吃点击，只动 transform（不触发重排） */
.kiki-walker{position:absolute;left:0;top:0;width:1px;height:1px;pointer-events:none;
  will-change:transform;transition:opacity .35s ease}
.kiki-walker svg{display:block;overflow:visible}
.kiki-walker .kw-leg{transform-box:fill-box;transform-origin:50% 0}
.kiki-walker .kw-body{transform-box:fill-box;transform-origin:50% 50%}
</style>
""".strip()

CARDS_SCROLL = """/* 日报卡：入场由 CSS 的 3D 归正 + JS 的水波纹脉冲负责，这里只需要定位上下文 */
.cards>.card{position:relative}"""


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
  // 报头字形骨架：{"upm":1000,"d":{字:路径,...},"adv":{...}}，由 build_head_glyphs.py 生成
  var KIKI_G = {{GLYPHS}};
  window.KIKI_G = KIKI_G;   // 便于线上调试/校验（渲染时也读这份）

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

  // 3) 卡片水波纹：和发音键**完全同一套**——几圈细线同时往外荡，最外圈先到边，
  //    里圈依次接上，最后一起淡掉。卡片自己的子元素会被 overflow:hidden 裁掉，
  //    所以环挂在卡片外面（挂在 .cards 里），按卡片位置摆好，跟着页面一起滚。
  function pop(card, delay) {
    setTimeout(function () {
      var glow = document.createElement('span');
      glow.className = 'kiki-glow';
      card.insertBefore(glow, card.firstChild);
      setTimeout(function () { glow.remove(); }, 1400);

      var host = card.parentNode;
      if (!host) return;
      if (getComputedStyle(host).position === 'static') host.style.position = 'relative';

      var cr = card.getBoundingClientRect(), pr = host.getBoundingClientRect();
      if (!cr.width) return;
      var kx = (cr.width + 18) / cr.width;     // 总共外扩 18px（每边 9px，小于 10px 卡片间距）
      var ky = (cr.height + 18) / cr.height;
      var radius = getComputedStyle(card).borderTopLeftRadius;

      // 三圈细线：起跑间隔 320ms（肉眼能看出先后），收束时长递减 → 最后几乎同时淡掉
      [[0, 2050], [320, 1850], [640, 1680]].forEach(function (p) {
        var ring = document.createElement('span');
        ring.className = 'kiki-cring';
        ring.style.left = (cr.left - pr.left) + 'px';
        ring.style.top = (cr.top - pr.top) + 'px';
        ring.style.width = cr.width + 'px';
        ring.style.height = cr.height + 'px';
        ring.style.borderRadius = radius;
        ring.style.setProperty('--kx', kx);
        ring.style.setProperty('--ky', ky);
        ring.style.animationDelay = p[0] + 'ms';
        ring.style.animationDuration = p[1] + 'ms';
        host.appendChild(ring);
        setTimeout(function () { ring.remove(); }, p[0] + p[1] + 60);
      });
    }, delay || 0);
  }

  // 3c) 边缘流光：一条光沿胶囊描边绕行（SVG 路径 + stroke-dashoffset，匀速）
  function stadiumD(w, h) {
    var r = Math.min(h / 2, w / 2) - 0.5, t = 0.5;
    var p = [[t + r, t], [w - t - r, t], [w - t, t + r], [w - t, h - t - r],
             [w - t - r, h - t], [t + r, h - t], [t, h - t - r], [t, t + r]];
    var a = ' A' + r + ' ' + r + ' 0 0 1 ';
    return 'M' + p[0] + ' L' + p[1] + a + p[2] + ' L' + p[3] + a + p[4]
         + ' L' + p[5] + a + p[6] + ' L' + p[7] + a + p[0];
  }
  // 线速度：与屏幕宽度无关的"匀速"基准（px/秒）。一圈时长由胶囊周长算出来。
  // 但纯匀速有个副作用：手机竖屏周长只有 744px，一圈 4s 就跑完，虽然线速度一样，
  // 观感上"绕得太勤"显得快。所以再给一圈时长加下限 MIN_DUR，把短胶囊压慢一点；
  // 大小屏的圈时差距也从 2.4 倍收到 1.8 倍以内。
  var BEAM_SPEED = 160;
  var MIN_DUR = 6200;
  function buildBeam() {
    var btn = document.querySelector('.cbtn');
    if (!btn || !document.createElementNS) return;
    var old = btn.querySelector('svg.kiki-beam');
    if (old) old.remove();                       // 旋转屏幕/换布局后要按新尺寸重画
    var w = btn.offsetWidth, h = btn.offsetHeight;
    if (!w || !h) return;
    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('class', 'kiki-beam');
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    svg.setAttribute('width', w); svg.setAttribute('height', h);
    var d = stadiumD(w, h);
    function layer(dash, behind, color, width, blur, cls) {
      var p = document.createElementNS(ns, 'path');
      p.setAttribute('d', d);
      p.setAttribute('fill', 'none');
      p.setAttribute('stroke', color);
      p.setAttribute('stroke-width', width);
      p.setAttribute('stroke-linecap', 'round');
      p.setAttribute('stroke-dasharray', dash + ' 9999'); // 占位，len 算出来后再按"整圈"改
      p.__dash = dash;
      if (blur) p.style.filter = 'blur(' + blur + 'px)';
      p.setAttribute('class', cls);
      svg.appendChild(p);
      return p;
    }
    // 尺寸随胶囊宽度缩放：竖屏（约 380px 宽）按 1 倍，横屏/平板按比例拉长，
    // 否则固定 138px 的尾巴在大宽屏上会显得像个小点。粗细只按 s^0.55 放大，避免又变笨。
    var s = Math.min(2.6, Math.max(1, w / 380));
    var ws = Math.pow(s, 0.55);
    var LAYERS = [
      [138, 104, 'rgba(70,140,255,.08)', 0.60, 0, 'b8'],
      [116,  84, 'rgba(80,150,255,.14)', 0.70, 0, 'b7'],
      [96,   66, 'rgba(95,165,255,.22)', 0.78, 0, 'b6'],
      [78,   50, 'rgba(110,180,255,.31)', 0.88, 0, 'b5'],
      [62,   36, 'rgba(125,190,255,.41)', 0.96, 0, 'b4'],
      [48,   24, 'rgba(140,200,255,.52)', 1.05, 0, 'b3'],
      [36,   14, 'rgba(160,210,255,.64)', 1.12, 0, 'b2'],
      [22,    0, 'rgba(150,200,255,.30)', 2.40, 2.4, 'bg'],   // 头部外发光
      [26,    6, 'rgba(185,220,255,.78)', 1.20, 0, 'b1'],
      [16,    0, 'rgba(232,244,255,.95)', 1.30, 0, 'b0']      // 亮芯
    ];
    LAYERS.forEach(function (L) {
      layer(Math.round(L[0] * s), Math.round(L[1] * s), L[2],
            +(L[3] * ws).toFixed(2), L[4] ? +(L[4] * ws).toFixed(2) : 0, L[5]);
    });
    var head = svg.querySelector('.b0');
    btn.appendChild(svg);
    var len = head.getTotalLength();
    var dur = Math.min(18000, Math.max(MIN_DUR, Math.round(len / BEAM_SPEED * 1000)));
    svg.style.setProperty('--len', len + 'px');
    var offs = { b0: 0, bg: 0, b1: 6, b2: 14, b3: 24, b4: 36, b5: 50, b6: 66, b7: 84, b8: 104 };
    Object.keys(offs).forEach(function (cls) {
      var el = svg.querySelector('.' + cls);
      if (!el) return;
      var behind = Math.min(offs[cls] * s, len / 2 - 10);
      el.style.animationDuration = dur + 'ms';
      el.style.animationDelay = (-dur * (len - behind) / len) + 'ms';
      // 关键：虚线周期必须正好等于整圈周长（dash + gap = len）。
      // 用 9999 这种超大 gap 时，光跑到起点(左上圆角)那一刻会被路径末端截断，
      // 出现"断一下再冒出来"；周期=len 时末端被截掉的那段会同时从起点补回来，接缝是连着的。
      var gap = Math.max(0.5, len - el.__dash);
      el.setAttribute('stroke-dasharray', el.__dash.toFixed(2) + ' ' + gap.toFixed(2));
    });
  }

  // 3b) 跳到某张卡（目录 / 跨页锚点）：等滚动真的停下来再发水波纹。
  //     以前是 :target 一改 hash 就开播，等滚到位动画只剩最后一帧，等于白播。
  var popped = {};
  function popHash() {
    var id = location.hash.slice(1);
    try { id = decodeURIComponent(id); } catch (e) { /* 保持原样 */ }
    if (!id || popped[id]) return;
    var el = document.getElementById(id);
    if (!el || !el.classList || !el.classList.contains('card')) return;
    popped[id] = 1;
    setTimeout(function () { delete popped[id]; }, 1600);
    pop(el, 0);
  }

  function afterScroll(fn) {
    var done = false;
    var go = function () { if (done) return; done = true; fn(); };
    if ('onscrollend' in window) window.addEventListener('scrollend', go, { once: true });
    setTimeout(go, 720);
  }
  window.addEventListener('hashchange', function () { afterScroll(popHash); });

  // 3a) 跨文档带锚点落地（主页点正文里的超纲词跳到词汇卡）：浏览器自己的锚点滚动会被吃掉。
  //     实测：直接打开 vocab.html#w-x 能滚到位；但从另一页点链接进来，落到 scrollY=0 ——
  //     新页面 URL 带着 #，位置却停在顶部。原因是锚点滚动与「平滑滚动 + 视图过渡」撞车：
  //     平滑滚动的动画刚起跑就被快照/过渡打断，回到 0。
  //     对策：落地时临时把 scroll-behavior 改成 auto 做一次硬跳（瞬间到位，不走平滑），
  //     跳完立刻还原，页内的目录点击仍然是平滑滚动。
  function hardLand() {
    if (!location.hash) return;
    var id = location.hash.slice(1);
    try { id = decodeURIComponent(id); } catch (e) { /* 原样 */ }
    var el = document.getElementById(id);
    if (!el) return;
    var root = document.documentElement, prev = root.style.scrollBehavior;
    root.style.scrollBehavior = 'auto';
    el.scrollIntoView({ block: 'start' });
    root.style.scrollBehavior = prev;
  }
  // 图片/字体稍后加载会把落点顶偏，900ms 后再校一次（仍然是硬跳，看不出第二次跳）
  if (location.hash) {
    setTimeout(function () {
      var el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (!el) return;
      var top = el.getBoundingClientRect().top;
      var want = parseFloat(getComputedStyle(el).scrollMarginTop) || 0;
      if (Math.abs(top - want) > 8) hardLand();
    }, 900);
  }
  window.addEventListener('load', hardLand);

  // 数字递增第 1 步：把数字折进 .kiki-num。必须尽早做（DOMContentLoaded，还没绘制），
  // 否则页面已经画出来再插 span，宽度会"宽一下"——从词汇页返回时尤其明显。
  // 宽度只按目标位数留位：原本 1 位的「双语 7 条」不会多占一格，右边内容不会被顶开。
  function wrapNums() {
    var nums = document.querySelectorAll('.pillrow span.pill,.cbtn .l,.cbtn .r,.summary > div,.bar .count');
    Array.prototype.forEach.call(nums, function (el) {
      if (el.getAttribute('data-kiki-wrapped')) return;
      var w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null), n, t = null;
      while ((n = w.nextNode())) { if (/[0-9]/.test(n.nodeValue)) { t = n; break; } }
      if (!t) return;
      var m = t.nodeValue.match(/[0-9]+/);
      if (!m) return;
      var target = parseInt(m[0], 10);
      if (!target || target > 9999) return;
      el.setAttribute('data-kiki-wrapped', '1');

      var pad = String(target).length;
      var before = t.nodeValue.slice(0, m.index), after = t.nodeValue.slice(m.index + m[0].length);
      t.nodeValue = before;
      var span = document.createElement('span');
      span.className = 'kiki-num';
      span.style.minWidth = pad + 'ch';
      span.textContent = new Array(pad + 1).join('0');
      var par = t.parentNode;
      par.insertBefore(span, t.nextSibling);
      par.insertBefore(document.createTextNode(after), span.nextSibling);
      el.__kikiNum = { span: span, target: target, pad: pad };
    });
  }

  var beamRz;
  function scheduleBeam() { clearTimeout(beamRz); beamRz = setTimeout(buildBeam, 180); }

  // 3d) 报头小人：踩在字的**真实上沿**往右走，遇到空隙就跳过去，落到间隔点那一下点会颤。
  //     地形不是手写的坐标，是把报头专用字体里的字形轮廓栅格化后"逐列取最上面的墨迹"得来的，
  //     所以换字号 / 换设备 / 横竖屏都是自动贴合，不需要调像素。
  var walkerRz;
  function scheduleWalker() { clearTimeout(walkerRz); walkerRz = setTimeout(buildWalker, 220); }

  function buildWalker() {
    var h1 = document.querySelector('.hero h1');
    if (!h1 || !KIKI_G || !KIKI_G.d || !window.Path2D) return;
    var old = h1.querySelector('.kiki-walker');
    if (old) old.remove();

    // (1) 逐字拆 span：只为能单独颤那个间隔点。inline-block 下字距仍由 h1 的 letter-spacing 管
    if (!h1.__kch) {
      var raw = h1.textContent, arr = [], i;
      h1.textContent = '';
      for (i = 0; i < raw.length; i++) {
        var sp = document.createElement('span');
        sp.className = 'kch';
        sp.textContent = raw.charAt(i);
        h1.appendChild(sp);
        arr.push(sp);
      }
      h1.__kch = arr;
    }
    var chars = h1.__kch, cs = getComputedStyle(h1);
    var F = parseFloat(cs.fontSize) || 23;
    var LH = parseFloat(cs.lineHeight) || F * 1.3;
    var hr = h1.getBoundingClientRect();
    var W = Math.max(40, Math.ceil(hr.width)), H = Math.ceil(F * 2.2);
    var k = F / (KIKI_G.upm || 1000);

    // (2) 骨架：字形轮廓以 2 倍超采样画进 canvas，再逐列扫描 alpha
    var cvs = document.createElement('canvas');
    cvs.width = W * 2; cvs.height = H * 2;
    var ctx = cvs.getContext('2d');
    if (!ctx) return;
    ctx.font = '700 ' + F + 'px KikiHead';        // 用浏览器自己的字体度量，别硬编码 asc/desc
    var mt = ctx.measureText('科');
    var asc = mt.fontBoundingBoxAscent || F * 1.16, desc = mt.fontBoundingBoxDescent || F * 0.288;
    var base = (LH - (asc + desc)) / 2 + asc;     // 半行距 + 上沿：和 CSS 行框严丝合缝
    ctx.scale(2, 2);
    ctx.fillStyle = '#fff';
    chars.forEach(function (sp) {
      var d = KIKI_G.d[sp.textContent];
      if (!d) return;
      var r = sp.getBoundingClientRect();
      ctx.save();
      ctx.translate(r.left - hr.left, base);
      ctx.scale(k, -k);
      try { ctx.fill(new Path2D(d)); } catch (e) { /* 单字失败就跳 */ }
      ctx.restore();
    });
    var img;
    try { img = ctx.getImageData(0, 0, cvs.width, cvs.height).data; } catch (e) { return; }
    function alpha(x, y) { return img[(y * cvs.width + x) * 4 + 3]; }
    var top = [], x, y;
    for (x = 0; x < W; x++) {
      top[x] = -1;
      for (y = 0; y < cvs.height; y++) {
        if (alpha(Math.min(cvs.width - 1, x * 2), y) > 28) { top[x] = y / 2; break; }
      }
    }

    // (3) 间隔点的真实墨迹直径 → 小人高度 = 点直径 × 2（用户定的比例）
    var dot = null, dotSpan = null;
    chars.forEach(function (sp) {
      if (sp.textContent !== '·') return;
      dotSpan = sp;
      var r = sp.getBoundingClientRect();
      var cx = Math.round((r.left - hr.left + r.width / 2) * 2);
      cx = Math.max(0, Math.min(cvs.width - 1, cx));
      var t = -1, b = -1;
      for (var yy = 0; yy < cvs.height; yy++) {
        if (alpha(cx, yy) > 28) { if (t < 0) t = yy; b = yy; }
      }
      if (t >= 0) dot = { x0: r.left - hr.left, x1: r.left - hr.left + r.width, t: t / 2, b: b / 2 };
    });
    var dH = dot ? Math.max(2, dot.b - dot.t) : F * 0.26;
    var SH = Math.max(8, dH * 2);      // 小人高度 = 点直径 × 2
    var SW = SH * 0.7;

    // (4) 地形分段：连续的墨迹列 = 一段可走的平地，段与段之间就是要跳的空隙
    var runs = [], cur = null;
    for (x = 0; x < W; x++) {
      if (top[x] >= 0) {
        if (!cur) { cur = { x0: x, x1: x }; runs.push(cur); }
        cur.x1 = x;
      } else cur = null;
    }
    var merged = [];
    runs.forEach(function (r) {
      var last = merged[merged.length - 1];
      if (last && r.x0 - last.x1 <= 5) last.x1 = r.x1;   // 字形内部的小缺口并掉，免得一步一跳
      else merged.push({ x0: r.x0, x1: r.x1 });
    });
    if (!merged.length) return;

    // (5) 时间线：走一段 → 跳一段 → 走一段……速度按字号定，字大字小节奏一致
    var SPEED = Math.max(14, F * 1.1);
    var segs = [], acc = 0;
    merged.forEach(function (r, i2) {
      var d = Math.max(80, (r.x1 - r.x0) / SPEED * 1000);
      segs.push({ walk: 1, x0: r.x0, x1: r.x1, d: d, t0: acc });
      acc += d;
      var nxt = merged[i2 + 1];
      if (nxt) {
        var jd = Math.max(120, Math.abs(nxt.x0 - r.x1) / SPEED * 1000 * 1.15);
        segs.push({ walk: 0, x0: r.x1, x1: nxt.x0, d: jd, t0: acc, fy: top[r.x1], ty: top[nxt.x0] });
        acc += jd;
      }
    });

    // (6) 小人本体：现在先用一个通用占位形象（换形象只要改这段字符串）
    var walker = document.createElement('div');
    walker.className = 'kiki-walker';
    walker.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" width="' + SW.toFixed(1) + '" height="' + SH.toFixed(1) +
      '" viewBox="0 0 8 12" shape-rendering="geometricPrecision">' +
      '<line class="kw-antenna" x1="4" y1="1.6" x2="4" y2=".5" stroke="#ffb84d" stroke-width=".5"/>' +
      '<circle cx="4" cy=".42" r=".42" fill="#ffcf7a"/>' +
      '<g class="kw-body">' +
      '<rect x="1.7" y="1.7" width="4.6" height="6.2" rx="2.2" fill="#d6e9ff" stroke="#8ec2ff" stroke-width=".45"/>' +
      '<circle cx="4" cy="4.0" r=".72" fill="#2f6bff"/>' +
      '<circle cx="4" cy="4.0" r=".28" fill="#eaf4ff"/>' +
      '</g>' +
      '<g class="kw-leg kw-legL"><line x1="3.2" y1="7.9" x2="3.2" y2="11.6" stroke="#9fc9ff" stroke-width=".55"/></g>' +
      '<g class="kw-leg kw-legR"><line x1="4.8" y1="7.9" x2="4.8" y2="11.6" stroke="#9fc9ff" stroke-width=".55"/></g>' +
      '</svg>';
    h1.appendChild(walker);
    var body = walker.querySelector('.kw-body');
    var legL = walker.querySelector('.kw-legL'), legR = walker.querySelector('.kw-legR');

    // (7) 播放：一圈走完停 2.6s 再来；报头滚出视野就暂停
    var startT = performance.now(), alive = true, pass = -1, raf = 0;
    var loop = acc + 2600;
    function shake() {
      if (!dotSpan) return;
      dotSpan.classList.remove('kiki-dot-hit');
      void dotSpan.offsetWidth;           // 强制重排，让动画能重播
      dotSpan.classList.add('kiki-dot-hit');
    }
    function frame(ts) {
      raf = requestAnimationFrame(frame);
      if (!alive) return;
      var t = (ts - startT) % loop;
      var s = segs[segs.length - 1], idx = segs.length - 1, i3;
      for (i3 = 0; i3 < segs.length; i3++) {
        if (t < segs[i3].t0 + segs[i3].d) { s = segs[i3]; idx = i3; break; }
      }
      var u = t > acc ? 1 : Math.min(1, Math.max(0, (t - s.t0) / s.d));
      var wx, fy;
      if (t > acc) {
        wx = segs[segs.length - 1].x1;
        fy = top[Math.round(wx)]; if (fy < 0) fy = 0;
      } else if (s.walk) {
        wx = s.x0 + (s.x1 - s.x0) * u;
        fy = top[Math.round(wx)]; if (fy < 0) fy = 0;
      } else {
        wx = s.x0 + (s.x1 - s.x0) * u;
        fy = s.fy + (s.ty - s.fy) * u - Math.sin(Math.PI * u) * SH * 0.5;   // 抛物线
      }
      walker.style.transform = 'translate(' + (wx - SW / 2).toFixed(2) + 'px,' + (fy - SH).toFixed(2) + 'px)';

      // 腿部摆动：走是交替迈步，跳是收腿；身体跟着轻点头
      var rot = 0, ph = 0;
      if (s.walk && t <= acc) {
        ph = (u * s.d / 1000) * 6.4;
        rot = Math.sin(ph) * 15;
        legL.style.transform = 'rotate(' + rot.toFixed(1) + 'deg)';
        legR.style.transform = 'rotate(' + (-rot).toFixed(1) + 'deg)';
        body.style.transform = 'translateY(' + (Math.sin(ph * 2) * 0.12).toFixed(2) + 'px)';
      } else {
        legL.style.transform = 'rotate(13deg)';
        legR.style.transform = 'rotate(-13deg)';
        body.style.transform = 'translateY(-0.15px)';
      }

      // 落在间隔点上：点颤一下（每个 jump 段每圈只触发一次）
      var pid = Math.floor((ts - startT) / loop);
      if (!s.walk && u > 0.86 && s.__pid !== pid && dot && s.x1 > dot.x0 - 2 && s.x1 < dot.x1 + 2) {
        s.__pid = pid; shake();
      }
    }
    raf = requestAnimationFrame(frame);

    // 报头不在视野里就停（省电，避免后台空转）
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        alive = es[0].isIntersecting;
      }, { threshold: 0.15 }).observe(h1);
    }
  }


  function start() {
    buildBeam();
    // 屏幕旋转 / 折叠屏切换 / 窗口变化：胶囊长度变了就得按新轮廓重画，
    // 否则光还在照着旧的（竖屏那条短）路径跑。
    var beamBtn = document.querySelector('.cbtn');
    if (beamBtn && window.ResizeObserver) {
      new ResizeObserver(scheduleBeam).observe(beamBtn);
    }
    window.addEventListener('resize', scheduleBeam);
    window.addEventListener('orientationchange', function () { setTimeout(buildBeam, 320); setTimeout(buildWalker, 360); });
    // 报头小人：字体是外链 woff2，等它真正到了再量（否则量到的是回退字体的行高）
    buildWalker();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(scheduleWalker);
    window.addEventListener('resize', scheduleWalker);
    hardLand();          // 跨文档带 #锚点进来时，见下方 hardLand 注释
    // 顶部阅读进度光条（滚动时间线驱动，不支持就什么都不显示）
    var bar = document.createElement('div');
    bar.className = 'kiki-progress';
    document.body.appendChild(bar);

    var cards = document.querySelectorAll('.cards > .card');

    // 首屏已经在画面里的卡不参与：一进来就"依次闪下去"很别扭。只有后面滚进来的才发。
    var initial = [];
    var h = window.innerHeight;
    Array.prototype.forEach.call(cards, function (c) {
      var r = c.getBoundingClientRect();
      if (r.top < h - 40 && r.bottom > 0) initial.push(c);
    });

    // 卡片滚进视野：发水波纹（淡入已去掉，见 CSS 5d 注释）
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          io.unobserve(en.target);
          if (initial.indexOf(en.target) >= 0) return;  // 进来时就在画面里，跳过
          pop(en.target, 0);
        });
      }, { threshold: 0.3, rootMargin: '0px 0px -8% 0px' });
      Array.prototype.forEach.call(cards, function (c) { io.observe(c); });
    }

    // 数字递增：报头/候选条/摘要里的数字从 0 数上去，滚进视野触发一次。
    // wrapNums() 已在 DOMContentLoaded 提前折好，这里只负责触发。
    function countUp(el) {
      var d = el.__kikiNum;
      if (!d || el.getAttribute('data-kiki-counted')) return;
      el.setAttribute('data-kiki-counted', '1');
      var span = d.span, target = d.target, pad = d.pad;
      var t0 = null, dur = 1800;              // 1.8s：太快会"一进页面就数完了"，看不出效果
      function frame(ts) {
        if (t0 === null) t0 = ts;
        var p = Math.min(1, (ts - t0) / dur);
        var e = 1 - Math.pow(1 - p, 3);          // ease out cubic
        var v = String(Math.round(target * e));
        while (v.length < pad) v = '0' + v;
        span.textContent = v;
        if (p < 1) requestAnimationFrame(frame);
      }
      setTimeout(function () { requestAnimationFrame(frame); }, 180);
      // 兜底：标签页被切走时 rAF 会暂停，恢复不了就会一直停在 0，这里保证最终值一定落地
      setTimeout(function () {
        var fin = String(target);
        while (fin.length < pad) fin = '0' + fin;
        span.textContent = fin;
      }, 180 + dur + 400);
    }
    var nums = document.querySelectorAll('.pillrow span.pill,.cbtn .l,.cbtn .r,.summary > div,.bar .count');
    if ('IntersectionObserver' in window) {
      var cio = new IntersectionObserver(function (es) {
        es.forEach(function (en) {
          if (!en.isIntersecting) return;
          cio.unobserve(en.target); countUp(en.target);
        });
      }, { threshold: 0.4 });
      Array.prototype.forEach.call(nums, function (n) { cio.observe(n); });
    } else {
      Array.prototype.forEach.call(nums, countUp);
    }

    // 带锚点进来的（比如从主页点超纲词跳到某张卡）：滚到位后再发
    if (location.hash) setTimeout(popHash, 120);
  }
  var wait = 640;
  // 数字容器要尽早折进去：DOMContentLoaded 立刻 wrap（此时还没绘制，宽度一定），
  // 免得像之前那样等 640ms 才插 span，页面已经画出来又"宽一下"，每回一次页面都跳。
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { wrapNums(); setTimeout(start, wait); });
  } else {
    wrapNums();
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


def ensure_font(target_dir: Path | None = None) -> None:
    """把报头字体子集从 scripts/ 复制到 docs/fonts/。

    字体放在 scripts/ 而不是 docs/，是因为 **往 main 的 docs/** 推任何文件都会触发
    deploy-docs.yml，把 main 上那份过期的 docs 全量发布到 gh-pages，覆盖掉当天的新页面
    （2026-11-22 就是这么被覆盖成 11-18 的）。让 polish 在运行时自己复制，
    Actions 的工作区里就自动有这个文件，主仓 docs 永远不需要动。
    """
    src = Path(__file__).with_name("kiki-head-700.woff2")
    if not src.exists():
        return
    dst_dir = Path(target_dir or "docs/fonts")
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / "kiki-head-700.woff2"
        if (not dst.exists()) or dst.stat().st_size != src.stat().st_size:
            dst.write_bytes(src.read_bytes())
    except OSError:
        pass


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
    # 词汇页没有报头，字形骨架（7.9KB）没必要塞进去
    parts += [SPECULATION, css, JS.replace("{{GLYPHS}}", "null" if vocab else GLYPHS_JS), END]
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
    # 报头字体：脚本自己把文件复制进 docs/fonts（这样 Actions 的 docs 里一定有它，
    # 而主仓的 docs/ 永远不用改，避免触发 deploy-docs 覆盖页面）
    if files:
        ensure_font(files[0].parent / "fonts")
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

