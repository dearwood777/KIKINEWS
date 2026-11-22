# 报头小人 · 实现说明与踩坑记录

> 这份文件是给"以后还要改这个报头小人"的人（包括我自己）看的。
> 只写两类东西：**为什么这么做**（避免走回头路），**怎么验**（避免再让用户替我们发现 bug）。
> 代码在 `scripts/web_polish.py`，替换区间是 `  // 3d) 报头小人` → `  function start() {`。

---

## 一、它到底是什么

- 报头 `科技 · 财经 · 国际速递` 里那个踩在字顶上走的小人。
- **不用 three.js、不用骨架动画、不做 3D**。曾经试过 three.js、位图静帧、自绘色块、手绘骨架、
  切件绕髋摆腿、程序化细线腿，全部被否（原因见第三节）。
- 现在有三套素材，按动作切换：
  1. **剪纸版**（矢量、样式化的葫芦娃）：站立、跳跃、底部横爬用。
  2. **走路雪碧图**（`docs/walk-sheet.png`）：`walk` 专用，7 帧 × 75×90（原 150×180，后来减半）。
  3. **爬墙雪碧图**（`docs/climb-sheet.png`）：`vert` 专用，4 帧 × 150×220。
     四帧是"右膝抬 / 双腿收 / 左膝抬 / 双腿收换手"的循环，姿态是**手在身前胸前、背弓、面朝字**
     （参照 FC《忍者龙剑传》爬墙）——**双手上举抓横杆那套已经被用户否掉，别再拿回来**。
- 地形不是贴图，是**真字形**：把 10 个汉字 + 空格用隐藏 canvas 以 2× 超采样栅格化，
  逐列取"墨迹上沿"，得到一条 `ts[]` 高度表；小人就在这条线上走。
  字体用子集化的 `docs/fonts/kiki-head-700.woff2`，字形路径表在 `scripts/head_glyphs.json`
  （`upm=1000, ascent=1160, descent=-288`），运行时注入 `window.KIKI_G`。
- 坐标：`.kiki-walker` 是 `position:fixed` 挂在 `body` 上（**不在 h1 里**），
  位置 = `h1 的视口矩形 + 局部地形坐标`。滚动/缩放时跟着走。

## 二、必须守住的三条铁律（都是血泪换的）

1. **脚位只能有一套数**。任何"图自己量出来的高度/包围盒"都不许再参与定脚位。
   现在是：`cellH = PH`、框 `top = 0`、图 `bottom: 0`、脚底 = walker 底边 = 地形线。
2. **不许反复重建**。构建入口有签名 `sig`（`W|F|LH|字数|字体是否就绪`）挡重复构建，
   而且判断"已经建过"要查 `document.querySelector('.kiki-walker')`（**不是 `h1.querySelector`**，
   小人已经搬出 h1 了）。每次构建发一个代号 `window.__kwGen`，旧 rAF 循环发现代号不对就安静退出。
3. **先验后交**。改完必须自己做像素级/几何级校验（第四节的三个手段），不许把"看着差不多"交给用户。

## 三、踩过的坑（按"真凶"排序）

1. **重建死循环 → "静帧平移 + 突然沉下去"**
   v13 把小人搬到 body 后，防重建的 guard 还在 `h1.querySelector('.kiki-walker')`，永远 null，
   于是每次调用都整段重建：剪纸版先占位（腿是死的，人还在往前滑）→ 雪碧图解码完切过去（位置错，沉下去）。
   用户的原话帮我们锁定："沉下去的同时腿才开始动"——同时发生，说明是"换了一套显示"。

2. **`getBBox()` 定脚位 → 桌面对、真机沉**
   `footY = (bb.y + bb.height)*U` 一旦某家 WebView 的 bbox 多算（clipPath 外、描边等），
   脚底线就整体下移。同一份代码两台设备两个结果，最难查。

3. **`<img>` 的行内基线 + `overflow:hidden` → "站着对、一走腿被切一半"**
   图默认是 inline，坐在文字基线上，下面留下行空隙；框高正好等于图高又带裁切，
   各家默认字号/行高不同 → 图被顶下去、框底把小腿裁掉。站着那套是 SVG（`overflow:visible`），
   完全不裁，所以看不出来。**修法**：图 `position:absolute; bottom:0; display:block`，
   框加 `contain:paint`，再加运行时自校准 `sprCalibrate()`（量 `图底 - 框底`，差多少补多少）。

4. **SVG `<image>` + data URI 内联 → 安卓 WebView 整块不出图（只有几个点）**
   千万别再往 SVG 里塞 base64 图。

5. **`ctx.measureText` 量基线 → 安卓上返回回退字体度量**
   基线一律用字体表 `KIKI_G.ascent/descent` + 每个字自己 span 的矩形反算，不用 measureText。

6. **切件绕髋摆腿走不出交叉步（几何死因）**
   原图两脚岔开 29.4 unit、整条腿只有 23 unit 高，绕髋旋转的横向行程上限 < 原有开度，
   数学上不可能交叉。`check_cross.py` 逐相位验证过。**别再试**。

7. **首开自动带参重载 → 多一次整页闪、导航等不到 load**。已撤，别再加。

8. **`elementFromPoint` 不能判断层叠**：`.kiki-walker` 有 `pointer-events:none`，永远探到下层元素。

9. **AI 出的动作帧，头身比和剪纸版不一样（0.38 vs 0.21）**
   按"头宽对齐"归一，人物会缩到 55% 高，一换动作就"人变小了"。**按身高归一**（角色 = walk-sheet 同高），
   唯一代价是头略大；换来的是切换素材时不跳尺寸。别反过来。

10. **`alpha.getbbox()` 会把极淡边缘算进包围盒**
    抗锯齿那圈 alpha=1..30 也被算成内容 → 裁剪框底下多出几十行空像素 → 底对齐后**脚离格底 26px**，
    又变成"悬空/沉字"。取 bbox 一律先 `alpha.point(lambda v: 255 if v>30 else 0)` 再 `getbbox()`。

11. **让 AI 画"贴墙"动作，它会把墙和投影一起画进来**
    墙线、剪纸投影的灰斜线会跟人物连成一片，抠图时一起进来，帧边上多出一条灰线。
    提示词写死"纯白画布、不画墙、不画投影"；万一还是带进来，按"中亮度 + 低彩度"过滤一次。

## 四、怎么验（每次都做，别跳）

1. **DOM 真值**（最可靠）：量 `spr`/`box` 的 `getBoundingClientRect()` 与字形墨迹上沿对比。
   合格线：`|脚底 - 墨迹上沿| < 1px`（目前 0.63px）。
   顺手再看：`img.bottom == box.bottom`（自校准生效）、`img naturalWidth` 对不对、`display` 状态。
2. **逐帧在动**：连续读 `img.style.transform`，应该看到 `translateX(0 → -115.6 → -92.5 …)` 这种跳变。
   不变 = 又变成静帧了。
3. **真的看画面**：本机 Edge headless 截图（**ego 的 `page.screenshot()` 必超时，别用**）：
   ```
   msedge --headless=new --disable-gpu --hide-scrollbars --no-first-run \
     --user-data-dir=<临时目录> --force-device-scale-factor=2 \
     --window-size=390,844 --screenshot=<out.png> --virtual-time-budget=4000 <url>
   ```
   然后用 PIL 裁剪放大、`Read` 看。注意：**虚拟时间下 rAF 会被冻住**，同一张图里位置不动是正常的，
   它只用来验"这一帧长什么样、脚踩在哪"，不验流畅度。
   另：多个截图任务要各用独立的 `--user-data-dir`，否则 Edge 单例会复用窗口尺寸。
4. **临时演示页**：需要把小人直接丢到某一段（垂直、跳跃）验帧时，往页面副本里插一段
   `setInterval` 调 `window.__kwdbg.vertTo(...)`；正式页面里 `?kwdbg=1` 会挂调试钩子
   （`__kwdbg = {st, ts, W, PH, vertTo, hopTo}`），不带参数时完全不挂，**验完把副本删掉，别推上线**。

## 五、动作分段（现在的状态机）

`walk`（雪碧图逐帧，脚落点驱动）→ `hop`（跨字缝隙，剪纸腿）→
`vert`（贴字边上下，**攀爬版**：双手交替抓、双腿交替蹬，相位跟垂直位移走）→
`crawl`（沿字下方横爬，正面攀爬图镜像）。

- 空隙一律"跳"，不踩线；间隔点 `·` 落在点心。
- `vert` 用**爬墙雪碧图 4 帧**（`CF`）：`frameIdx = floor(t*10) % 4`，`t = q*vd`；
  框 `cellH = PH*220/180`、`top = PH - cellH`，所以**框底 = 脚底 = 地形线**，换素材不沉字。
  镜像用**翻整框** `scaleX(-1)`（翻图会让 `translateX` 帧序错位）；朝向按 `st.x > W*0.5` 判断
  ——在字右侧往下时脸朝字（往左）。图没解码完时退回剪纸版 `PHp` 撑住。
- 走路爽感 = 帧 + 位移对齐：`cyc = 2*(PH*0.54)/SPEED`，帧占时 `WFw=[1.12,1,0.9,1.06,1.12,1,0.9]`。

## 六、素材从哪来

- 形象：用户 1280×1280 三姿态原图（`scripts/head/_sheet.png`）→ `prepare_art.py` 切侧身/攀爬 + 去白底
  → `gen_art3.py` 11 色最近色矢量化 → 按解剖切件 + `clipPath` + `<use>`。
- 爬墙帧：`image_edit`（seedream_5.5）**拿 walk-sheet 的一帧当参考图**，要求"同一角色 / 同一画风 /
  同一头身比、纯白画布、不要画墙与投影"，出 4 个爬墙姿态 → 去白底（边界 flood fill）→ 去掉剪纸投影的
  灰线（`118 ≤ 亮度 ≤ 212 且彩度 < 22` 的像素不算人）→ 只留最大连通块 → **按身高归一到 180 图像像素**
  （不要按头宽：AI 头身比 0.38 vs 剪纸 0.21，按头宽会缩成 55%）→ 底对齐 + 头顶最宽段中点水平对齐。
  生成器：`C:\Users\User\AppData\Local\Temp\make_climb_sheet7.py`。
- 走路帧：`image_edit`（seedream_5.5）按 4 个关键姿势出 7 张迈步图 →
  按头高归一化（`TARGET_HEAD=68`）→ 纵向拉伸到 `CELL_H=180` → 拼条 → 再减半到 525×90。
  生成器：`C:\Users\User\AppData\Local\Temp\make_walk_sheet2.py`。
- 引用带 `?v=` 版本号，换图必须 bump，否则 CDN/WebView 缓存咬人。

## 七、发布纪律

- 改 `scripts/web_polish.py` 后：`python scripts/web_polish.py docs/latest.html docs/latest-en.html docs/vocab.html`
  → `python %TEMP%\jscheck.py`（输出 `0` 才算语法过）。
- **main 和 gh-pages 都要推**：每天 06:18 的 digest 用 main 上的脚本重刷三页；
  `deploy-docs.yml` 已改成只手动触发，别再把 main 的 docs 往 gh-pages 覆盖。
- 绝不再往 main/docs 推文件（历史事故）。
