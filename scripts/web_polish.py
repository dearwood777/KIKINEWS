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
/* 绳子层：垫在小人下面，平时只有空隙处的"悬崖绳"是亮的 */
.kw-ropes{position:absolute;left:0;top:0;pointer-events:none;overflow:visible}
.kw-ropes .kw-rope-gap{stroke:#9c8a6d;stroke-width:1.1;stroke-linecap:round;opacity:.68}
.kw-ropes .kw-rope-back{stroke:#8b7f6b;stroke-width:1;stroke-linecap:round;opacity:0;
  transition:opacity .3s linear}
/* 小人：60×100 的关节骨架，transform 的 origin 放在脚底 */
.kw-pup{display:block;position:absolute;left:0;top:0;overflow:visible;
  transform-origin:50% 100%;user-select:none;transition:opacity .2s linear}
.kw-pup [stroke]{vector-effect:none}
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

  // 3d) 报头小人（葫芦娃 SVG 剪纸骨架 v4）
  //     关节骨架：头/躯干/双臂/双腿独立活动，真迈步、真抓绳攀爬，不是贴图平移。
  //     路线：沿字形上沿走 → 空隙点一下跳过去 → 到最右端沿字边爬下去 →
  //           手换手从字底下横爬回来（空隙处扒住悬在字底的绳）→ 最左端爬回字上沿。
  var walkerRz;
  function scheduleWalker() { clearTimeout(walkerRz); walkerRz = setTimeout(buildWalker, 220); }

  // 骨架：60×100 坐标系，脚底在 y≈99，整体朝右
  var PUP_SVG =
    '<svg class="kw-pup" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg">' +
    '<defs><linearGradient id="kwskin" x1="0" y1="0" x2="0" y2="1">' +
    '<stop offset="0" stop-color="#fcd9b6"/><stop offset="1" stop-color="#f0b688"/></linearGradient>' +
    '<linearGradient id="kwcoat" x1="0" y1="0" x2="0" y2="1">' +
    '<stop offset="0" stop-color="#f4563f"/><stop offset="1" stop-color="#c22f22"/></linearGradient></defs>' +

    // 白裤 + 光脚
    '<g class="kw-legL"><path d="M24 57.6 L29.8 57.6 L29.4 75.4 L24.4 75.4 Z" fill="#fdfaf3" stroke="#2a2320" stroke-width="1.2"/>' +
    '<g class="kw-kneeL"><path d="M24.3 73.4 L29.5 73.4 L28.8 93.6 L25 93.6 Z" fill="url(#kwskin)" stroke="#2a2320" stroke-width="1.1"/>' +
    '<path d="M25 92.6 L28.8 92.6 L31.4 96.6 Q32.2 99 29.6 99 L25 99 Q23.6 95.6 25 92.6 Z" fill="url(#kwskin)" stroke="#2a2320" stroke-width="1.1"/></g></g>' +
    '<g class="kw-legR"><path d="M30.2 57.6 L36 57.6 L35.6 75.4 L30.6 75.4 Z" fill="#f7f1e6" stroke="#2a2320" stroke-width="1.2"/>' +
    '<g class="kw-kneeR"><path d="M30.5 73.4 L35.7 73.4 L35 93.6 L31.2 93.6 Z" fill="url(#kwskin)" stroke="#2a2320" stroke-width="1.1"/>' +
    '<path d="M31.2 92.6 L35 92.6 L37.6 96.6 Q38.4 99 35.8 99 L31.2 99 Q29.8 95.6 31.2 92.6 Z" fill="url(#kwskin)" stroke="#2a2320" stroke-width="1.1"/></g></g>' +

    // 躯干：裸胸 + 红坎肩
    '<path d="M24 36.6 Q30 35 36 36.6 L35.4 57.6 Q30 59.6 24.6 57.6 Z" fill="url(#kwskin)"/>' +
    '<path d="M23.4 36.8 L27.6 35.8 L29.6 43 L27.2 46.2 L26.6 57.2 L24.4 56.8 Z" fill="url(#kwcoat)" stroke="#2a2320" stroke-width="1.1"/>' +
    '<path d="M36.6 36.8 L32.4 35.8 L30.4 43 L32.8 46.2 L33.4 57.2 L35.6 56.8 Z" fill="url(#kwcoat)" stroke="#2a2320" stroke-width="1.1"/>' +
    '<path d="M23.4 36.8 Q22.2 39 23 41.4 L25.4 38.4 Z" fill="#c22f22"/>' +
    '<path d="M36.6 36.8 Q37.8 39 37 41.4 L34.6 38.4 Z" fill="#c22f22"/>' +
    // 小绿叶项链
    '<path d="M27.6 37.6 Q30 40.4 32.4 37.6 Q30 38.6 27.6 37.6 Z" fill="#6fb84f" stroke="#2c431f" stroke-width=".9"/>' +
    '<path d="M29.4 38.4 Q27 40.6 25.4 39.6 Q27.4 38.6 29.4 38.4 Z" fill="#5da944" stroke="#2c431f" stroke-width=".8"/>' +
    '<path d="M30.6 38.4 Q33 40.6 34.6 39.6 Q32.6 38.6 30.6 38.4 Z" fill="#5da944" stroke="#2c431f" stroke-width=".8"/>' +
    // 腰带 + 草叶裙
    '<path d="M24.4 56.6 Q30 58.6 35.6 56.6 L35.5 60 Q30 62 24.5 60 Z" fill="#8a5a33" stroke="#3d2a16" stroke-width="1"/>' +
    '<path d="M24.6 59.4 Q20.6 62.6 21.8 67.6 Q26.4 65.6 28.4 61.6 Z" fill="#63ad4a" stroke="#2c431f" stroke-width="1"/>' +
    '<path d="M27.4 61.4 Q26.2 67 28.4 70.6 Q31 66.6 31.6 61.6 Z" fill="#57a341" stroke="#2c431f" stroke-width="1"/>' +
    '<path d="M31.8 61.6 Q32.8 67 36.4 68.6 Q37.4 63.4 37.2 59.6 Z" fill="#63ad4a" stroke="#2c431f" stroke-width="1"/>' +

    // 头
    '<ellipse cx="30.6" cy="24.4" rx="10.6" ry="11.2" fill="url(#kwskin)"/>' +
    // 后发（只盖头顶与两侧，不包下巴）
    '<path d="M19.8 25.4 Q19 12.6 30.4 11.8 Q42.2 12.6 41.4 25.4 Q40.6 19 37.6 17 Q30 15.4 23.4 17 Q20.6 19 19.8 25.4 Z" fill="#221d18"/>' +
    // 两鬓
    '<path d="M19.8 20.6 Q18.6 26 20.6 28.8 Q22.4 25.4 23.2 21.6 Z" fill="#221d18"/>' +
    '<path d="M41.4 20.6 Q42.6 26 40.6 28.8 Q38.8 25.4 38 21.6 Z" fill="#221d18"/>' +
    // 刘海（三缕）
    '<path d="M21.6 19.6 Q24 14.4 30.4 14.2 Q36.8 14.4 39.4 19.6 Q36.4 16.4 33.6 17.2 Q31.2 15.2 28.6 17 Q25 16 21.6 19.6 Z" fill="#221d18"/>' +
    // 耳
    '<ellipse cx="20.6" cy="25.6" rx="1.7" ry="2.3" fill="url(#kwskin)" stroke="#2a2320" stroke-width=".8"/>' +
    // 眼
    '<ellipse cx="27.4" cy="23.8" rx="2.7" ry="3" fill="#fffdf6" stroke="#2a2320" stroke-width=".8"/>' +
    '<ellipse cx="34.8" cy="23.6" rx="2.9" ry="3.2" fill="#fffdf6" stroke="#2a2320" stroke-width=".8"/>' +
    '<ellipse cx="28" cy="24.2" rx="1.7" ry="2.1" fill="#2f7f6a"/>' +
    '<ellipse cx="35.4" cy="24" rx="1.8" ry="2.2" fill="#2f7f6a"/>' +
    '<ellipse cx="28.1" cy="24.3" rx=".8" ry="1.3" fill="#141110"/>' +
    '<ellipse cx="35.5" cy="24.1" rx=".8" ry="1.4" fill="#141110"/>' +
    '<circle cx="27.2" cy="23" r=".65" fill="#fff"/>' +
    '<circle cx="34.6" cy="22.8" r=".7" fill="#fff"/>' +
    // 眉
    '<path d="M24.4 19.4 Q26.8 17.8 29.4 19.4" fill="none" stroke="#241e19" stroke-width="1" stroke-linecap="round"/>' +
    '<path d="M37.8 19.2 Q35.2 17.6 32.6 19.2" fill="none" stroke="#241e19" stroke-width="1" stroke-linecap="round"/>' +
    // 鼻、嘴、腮红
    '<path d="M36.4 26.4 Q37.4 27.6 36.2 28" fill="none" stroke="#c98a63" stroke-width=".9"/>' +
    '<path d="M28.6 30.6 Q30.6 32.2 32.6 30.4" fill="none" stroke="#b8544a" stroke-width="1" stroke-linecap="round"/>' +
    '<ellipse cx="24" cy="27.6" rx="1.9" ry="1.1" fill="#f2968a" opacity=".5"/>' +
    '<ellipse cx="37" cy="27.6" rx="1.9" ry="1.1" fill="#f2968a" opacity=".5"/>' +

    // 头顶小葫芦 + 红珠 + 两片叶
    '<path d="M30.4 12 Q30 9 31 6.2" stroke="#3f6f2f" stroke-width="1.1" fill="none"/>' +
    '<ellipse cx="31.4" cy="4.4" rx="2.9" ry="2.3" fill="#6fb84f" stroke="#2c431f" stroke-width=".9"/>' +
    '<ellipse cx="31.4" cy="1.8" rx="1.9" ry="1.6" fill="#5da944" stroke="#2c431f" stroke-width=".8"/>' +
    '<circle cx="31.4" cy=".5" r=".9" fill="#e0453a"/>' +
    '<path d="M28.6 8.4 Q24 5.6 20 8.2 Q24 11 28.6 9.6 Z" fill="#7ac155" stroke="#2c431f" stroke-width=".9"/>' +
    '<path d="M34.2 8.2 Q38.8 5.4 42.6 8 Q38.8 10.8 34.2 9.4 Z" fill="#6fb84f" stroke="#2c431f" stroke-width=".9"/>' +

    // 手臂：红短袖 + 细胳膊
    '<g class="kw-armL"><path d="M19.4 37.4 L23.4 35.6 L23 43.6 L19.8 44.4 Z" fill="url(#kwcoat)" stroke="#2a2320" stroke-width="1"/>' +
    '<g class="kw-elbL"><path d="M19.9 43.6 L22.7 43 L22.2 56 L20.4 56 Z" fill="url(#kwskin)" stroke="#2a2320" stroke-width=".9"/>' +
    '<ellipse cx="21.2" cy="57.8" rx="2.2" ry="2.5" fill="url(#kwskin)" stroke="#2a2320" stroke-width=".9"/></g></g>' +
    '<g class="kw-armR"><path d="M40.6 37.4 L36.6 35.6 L37 43.6 L40.2 44.4 Z" fill="url(#kwcoat)" stroke="#2a2320" stroke-width="1"/>' +
    '<g class="kw-elbR"><path d="M40.1 43.6 L37.3 43 L37.8 56 L39.6 56 Z" fill="url(#kwskin)" stroke="#2a2320" stroke-width=".9"/>' +
    '<ellipse cx="38.8" cy="57.8" rx="2.2" ry="2.5" fill="url(#kwskin)" stroke="#2a2320" stroke-width=".9"/></g></g>' +
    '</svg>';
  var PUP_JOINTS = [
    ['legL', '27px 58px'], ['kneeL', '26.6px 75px'], ['legR', '33px 58px'], ['kneeR', '33.4px 75px'],
    ['armL', '21.2px 37px'], ['elbL', '21px 44px'], ['armR', '38.8px 37px'], ['elbR', '39px 44px']
  ];

  function buildWalker() {
    var h1 = document.querySelector('.hero h1');
    if (!h1 || !KIKI_G || !KIKI_G.d || !window.Path2D) return;

    // (1) 逐字拆 span
    if (!h1.__kch) {
      var raw = h1.textContent, arr = [], i0;
      h1.textContent = '';
      for (i0 = 0; i0 < raw.length; i0++) {
        var sp0 = document.createElement('span');
        sp0.className = 'kch';
        sp0.textContent = raw.charAt(i0);
        h1.appendChild(sp0);
        arr.push(sp0);
      }
      h1.__kch = arr;
    }
    var chars = h1.__kch, cs = getComputedStyle(h1);
    var F = parseFloat(cs.fontSize) || 23;
    var LH = parseFloat(cs.lineHeight) || F * 1.3;
    var hr = h1.getBoundingClientRect();
    var W = Math.max(40, Math.ceil(hr.width)), H = Math.ceil(F * 2.6);
    var k = F / (KIKI_G.upm || 1000);
    var sig = W + '|' + F.toFixed(2) + '|' + LH.toFixed(2) + '|' + chars.length;
    if (h1.__kwSig === sig && h1.querySelector('.kiki-walker')) return;
    h1.__kwSig = sig;

    // (2) 栅格化取上沿 / 下沿
    var cvs = document.createElement('canvas');
    cvs.width = W * 2; cvs.height = H * 2;
    var ctx = cvs.getContext('2d');
    if (!ctx) return;
    ctx.font = '700 ' + F + 'px KikiHead';
    var mt = ctx.measureText('科');
    var asc = mt.fontBoundingBoxAscent || F * 1.16, desc = mt.fontBoundingBoxDescent || F * 0.288;
    var base = (LH - (asc + desc)) / 2 + asc;
    ctx.scale(2, 2);
    ctx.fillStyle = '#fff';
    chars.forEach(function (sp) {
      var d = KIKI_G.d[sp.textContent];
      if (!d) return;
      var r = sp.getBoundingClientRect();
      ctx.save();
      ctx.translate(r.left - hr.left, base);
      ctx.scale(k, -k);
      try { ctx.fill(new Path2D(d)); } catch (e) {}
      ctx.restore();
    });
    var img;
    try { img = ctx.getImageData(0, 0, cvs.width, cvs.height).data; } catch (e) { return; }
    function alpha(x, y) { return img[(y * cvs.width + x) * 4 + 3]; }
    var top = [], bot = [], x, y;
    for (x = 0; x < W; x++) {
      top[x] = -1; bot[x] = -1;
      for (y = 0; y < cvs.height; y++) {
        if (alpha(Math.min(cvs.width - 1, x * 2), y) > 28) { top[x] = y / 2; break; }
      }
      for (y = cvs.height - 1; y >= 0; y--) {
        if (alpha(Math.min(cvs.width - 1, x * 2), y) > 28) { bot[x] = y / 2; break; }
      }
    }
    // 站立面：脚掌只有 2~3px，只取 ±1 列的最高墨迹；再 ±2 列平均让曲线连续
    var env = [], ts = [], bs = [], d3;
    for (x = 0; x < W; x++) {
      var hi = -1, lo = -1;
      for (d3 = -1; d3 <= 1; d3++) {
        var xa = x + d3;
        if (xa < 0 || xa >= W) continue;
        if (top[xa] >= 0 && (hi < 0 || top[xa] < hi)) hi = top[xa];
        if (bot[xa] > lo) lo = bot[xa];
      }
      env[x] = hi;
      bs[x] = lo;
    }
    for (x = 0; x < W; x++) {
      var s1 = 0, n1 = 0, s2 = 0, n2 = 0;
      for (d3 = -2; d3 <= 2; d3++) {
        var xb = x + d3;
        if (xb < 0 || xb >= W) continue;
        if (env[xb] >= 0 && env[x] >= 0) { s1 += env[xb]; n1++; }
        if (bs[xb] >= 0 && bs[x] >= 0) { s2 += bs[xb]; n2++; }
      }
      ts[x] = n1 ? s1 / n1 : env[x];
      bot[x] = n2 ? s2 / n2 : bs[x];
    }

    // (3) 尺寸：间隔点墨迹直径 × 2.5
    var dots = [], dot = null;
    chars.forEach(function (sp) {
      if (sp.textContent !== '·') return;
      var r = sp.getBoundingClientRect();
      var cx = Math.max(0, Math.min(cvs.width - 1, Math.round((r.left - hr.left + r.width / 2) * 2)));
      var t = -1, b = -1;
      for (var yy = 0; yy < cvs.height; yy++) {
        if (alpha(cx, yy) > 28) { if (t < 0) t = yy; b = yy; }
      }
      if (t >= 0) dots.push({ x0: r.left - hr.left, x1: r.left - hr.left + r.width, t: t / 2, b: b / 2, span: sp });
    });
    dot = dots[0] || null;
    var dH = dot ? Math.max(2, dot.b - dot.t) : F * 0.26;
    var SH = Math.max(11, dH * 2.5);
    var SW = SH * 0.6;

    // (4) 可走段
    var runs = [], cur = null;
    for (x = 0; x < W; x++) {
      if (ts[x] >= 0) {
        if (!cur) { cur = { x0: x, x1: x }; runs.push(cur); }
        cur.x1 = x;
      } else cur = null;
    }
    var merged = [];
    runs.forEach(function (r) {
      var last = merged[merged.length - 1];
      if (last && r.x0 - last.x1 <= 4) last.x1 = r.x1;
      else merged.push({ x0: r.x0, x1: r.x1 });
    });
    if (merged.length < 2) return;

    // (5) 骨架 + 悬崖绳层
    var ns = 'http://www.w3.org/2000/svg';
    var ropes = document.createElementNS(ns, 'svg');
    ropes.setAttribute('class', 'kw-ropes');
    ropes.setAttribute('width', W);
    ropes.setAttribute('height', H);
    ropes.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    var walker = document.createElement('div');
    walker.className = 'kiki-walker';
    walker.innerHTML = PUP_SVG;
    var pup = walker.querySelector('.kw-pup');
    pup.setAttribute('width', SW.toFixed(1));
    pup.setAttribute('height', SH.toFixed(1));
    var J = {};
    PUP_JOINTS.forEach(function (pair) {
      var el = walker.querySelector('.kw-' + pair[0]);
      if (!el) return;
      el.style.transformBox = 'view-box';
      el.style.transformOrigin = pair[1];
      J[pair[0]] = el;
    });
    var prevWalker = h1.querySelector('.kiki-walker');
    if (prevWalker) prevWalker.remove();
    var prevRopes = h1.querySelector('.kw-ropes');
    if (prevRopes) prevRopes.remove();
    h1.appendChild(ropes);
    h1.appendChild(walker);

    function rot(name, deg) {
      var el = J[name];
      if (el) el.style.transform = 'rotate(' + deg.toFixed(1) + 'deg)';
    }
    function poseAll(mode, ph, p) {
      var s = Math.sin(ph), c = Math.cos(ph);
      if (mode === 'walk') {
        // 自然的走：小步幅、后腿屈膝抬起，手臂小幅反相
        rot('legL', 17 * s); rot('kneeL', -10 - 26 * Math.max(0, c));
        rot('legR', -17 * s); rot('kneeR', -10 - 26 * Math.max(0, -c));
        rot('armL', -13 * s - 3); rot('elbL', 14 + 8 * s);
        rot('armR', 13 * s - 3); rot('elbR', 14 - 8 * s);
      } else if (mode === 'hop') {
        rot('legL', -22); rot('kneeL', 52);
        rot('legR', -6); rot('kneeR', 34);
        rot('armL', -52); rot('elbL', 26);
        rot('armR', 52); rot('elbR', 26);
      } else if (mode === 'climb') {
        // 手换手：一只手抓住、另一只手向上摸，身体随之微微侧摆
        var a1 = Math.sin(p), a2 = Math.sin(p + Math.PI);
        rot('armL', 156 + 26 * a1); rot('elbL', 14 + 22 * Math.max(0, -a1));
        rot('armR', -156 - 26 * a2); rot('elbR', -14 - 22 * Math.max(0, -a2));
        rot('legL', 12 + 16 * Math.sin(p * 0.5)); rot('kneeL', 24 + 16 * Math.sin(p * 0.5 + 1));
        rot('legR', -6 + 16 * Math.sin(p * 0.5 + 2)); rot('kneeR', 28 + 16 * Math.sin(p * 0.5));
        rot('torso', 3 * Math.sin(p));
      } else {   // hang：单手扒住，另一只手垂着
        var h1p = Math.sin(p);
        rot('armL', 162 + 10 * h1p); rot('elbL', 12);
        rot('armR', -140 - 14 * h1p); rot('elbR', -14);
        rot('legL', 10 + 12 * Math.sin(p * 0.6)); rot('kneeL', 20 + 12 * Math.sin(p * 0.6 + 1));
        rot('legR', -8 + 12 * Math.sin(p * 0.6 + 2)); rot('kneeR', 22 + 12 * Math.sin(p * 0.6));
        rot('torso', -3 + 3 * h1p);
      }
    }

    // 悬崖绳：每道缝一根，两端挂在两个字的下沿，中间往下垂
    var hy = [], ropes2 = [], i5;
    for (i5 = 0; i5 < merged.length - 1; i5++) {
      var a = merged[i5], b2 = merged[i5 + 1];
      // 绳头要落在有墨迹的列上（缝隙两侧各留半像素，往里找几列）
      var ax = a.x1 + 0.4, bx = b2.x0 - 0.4, j5;
      var ay = -1, by = -1;
      for (j5 = 0; j5 < 5; j5++) {
        var qa = Math.round(ax - j5);
        if (qa >= 0 && bot[qa] >= 0) { ay = bot[qa]; ax = qa + 0.4; break; }
      }
      for (j5 = 0; j5 < 5; j5++) {
        var qb = Math.round(bx + j5);
        if (qb < W && bot[qb] >= 0) { by = bot[qb]; bx = qb - 0.4; break; }
      }
      if (!(ay >= 0) || !(by >= 0)) continue;
      var gapw = Math.max(4, bx - ax);
      var sag = Math.min(SH * 0.85, SH * 0.28 + gapw * 0.5);
      var rp = { ax: ax, ay: ay, bx: bx, by: by, my: Math.max(ay, by) + sag };
      ropes2.push(rp);
      var pth = document.createElementNS(ns, 'path');
      pth.setAttribute('class', 'kw-rope-gap');
      pth.setAttribute('d', 'M' + ax.toFixed(1) + ' ' + ay.toFixed(1) +
        ' Q' + ' ' + ((ax + bx) / 2).toFixed(1) + ' ' + rp.my.toFixed(1) +
        ' ' + bx.toFixed(1) + ' ' + by.toFixed(1));
      ropes.appendChild(pth);
    }

    // (6) 位移
    var SPEED = F * 1.15, HOPX = F * 1.45, CRAWL = F * 1.80, LOWER = F * 1.10;
    var st = { mode: 'walk', i: 0, x: merged[0].x0 + 1, y: ts[merged[0].x0 + 1] || 0,
               ph: 0, dist: 0, t: 0, dir: 1, rot: 0,
               hp: 0, hd: 0, hx0: 0, hx1: 0, hy0: 0, hy1: 0, hh: 0,
               vp: 0, vd: 0, vy0: 0, vy1: 0, vx: 0 };
    var alive = true, lastT = 0, land = -9;

    function groundAt(px) {
      var i1 = Math.floor(px);
      if (i1 < 0) i1 = 0;
      if (i1 >= W - 1) return ts[W - 1];
      return ts[i1] * (1 - (px - i1)) + ts[i1 + 1] * (px - i1);
    }
    function bottomAt(px) {
      var i1 = Math.floor(px);
      if (i1 < 0) i1 = 0;
      if (i1 >= W - 1) return bot[W - 1];
      var b0 = bot[i1], b1 = bot[i1 + 1];
      if (b0 < 0) b0 = b1;
      if (b1 < 0) b1 = b0;
      return b0 * (1 - (px - i1)) + b1 * (px - i1);
    }
    // 回程时手要抓的那条线：缝里走绳（贝塞尔），字底走字的下沿
    function lineY(px) {
      for (var i6 = 0; i6 < ropes2.length; i6++) {
        var r2 = ropes2[i6];
        if (px < r2.ax || px > r2.bx) continue;
        var u = (px - r2.ax) / (r2.bx - r2.ax), v = 1 - u;
        return v * v * r2.ay + 2 * v * u * r2.my + u * u * r2.by;
      }
      var bb = bottomAt(px);
      return bb >= 0 ? bb : 0;
    }
    function shakeDot() {
      for (var i2 = 0; i2 < dots.length; i2++) {
        if (st.x < dots[i2].x0 - SH * 0.6 || st.x > dots[i2].x1 + SH * 0.6) continue;
        var sp2 = dots[i2].span;
        if (!sp2) continue;
        sp2.classList.remove('kiki-dot-hit');
        void sp2.offsetWidth;
        sp2.classList.add('kiki-dot-hit');
      }
    }
    function hopTo(x0, y0, x1, y1, lift) {
      st.mode = 'hop'; st.hp = 0;
      st.hd = Math.min(0.62, Math.max(0.24, Math.abs(x1 - x0) / HOPX));
      st.hx0 = x0; st.hx1 = x1; st.hy0 = y0; st.hy1 = y1;
      st.hh = lift;
      st.dir = x1 >= x0 ? 1 : -1;
    }
    // 垂直升降（贴字边爬）：from y0 to y1 at fixed x
    function vertTo(x0, y0, y1, after) {
      st.mode = 'vert'; st.vp = 0; st.vx = x0;
      st.vy0 = y0; st.vy1 = y1;
      st.vd = Math.min(1.2, Math.max(0.26, Math.abs(y1 - y0) / LOWER));
      st.vafter = after;
    }

    function step(dt) {
      st.t += dt;
      if (st.mode === 'walk') {
        var r = merged[st.i];
        var dx = SPEED * dt;
        st.x += dx; st.dist += dx;
        st.ph = st.dist / (SH * 0.62) * Math.PI;
        poseAll('walk', st.ph, 0);
        if (st.x >= r.x1) { st.x = r.x1; arrive(); }
        else {
          var gy = groundAt(st.x);
          if (gy >= 0) st.y += (gy - st.y) * Math.min(1, dt * 10);
        }
      } else if (st.mode === 'hop') {
        st.hp += dt;
        var s = Math.min(1, st.hp / st.hd);
        poseAll('hop', 0, 0);
        st.x = st.hx0 + (st.hx1 - st.hx0) * s;
        st.y = st.hy0 + (st.hy1 - st.hy0) * s - st.hh * 4 * s * (1 - s);
        st.rot = st.dir * Math.sin(Math.PI * s) * 7;
        if (s >= 1) {
          st.y = st.hy1; st.rot = 0;
          st.mode = 'walk'; st.ph = 0; st.dist = 0;
          st.i = Math.min(merged.length - 1, st.i + 1);
          land = st.t; shakeDot();
          // 落在间隔点上（很短的一段）：不做走，直接再跳一下
          var rr = merged[st.i];
          if (st.i < merged.length - 1 && rr && rr.x1 - rr.x0 < SH * 0.85) arrive();
        }
      } else if (st.mode === 'vert') {
        st.vp += dt;
        var q = Math.min(1, st.vp / st.vd);
        st.x = st.vx;
        st.y = st.vy0 + (st.vy1 - st.vy0) * q;
        st.ph = q * st.vd * 7;
        poseAll('climb', st.ph, 1);
        st.rot = 0;
        if (q >= 1) {
          if (st.vafter === 'crawl') {
            st.mode = 'crawl'; st.dir = -1; st.dist = 0;
          } else {
            st.mode = 'walk'; st.ph = 0; st.dist = 0; st.i = 0;
            st.dir = 1; st.y = ts[Math.round(st.x)] || st.y;
            land = st.t; shakeDot();
          }
        }
      } else if (st.mode === 'crawl') {
        // 手换手往左爬：缝里抓着绳，字底抓着字沿
        var mv = CRAWL * dt;
        st.x -= mv; st.dist += mv;
        st.ph = st.dist / (SH * 0.55) * Math.PI;
        var ly = lineY(st.x);
        st.y = ly + SH * 0.96;
        st.dir = -1;
        poseAll('climb', st.ph, 1);
        st.rot = -3 * Math.sin(st.ph);
        if (st.x <= merged[0].x0 + 1) {
          st.x = merged[0].x0 + 1;
          vertTo(st.x, st.y, (ts[Math.round(st.x)] || st.y), 'walk');
        }
      }
    }

    function arrive() {
      var r = merged[st.i], next = merged[st.i + 1];
      if (!next) {                                   // 右端：贴字边爬下去
        vertTo(st.x, st.y, bottomAt(r.x1) + SH * 0.96, 'crawl');
        return;
      }
      var curY = ts[Math.round(r.x1)], nextY = ts[Math.round(next.x0)];
      var gap = Math.max(2, next.x0 - r.x1);
      if (gap <= 7 && Math.abs(nextY - curY) <= 4) {
        hopTo(st.x, st.y, next.x0 + 1, nextY, Math.max(SH * 0.16, gap * 0.45));
      } else {
        // 字间空隙：跳过去（不架桥）
        var lift = Math.max(SH * 0.34, gap * 0.5);
        hopTo(st.x, curY, next.x0 + 1, nextY, lift);
      }
    }

    function frame(now) {
      requestAnimationFrame(frame);
      var dt = lastT ? Math.min(0.05, (now - lastT) / 1000) : 0.016;
      lastT = now;
      if (!alive) return;
      step(dt);
      var sx = st.dir < 0 ? -1 : 1;
      walker.style.transform = 'translate(' + (st.x - SW / 2).toFixed(2) + 'px,' +
        (st.y - SH).toFixed(2) + 'px) scaleX(' + sx + ')';
      pup.style.transformOrigin = '50% 100%';
      pup.style.transform = st.rot ? 'rotate(' + (st.rot * sx).toFixed(2) + 'deg)' : '';
      var since = st.t - land;
      if (since >= 0 && since < 0.22) {
        var wq = since / 0.22;
        pup.style.scale = (1 + 0.10 * Math.sin(Math.PI * wq)) + ' ' + (1 - 0.16 * Math.sin(Math.PI * wq));
      } else pup.style.scale = '';
    }
    requestAnimationFrame(frame);


    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { alive = es[0].isIntersecting; }, { threshold: 0.15 }).observe(h1);
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
    """把报头资源（字体子集 + 葫芦娃精灵帧）从 scripts/ 复制到 docs/。

    放在 scripts/ 而不是 docs/，是因为 **往 main 的 docs/** 推任何文件都会触发
    deploy-docs.yml，把 main 上那份过期的 docs 全量发布到 gh-pages，覆盖掉当天的新页面
    （2026-11-22 就是这么被覆盖成 11-18 的）。让 polish 在运行时自己复制，
    Actions 的工作区里就自动有这些文件，主仓 docs 永远不需要动。
    """
    root = Path(__file__).parent
    dst_dir = Path(target_dir or "docs/fonts")
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        src = root / "kiki-head-700.woff2"
        if src.exists():
            dst = dst_dir / src.name
            if (not dst.exists()) or dst.stat().st_size != src.stat().st_size:
                dst.write_bytes(src.read_bytes())
        # 精灵帧 → docs/head/
        head_src = root / "head"
        if head_src.is_dir():
            head_dst = dst_dir.parent / "head"
            head_dst.mkdir(parents=True, exist_ok=True)
            for png in head_src.glob("*.png"):
                if png.name.startswith("_"):
                    continue
                dst = head_dst / png.name
                if (not dst.exists()) or dst.stat().st_size != png.stat().st_size:
                    dst.write_bytes(png.read_bytes())
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

