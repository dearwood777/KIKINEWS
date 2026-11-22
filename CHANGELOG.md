# 更新记录

## 报头小人 v5：直接矢量化原版参考图做剪纸（形象、步态、攀爬一次全改）（2026-11-22）

v4 的关节骨架动作逻辑是对的，但**造型被彻底否掉**（"完全不是葫芦娃"）。v5 换路线：**不再手绘造型，而是把用户给的原版葫芦娃参考图自动矢量化，按人体解剖切成可旋转的剪纸部件**。

**矢量化管线**（`prepare_art.py` + `gen_art3.py`）：
- 从 `scripts/head/_sheet.png`（1280×1280，三个姿态）按列区间切出侧身走姿与双手抓杆攀爬姿态。
- **只从四角泛洪吃纸白**（阈值 `min>236`）：这一步是关键，早先"行内纯白全转透明"把白裤腰上的纯白一起铲了，裤子只剩灰阴影 → 渲染出来是**一片黑斑**（brown-black speckles，改了三次才定位）。
- 分色用**固定 11 色最近色分类**（黑/皮肤/白/草绿/红/棕/灰绿/浅灰/暗红/眼绿/腮红），而非 kmeans（kmeans 会把白裤糊成黑块）；再加 `lum>176 & sat<30 → 白` 把裤子阴影吸回白色。
- `findContours(RETR_CCOMP)`，**每个外轮廓单独成一条 path，洞跟着自己的父轮廓一起 evenodd**；排序时**黑色（描边）永远先画**，其他色再盖上去——这样即使某块描边的洞没被识别出来，实心黑也会被内部的颜色重新覆盖，不会整块变黑。
- 攀爬图先按色抠掉横杆，再泛洪；顶部被双手+横杆围死的背景泛洪进不去，额外把上部 28% 的近白（`min>190`）清掉，双手因为是肤色不会被误伤。

**切件**：`<defs><g id="a-walk"/"a-hang">` 各一份完整矢量图，每个部件 `g.p-{art}-{part`} + `clip-path` 裁自己那一块 + `<use>` 复用同一份图形；枢轴放在关节位置（`transform-origin` + `transform-box:view-box`）。侧身图 5 件（`legB/legF/body/armB/head`），攀爬图 6 件（`legL/legR/body/armL/armR/head`），坐标统一缩到 **100 单位高**（`wS=52.8 / wH=85.7`）。

**步态**：只转部件、整图不转，所以不会"后仰/正步"。`legF/legB` 反相 ±11°、`body` 起伏 `|cos|*0.9` + 1.2° 轻摆、`armB` ±15° 反相、`head` -0.9° 跟随。走速 `F*0.82`。

**攀爬**：`armL/armR` 反相 ±13°（一手抓牢一手往上摸）、`legL/legR` 反相 9° 交替蹬、`body` 2.2° 侧摆、`head` 跟随 —— 四肢全动，不再是"只有手在动"。走 `poseClimb`，垂直吊着用 `poseHang`。

**路线与转身**：`walk` 全程正向，**走到最右端（"递"字末）才 `vert` 吊下去**，不再在"速"字处提前转身倒走；`crawl` 用正面朝外的攀爬图、不镜像；到最左端 `vert` 爬回字上沿继续走。整圈 ≈26s。

**线**：只保留 2 根，跨"技↔财"、"经↔国"这种**含间隔点的大空隙**，两端**挂在两个字的字底下沿**（`bot[]`），中间下垂 `sag=min(PH*0.34, PH*0.14 + w*0.1)`，`stroke .75 / opacity .55`（v4 的 1.1 还被嫌粗）。空隙一律"跳"，线只做回程抓手。

**踩坑记录（给下一个 AI）**：
- `web_polish.py` 里的注入脚本是**普通 Python 字符串**，往里塞 JSON 时 `\"` 会被 Python 解析掉，页面直接 SyntaxError（整段脚本不执行，`window.KIKI_G` 都变 undefined）。**改用单引号包 SVG 并转义 `\` 和 `'`**。
- 白底转透明**必须用"从四角泛洪"**，任何"全局近白→透明"都会吃掉白裤/白衣的纯白区域。
- 一件多色矢量图里，**描边色要先画**，否则丢洞时整块变黑。
- 部件裁剪框别用固定像素，参考图尺寸会变；攀爬图用比例框（`fx/fy`）更稳。
- `ego` 里 rAF 被节流，看位移速度不能当真；要验路线就临时挂 `window.__kwdbg = {step,st,...}` 手动 `step(1/60)` 推演（推完记得删钩子）。
- 两套剪纸共用一个 DOM 舞台，**建完必须显式 `display` 初始化**（`setArt(false)` 首帧会因 `useHang===false` 直接 return，导致两张图叠一起）。

## 报头小人 v4：照参考图重画葫芦娃 + 空隙改"跳" + 字底悬崖绳（2026-11-22）

v3 的骨架方向对了，但造型和路线都被打回，这一版是重写：

**造型照参考图重画**（不再是我自己捏的色块）：黑短发+刘海三缕+两鬓小尖、大绿瞳（带高光和眉毛）、腮红、红坎肩敞开露胸、脖子上一圈小绿叶、棕腰带 + 三片草叶短裙、白短裤、细胳膊细腿（原来 8.8 宽的胳膊收到 4.4，腿收到 4.8）、光脚、头顶小葫芦+两片叶+红珠。还是 8 个关节的分组骨架，脚底对齐 `y≈99`，所以缩放后正好踩在字上。

**空隙的处理改回来了**：v3 我把 `·` 两侧的缝架成"绳桥"踩着走过去——这是错的，那根线不是给人走的。现在 **缝合处一律跳**（`hop`：抛物线 + 收腿 + 双臂后摆），落在间隔点 `·` 上不做走（`rr.width < SH*0.85` 直接 `arrive()` 再跳一次），于是是"跳上点、再跳上字"的节奏。

**悬崖绳改成"往字底下垂"**：每道缝一根浅棕细绳（`kw-rope-gap`，`stroke 1.1 / opacity .68`），**两端挂在两个字的下沿**（沿列往内找 5 列取有效墨迹，避免取到空白列得 -1），中间往下垂 `sag = min(0.85*SH, 0.28*SH + 0.5*gap)`。间隔点 `·` 本身比字底高，所以绳的末端是"吊到点上"的，正是要的两截线。原来那条横贯全宽的回程长绳删掉了。

**回程改成"字底下攀爬"**：`walk → hop… → 最右端 vert 垂直贴边爬下去 → crawl 手换手横向往左爬（缝里抓着绳、字与字之间抓着字的下沿，身子吊在线下面 SH*0.96）→ 最左端 vert 爬回字上沿 → walk`。不再有整条底线，也不再出现"背对行进方向"——`crawl` 期间 `dir=-1` 统一镜像，头朝左、朝行进方向。

**手换手**：`climb` 姿势双臂举过头顶 `±156°`，左右手反相各摆 26°（一手抓、一手往上摸），肘反过来 14~36° 跟着屈，配合躯干 3° 侧摆和双腿在下面交替蹬。

**步子改自然**：腿摆 ±26° → ±17°，膝盖改成"后腿抬起"（`-10 - 26*max(0,cos)`），手臂只小幅反相 ±13° 并带 3° 前倾，不再是走正步。

**速度**：走 `F*1.15`、跳 `F*1.45`、横向爬 `F*1.80`、垂直爬 `F*1.10`。整圈 ≈17.4s（走 8.9s / 跳 2.6s / 下去 1.1s / 横爬 6.1s / 上来 1.2s）。

**踩坑记录**：
- 绳头取样一定要往字里退几列：`a.x1+1` 已经是空白列，`bot` 为 -1，四条绳会全部 `continue`（我这次就踩了，绳层 children=0）。
- 别把空隙架成桥给人踩——线是给"回程攀爬"用的。
- 攀爬时手要 `±156°` 才算举过头顶，`±132°` 看着像在"欢呼"。
- 腿分段（白裤/小腿）要在 y 上重叠 1~2 单位，否则膝盖一转就露缝。

## 报头小人的 v3：位图帧 → SVG 关节骨架 + 崖间绳索（2026-11-22）

v2 上线后被验收打回，四条意见都指向同一个根因：**位图帧是"一张静止图在位移"**，再怎么换图也不会迈步。所以这次不再切图，改成**可驱动的关节骨架**。

**造型**：`60×100` viewBox 的 SVG，一块块拼出葫芦娃——红衣（渐变 `#ef5a4a→#cf3b2f`）、白裤、贴身绿叶裙、肤色手臂、黑发+两侧鬓角、头顶葫芦叶与红点、腮红。分组：`kw-legL/kneeL`、`kw-legR/kneeR`、`kw-armL/elbL`、`kw-armR/elbR`，每个关节 `transform-box:view-box` + 固定 `transform-origin`（腿根 `24,68`、膝 `24,86`、肩 `18.5,35`、肘 `15.5,49`，右肢 x 镜像），旋转就是真关节，不再是整图平移。

**四套姿势**（`poseAll`，参数按字号 F 缩放）：

| 姿势 | 用法 | 关节取值 |
|---|---|---|
| `walk` | 走字脊 | 腿 `±26°` 正弦反相、膝随 cos 一侧弯 14~32°、臂反相 `±18°`、肘随摆 12~22° |
| `bridge` | 踩绳过崖 | 双臂平举 `∓64°`（找平衡）、腿小幅交换 14°、膝微屈 |
| `rope` | 顺绳下 / 爬回 | 双手过顶 `±140°` 交替抓握、腿屈膝 42° 上下蹭 |
| `hang` | 挂绳荡回 | 双手 `±158°` 扒绳、腿自然下垂摆荡 |
| `hop` | 短缝平跳 | 收腿、双臂上举 |
| 落地 | 每次落地 | 0.22s 内 `scale` 1→`1.10/0.84`→1 的压扁回弹 |

**尺寸**：`SH = max(11, 点墨径 × 2.5)`，比 v2 的 ×2 大 1/4（30px 字号下 `18.8 × 11.3`），脚底贴在字形上沿。

**地形收窗口**：v2 用 ±3 列**最高**墨迹做包络，人物常比字边高出一大块、看着悬空。现在只在 `x±1` 取墨迹高度、再 ±2 列滑动平均，脚底压着字形上沿走（`ts/bot` 都插值）。

**方向**：`st.dir` 决定 `scaleX(-1)`。向右走 `+1`；回程长绳（从右往左荡）`-1`，人物**头朝行进方向**；绳索两端垂直位移时沿用上一段方向。

**崖间绳索**（用户点名要《天书奇谭》蛋生爬悬崖那种线）：五段可走字形之间有 4 条缝（16~20px），每条缝画一根二次贝塞尔**下垂绳**（`kw-rope-gap`，`stroke:#8b7f6b/.9/opacity .55`，sag `SH*0.2~0.7`），人从绳上"踩"过去（`bridge` 姿势），不再是硬跳。右端 `递` 之外没有下一段，于是**顺绳下到字底**（`down`）→ 挂上一条横贯全宽的**回程长绳**（`kw-rope-back`，淡入 0.3s）荡回左端（`back`）→ 在 `科` 左侧**垂直爬回字上沿**（`up`）→ 接着走。整圈 **≈12.7s**（走 8.4s + 四段绳桥 1.8s + 下 0.6s + 荡回 3.1s + 爬回 0.7s）。

**踩坑记录（留给下一个 AI）**：

- 位图帧永远做不出"迈步"，关节角度才是。
- `transform-box` 必须是 `view-box` 且 `transform-origin` 写 `px` 数值；`fill-box` 会让旋转中心跑到每个子路径的包围盒，看起来像骨折。
- 换姿势时只 `rot()` 已出现的关节，不要 `remove/re-add` 子节点，否则每帧重排、iOS WebView 掉帧。
- `intersection` 只是暂停推进，别拆 DOM，重进视口要接着原来的 `st`，不要从头再来。
- 绳桥别用 `poseAll('rope')`（双手过顶）——那是爬竖绳的姿势，横绳上要双臂平举。
- 回程长绳的 y 取 `bottomAt() + SH*1.35`，再往上贴近字底会穿字。

**代码位置**：`scripts/web_polish.py` 的 `buildWalker()`（唯一注入源，幂等；`h1.__kwSig` 签名防重建风暴）。cairosvg 本机缺 cairo，SVG 光栅化只能用浏览器 canvas `toDataURL`。

## 报头小人 v2：葫芦娃 + 走/跳/攀爬/悬挂荡回（2026-11-22）

**形象换了**：占位机器人 → **葫芦娃**（用户提供参考图，右侧那根攀爬横杆已用代码去掉）。四条精灵帧都从参考图切出来，脚本 `scripts/head/` 下：

| 文件 | 尺寸 | 用途 |
|---|---|---|
| `chw-walk1.png` | 52×68 | 行走第 1 帧 |
| `chw-walk1b.png` | 52×68 | 行走第 2 帧（walk1 水平镜像，左右脚互换） |
| `chw-walk2.png` | 43×68 | 空中 / 跳跃 |
| `chw-hang.png` | 52×68 | 攀爬 / 悬挂（双手扒上沿） |

切图要点：`flood_bg(thr=242)` 从四边泛洪只吃与边缘连通的白（人物内部的白裤子保住）；`kill_bar()` 按行统计"中性灰占比 >50%"定位横杆带，带内只保留肤色，杆体与描边抹掉、手指保留。显示尺寸仍按"间隔点直径 × 2"算（30px 字号下 15.3px 高、11.5px 宽）。

**运动从"自由物理"改成"脚本化 + 缓动"**。原版用重力 + 落地判定，在 7px 宽的间隔点上落点不可控，落到空处就继续掉、再撞上字边弹上来 —— 用户看到的就是"先掉下去又窜上来"和"歘一下"。现在：

| 模式 | 做法 | 参数（按字号 F 缩放） |
|---|---|---|
| `walk` | 匀速前进，脚随地形缓动跟随 | `SPEED = F*1.25`；跟随系数 `dt*9` |
| `hop` | 固定时长的抛物弧，起终点精确落在两段字形的上沿 | `HOPX = F*1.55`；时长 `clamp(gap/HOPX, 0.24, 0.62)`；抬升 `min(SH*0.45, gap*0.32)`，往下走再 ×0.55 |
| `slide` | 攀爬 / 下滑 / 爬回起点，统一"缓入缓出 + 直线位移" | `CLIMB = F*1.05`；时长 `max(dx,dy)/v`，`clamp(0.22, 1.4)` |
| `hang` | 手扒字的下沿，钟摆 `sin(t*2.2)*11°` 荡回左端 | `HANG = F*2.30`；y 限速 `SH*1.3/s`（下沿是笔画底边，太抖） |

**地形也重算了**：逐列只取单像素会掉进笔画缝隙（撇和竖之间只有 2~4px），曲线上下来回 10px 以上。现在先取 ±3 列的**最高墨迹**做包络、再做 ±2 列移动平均，`top`/`bot` 都这么处理；跟随时再在相邻两列之间做线性插值，1px 台阶没了。

**修掉的三条老毛病**：

1. 跳"歘一下"：原来 `y = top[round(x)]` 直接赋值 + 跳段时长被压到 120ms 下限 → 现在抛物线有完整上升—下落，加上落地压扁（0.88→1，200ms）和走路时前后倾 9°。
2. `际`/`速` 之间的洞"先掉再窜"：原来按"缝隙就跳"无条件用抛物线。现在按两段高差分流：更高的（`dy < -5`）**贴边爬**，更低的（`dy > 4`）抬升压一半做"跃出去往下落"，同高才平跳。
3. 到最右端停住重来：补了后半程 —— `descend`（滑到字的下沿）→ `hang`（挂着荡回左端，4.8s）→ `slide`（爬回第一段起点）→ 接回 `walk`。一整圈 15.97s。

**踩的坑（给下一个 AI）**：

- `splice_walker.py` 用 `src.index('// 3b)')` 找结束标记时，**3b 在 3d 之前**，`end < start` 导致整段被复制成两份（页面里两个 `buildWalker`、旧 SVG 小人还在跑）。教训：按标记切片前先断言 `end > start`。
- 重复重建：`document.fonts.ready`、resize 都会触发 `buildWalker`，每重建一次小人就从最左重走，看起来像"一直在重来"。现在加了 `h1.__kwSig`（W|F|LH|字数）做幂等，几何不变直接 return。
- 验证办法：浏览器 rAF 在这个环境被节流（实测 1.7~5fps，按 dt 累积算出来只有 2.5px/s），用它看动作会误判"太慢/一顿"。改成**在页面内以固定 1/60 步长同步推进**（`window.__kwstep(1/60)` 循环 60*20 次）来量整圈状态与单帧最大位移 —— 目前 `maxStep 1.98px`（< 2px 才算不"窜"）。调试钩子用完即删。
- 线上 `head/*.png` 一开始 404：Pages 构建是**三次独立提交**（三页 + 资源各一条 commit），构建需要等最后一次 commit 的 build 完成（`/pages/builds/latest` 看 status），CDN 还要几十秒；`?t=ts` 有时也逃不掉缓存，用 Cache-Control: no-cache 再取一次。

**现状**：`scripts/web_polish.py` 49.4KB，注入后 JS 26.0KB；gh-pages 三页 106904 / 103347 / 60073；`latest-en.html` 的标题是 `Tech · Finance · World`，字体子集与字形 JSON 只有中文 10 字，所以**英文页没有小人**（静默跳过，不报错）。要支持英文页得另打包一套拉丁字形。

## 修复：每日 digest 把线上特效覆盖掉（2026-11-22）

**现象**：11-22 早晨的新一期页面一上线，之前所有页面特效（水波纹 / 边缘流光 / 数字递增）全没了，等于恢复原样。

**根因**：`.github/workflows/horizon-daily.yml` 每天在 **main** 分支 checkout 后跑 `python scripts/web_polish.py` 再发布到 gh-pages。而所有特效改动只写进了本地 `scripts/web_polish.py`（24.0KB）和 gh-pages 的三页，**main 上的脚本一直是 13.7KB 的旧版，连流光那一段都没有**。于是每天早晨的重刷都会把三页重写成"没有流光"的版本，我们手工 push 的成果每天被清一次。

**修法**：
1. 把本地最新 `web_polish.py`（含恒速光束 / 尺寸自适应 / 接缝周期=周长 / 降速）推到 **main** → 以后每天 digest 用的就是新版（commit `05e4c019`）。
2. 拉取 11-22 期 gh-pages 三页，用新脚本重新注入后推回（`latest.html` 74588→84836、`latest-en.html` 71031→81279、`vocab.html` 35642→45891）。
3. 线上复验：三页均为 11-22 期，16 条正文 / 25 个词卡，`MIN_DUR = 6200` 命中；光束 `period == len`（2587.7 / 743.7 / 1747.7），圈时 16173 / 6200 / 10923ms。

**教训**：改 `web_polish.py` 后必须同时推 main 和 gh-pages。只推 gh-pages 的注入结果，第二天早晨必被覆盖。

## 事故二：deploy-docs 用 main 的过期 docs 覆盖了当日页面（2026-11-22）

**现象**：给报头加字体子集时，往 `main` 的 `docs/fonts/` 推了一个 2.6KB 的 woff2，几分钟后线上三页全部变回 **11-18 期**内容（16 条正文不变，但期号、词卡全退）。

**根因**：`deploy-docs.yml` 的触发条件是 `push: main + paths: docs/**…`，它做的事是把 **main 上的 docs/** 全量发布到 gh-pages。而每日 digest 是直接写 gh-pages 的，**main 的 docs 长期是一份过期快照**。所以任何一次 "往 main/docs 推文件" 都会把当天的新页面整体覆盖成旧快照。

**修法**：
1. `deploy-docs.yml` 改成**只保留 `workflow_dispatch`**（需要发布 main/docs 时手动 Run），push 不再触发（commit `02ec7551`）。
2. 报头字体从 `docs/fonts/` 挪到 `scripts/kiki-head-700.woff2`，由 `web_polish.py` 的 `ensure_font()` 在运行时复制进 `docs/fonts/` —— Actions 的工作区里自动有它，**主仓 docs 永远不需要动**。
3. 从历史提交 `a89b8d173`（11-22 期最后一版）取回三页，用最新脚本重新注入后推回：102230 / 98673 / 55397 字节，16 条正文、25 个词卡、日期 11-22。

## 报头小人（第一版：骨架 + 占位形象）（2026-11-22）

- 报头字体换成专门打包的子集 **KikiHead**（Noto Sans SC 700，只含"科技·财经国际速递"10 字 + 空格，**2.6KB**，OFL 可分发），`@font-face` 指向 `fonts/kiki-head-700.woff2`。换字体的唯一目的是：屏幕上渲染的字和隐藏层里的轮廓来自同一份数据，脚才踩得准。
- 字形轮廓由 `scripts/build_head_glyphs.py` 从 woff2 导出（`fontTools` + `SVGPathPen`）→ `scripts/head_glyphs.json`（**7.9KB**），注入页面为 `window.KIKI_G`。
- **地形不是手写坐标**：把整行字形以 2 倍超采样画进离屏 canvas，逐列扫描 alpha 取"最上面的墨迹"→ 得到一条真实的上沿曲线；连续墨迹列合并成"可走段"，段间空隙就是"跳"。所以换字号、换设备、横竖屏全自动贴合，不需要调像素。
- 基线用浏览器自己的度量算：`ctx.measureText().fontBoundingBoxAscent/Descent` + CSS 的 `line-height` 半行距，不硬编码 asc/desc。
- 尺寸：先量间隔点 `·` 的**真实墨迹直径**（当前 30px 字号下 7.67px），小人高度 = **直径 × 2**（15.33px），宽度 `0.7×高度`——用户指定的比例。
- 逐字拆 `span.kch`（`inline-block` + **`white-space:pre`**；少了 `pre` 只含空格的 span 会把空格折叠，整行从 331.45px 缩到 303px，字之间的间隙全没了）。
- 动作：走（两腿交替 `sin` 摆动、身体轻点头）→ 空隙抛物线跳（`sin(πu)` 抬到 0.5 倍身高）→ 落在 `·` 上时给该 span 加 `kiki-dot-hit`（300ms 压扁回弹）。一圈走完停 2.6s 重来；报头离开视野暂停。
- 现状：形象是**占位机器人**（`buildWalker()` 里的一段 SVG 字符串，换形象只改这段）。后半段（沿"际/速"下去 → 像长臂猿抓着上沿荡回来）还没做。

1. **`scripts/web_polish.py` 是唯一注入源**，页面里 `<!-- kiki-polish:start -->…end -->` 之间的东西全是它生成的，直接手改 HTML 会在下次注入时被覆盖。
2. **改脚本必须双推**：`main`（供每天 digest 用）+ `gh-pages`（供线上立即可见）。只推一边一定出问题——只推 gh-pages 第二天早晨被清，只推 main 要等下一期才生效。
3. **绝对不要往 main 的 `docs/**` 推任何文件**：会触发 `deploy-docs.yml`，把 main 上那份过期的 docs 全量发布到 gh-pages，直接覆盖当日页面（11-22 真被覆盖成 11-18）。需要放在页面目录的静态资源（如字体），放 `scripts/`，由 `web_polish.py` 运行时复制到 `docs/`。
3. **推送顺序**：先 `ghutil.raw()` 拉远端最新 → `web_polish.polish()` → 再 PUT。反过来会拿本地旧页面覆盖当天新内容（11-22 就踩过一次）。每天 **06:18 左右** digest 会整体重写三页，cd 到那个时间窗口之后要重刷。
4. **环境**：Windows + pwsh 7，**没有 Bash、没有 git 命令**（本机 git 不在 PATH），一切走 GitHub Contents API（`C:\Users\User\AppData\Local\Temp\ghutil.py`）。`python -c "..."` 带引号/正则会被 PowerShell 解析坏，**一律写临时 .py 再执行**。
5. **验证用 ego lite**：能 `goto`/`evaluate`/CDP 改视口，但 `page.screenshot`、`Page.captureScreenshot`、`Page.printToPDF` **全部 15s 超时**，要看形态只能用 canvas 按 `Path2D + setLineDash` 复刻 SVG 再 `toDataURL`。
6. **rAF 在页面不可见时被节流**：计数/动画类效果必须加"兜底直接写最终值"，否则后台标签页回来会卡在 0。
7. **跨文档带 `#` 落地**：浏览器原生锚点滚动会被 `scroll-behavior:smooth` + View Transition 打断并退回顶部 → 用 `hardLand()` 临时 `scroll-behavior:auto` 硬跳，再按 `scroll-margin-top` 校一次。
8. **数字递增**：数字必须在 `DOMContentLoaded` 就把值折进定宽 `span`（`tabular-nums` + `min-width`），等动画开始才插会让胶囊每次变宽跳一下。
9. **边缘流光**：虚线周期必须 **= 整圈周长**（`dash + gap = len`），否则转角处会断光；时长用 `周长 / 线速度` 算，**不要写固定 ms**（否则平板快手机慢）；容器尺寸变化必须删旧 SVG 整块重画（`ResizeObserver` + `orientationchange`）。
10. **已判死的路，别再试**：`offset-path: path()`（安卓 WebView 整条渲染不出来）、`conic-gradient` 旋转（椭圆上速度严重不均）、线性渐变横扫（变成上下两束光）、独立大白头（蝌蚪感、尾巴瞬间变细）、`box-shadow` spread 波纹（两条粗线）、`outline` 串行圈（不是同时荡）。


## 卡片涟漪定版 + 边缘流光 / 数字递增 / 错峰淡入 (2026-11-21)

**一、卡片水波纹定版参数（用户验收通过，改这块先看这张表）**

| 项 | 取值 | 说明 |
| --- | --- | --- |
| 环数 | 3 | 和发音键同一套算法：多圈同时在荡，不是一条消失再来一条 |
| 起跑延迟 | `0 / 320 / 640 ms` | 320ms 是肉眼能看出“先后”的最小间隔；想更散就加，想更密就减 |
| 单圈时长 | `2050 / 1850 / 1680 ms` | 递减是为了让三圈终点几乎重合（2050 / 2170 / 2320ms），一起收在最外轮廓淡掉 |
| 扩散曲线 | `cubic-bezier(.3,.4,.4,1)` | 近匀速，早期不再“唰”地弹到边 |
| 透明度 | 0% `.82` → 55% `.42` → 100% `0` | |
| 线宽 | `1px` | 已是 CSS 亚像素极限，再细会被安卓屏抹掉或糊成灰 |
| 外扩量 | 每边 `9px`（`--kx/--ky` 按宽高算） | 必须小于卡片间距 10px，否则压进邻居卡片 |
| 承载位置 | 卡片外面（`.cards` 容器内，绝对定位） | 卡片自身 `overflow:hidden`（左侧 3px 竖色条 `::before` 造成），环画在卡内必被裁 |
| 触发时机 | `IntersectionObserver` 进视野 / 目录跳转后 `scrollend` | 首屏已在画面里的卡不参与，避免“一进来就依次闪” |

发音键水波纹**不动**，仍为 2 圈 `0/140ms`、`860ms`、`scale .72→2.02`、1.5px —— 它是这套效果的参照基准。

**二、边缘流光（Border Beam，只做「从 71 条中筛出 / 展开全部 71 条」这个胶囊）**

- ①`conic-gradient` 旋转：**速度不均**（直边慢、冲过两端圆弧”唰”一下）。根因是胶囊为又扁又长的”体育场”形，锥形渐变转同一角度，落点在直边和圆弧上走的距离差好几倍，几何上不可能匀速。废弃。
- ②`offset-path` 沿路径（JS 生成体育场路径 + `offset-distance` 0→100%）：原理对，但**实机 WebView 里整条光渲染不出来，直接消失**。废弃。
- ③`padding-box` 遮罩 + 线性渐变横向位移：匀速了，但**上下两条边同时亮**，是"两束光并排走"，不是"一道光溜边"。废弃。
- ④定版：**SVG 描边 + `stroke-dashoffset`**。JS 按胶囊实际宽高（`offsetWidth/offsetHeight`）生成体育场路径（4 段直线 + 4 段 90° 圆弧，半径 = 高/2），`stroke-dashoffset` 0 → `-路径总长`（长度由 `getTotalLength()` 写进 `--len`），`6000ms linear infinite`。路径参数天生按弧长均匀，因此严格匀速。
- ⑤流星化：一条纯色线段太"干"。做法是叠 9 层 dash，每层 `animation-delay = -(dur*(len-behind)/len)` 让它落在亮头后面固定距离，宽度 **0.6 → 1.3px**、透明度 **.08 → .95** 逐层递增，尾巴拖到 138px，另加一层 blur 的头部外发光做光晕。**没有单独的大头**（试过 2.8px 纯白"白热头"，观感变蝌蚪、尾巴瞬间变细，已废弃）。
- ⑥尺寸按胶囊宽度自适应：`s = clamp(w/380, 1, 2.6)`，彗尾长度 ×s（横屏不再像个小点），粗细只放大 `s^0.55`（避免又变笨）。竖屏基准 ≈138px 尾长 / 1.3px 亮芯。
- ⑦速度恒定（跨设备一致）：不再固定 6000ms，而是 `duration = 路径周长 / 185 px·s⁻¹`（夹在 3.2–15s）。周长是手机 744 / 平板 1748 / 桌面 2588，对应 4020 / 9447 / 13988ms，**线速度都是 185px/s**。之前的固定时长正是"平板快、手机慢"的原因。
- ⑧旋转重建：`ResizeObserver` 盯住 `.cbtn` + `resize` / `orientationchange`，尺寸一变就整块重画 SVG（`getTotalLength` 与每层 delay 全部重算），否则光会沿旧的竖屏短路径跑。
- ⑨接缝不断光：虚线周期原来是 `dash 9999`（gap 远大于周长），光跑到起点（左上圆角）时会被路径末端截掉，出现"断一下再冒出来"。改成 **dash + gap = 整圈周长**，被截的那段会同时从起点补回来，转角处是连续的一道。
- ⑩整体降速：线速度 `185 → 160 px/s`，并加 **一圈时长下限 6.2s**。原来纯匀速时手机竖屏周长只有 744px、4.02s 就绕完一圈，线速度虽然相同但"绕得太勤"看着快。现在手机竖屏 **6200ms（120px/s，被下限压住）**、手机横屏 **10923ms（160px/s）**、桌面 **16173ms**，圈时差距从 2.4 倍收到 1.76 倍。

**三、数字递增（Count Up）**

- 纯 JS，`TreeWalker` 只动第一个含数字的文本节点，保留前后文字（"从 0 条中筛出" → "从 71 条中筛出"）；ease-out cubic，**1800ms + 180ms 起跑延迟**（1000ms 太快，"一进页面就数完了"，看不出效果）。
- **补零到目标位数**：目标 29 就按两位显示，数到 9 时是 `09` 而不是 `9`。
- **数字在 `DOMContentLoaded` 就折进 `.kiki-num`**（等宽数字 `tabular-nums`，`min-width` 只按目标位数留位），页面一画出来就是最终排版：①数数时位数变化不会顶开右边内容；②不再出现"页面已经画完、640ms 后又插 span，宽度宽一下"——从词汇页返回时那次跳动就是这么来的。
- 兜底：`180ms + 1800ms + 400ms` 后再强行写一次最终值，标签页被切走导致 rAF 暂停时不会永远停在 0。
- 触发元素：`.pillrow span.pill`（「共 16 条精选」「双语 7 条」）、`.cbtn .l`、`.cbtn .r`、`.summary > div`、`.bar .count`（「29 个词」）；滚进视野触发一次，`data-kiki-counted` 防重。

**四、卡片错峰淡入：试用后撤掉**

- 原因：`.kiki-in` 用 `animation-fill-mode: both`，卡片一拿到 class 就被按到 `opacity:0` 再淡上来；而在快速滑动时 IO 是在卡片已经露一半时才触发，视觉上等于"整张卡消失一下又回来"，比原来更闪。
- 已整体删除（CSS + JS），入场只保留水波纹。

**五、修：点正文超纲词跳词汇页不定位**

- 现象：主页正文点 `cautiously` 等超纲词，跳到词汇页后停在页面顶部，没滚到对应卡片。
- 排查：33 个正文词链 / 27 个唯一目标，全部能在 `vocab.html` 找到对应 `id="w-…"`，**锚点本身没错**；直接打开 `vocab.html#w-x` 能正常滚到位（scrollY 1342），只有"从另一页点链接进来"才落回 0。
- 根因：跨文档带 `#` 进入时，浏览器自己的锚点滚动与「`scroll-behavior:smooth` + View Transition」撞车 —— 平滑滚动的动画刚起跑就被过渡快照打断，退回顶部。属于全局机制问题，所以不止 `cautiously`，**所有**超纲词跳转都受影响。
- 修法：新增 `hardLand()`，落地时临时把 `scroll-behavior` 设为 `auto` 做一次"硬跳"（瞬间到位，不走平滑），跳完立即还原，页内目录点击仍是平滑滚动；在 `start()`、`load` 各跳一次，900ms 后再校正一次（图片/字体加载可能把落点顶偏）。实测点击后 `scrollY 1342`、卡片顶端 `64px` = 顶栏底边 `64px`，刚好贴住不被压。

## 检查更新有回音 + 网页视觉升级（1.6.008） (2026-11-21)

**一、先查现成的，再决定自己写**

| 需求 | 上游项目 | 星数 | 结论 |
| --- | --- | --- | --- |
| 全局动效引擎 | `mrdoob/three.js` 119039★ / `greensock/GSAP` 31000★ / `juliangarnier/anime` 74940★ | — | 不采纳：都要额外下 30–600 KB JS 并在 WebView 里跑逐帧循环，为“看起来酷”付帧率和电量代价，与“不能影响体验”冲突 |
| 滚动入场 | `michalsnik/aos` 28056★ | — | 不采纳：它的做法是 `IntersectionObserver` + 主线程回调，我们直接上原生 `animation-timeline: view()`（滚动驱动、合成层，零 JS） |
| CSS 动效库 | `animate-css/animate.css` 83043★ | — | 不采纳：关键帧命名体系庞大，本项目只需要 3 组；自写 40 行 CSS 更可控，也不多一次请求 |
| 平滑滚动 | `darkroomengineering/lenis` 17389★ / `dixonandmoe/rellax` 7115★ | — | 不采纳：Lenis 会接管滚轮/触摸（拦截默认滚动，WebView 里易与下拉刷新、小组件锚点滚动打架）；rellax 是视差滚动，本页不需要 |
| 跨页过渡 | 浏览器原生 View Transitions（Baseline 2025-10） | — | **采纳**：跨文档 `@view-transition` + `rel=expect`，零 JS、零依赖、不支持就瞬切 |

**二、检查更新不再“点了没反应”（1.6.008）**

- 点「检查更新」立刻弹 `正在检查更新…` 的即时反馈，结果不再是转瞬即逝的 toast，而是模态弹窗：
  - 无新版 →「已是最新版本」，正文列出当前版本号+versionCode 与线上版本号+versionCode；
  - 有新版 → 原有「发现新版本」对话框（保留“下载并安装/稍后”）；
  - 失败 →「检查更新失败」，正文附带真实原因（网络异常类名/信息，或“更新清单内容不完整”），并提示可直接下载安装包覆盖安装。
- 启动时的静默检查保持不变：只有发现新版本才提示，且同一版本只自动提示一次。

**三、网页视觉升级（同色调，纯 CSS）**

- 新增 `scripts/web_polish.py`：幂等注入，可反复跑；`docs/latest.html`、`docs/latest-en.html`、`docs/vocab.html` 三页统一，部署前自动执行（workflow 新增一步）。
- 跨页过场：点「难点词汇」/「返回」时旧页轻微上浮淡出、新页自下淡入（240/300ms，`cubic-bezier` 缓出）；`<link rel="expect" href="#kiki-head" blocking="render">` 保证快照时顶栏已解析，不会淡到白页。
- 预渲染：`speculationrules` 以 `moderate` 粒度预渲染同源 html，点进词汇页基本零等待。
- 卡片滚动入场：`animation-timeline: view()` + `entry 2%→40%`，只动 opacity/transform，不监听 scroll。
- 微交互：胶囊/返回键 hover 上浮 2px + 阴影、tap 缩放 0.97；正文超纲词 `a.vw` 悬停变亮；`focus-visible` 统一 2px accent 描边（键盘可用性）。
- 无障碍与降级：全部动效包在 `@media (prefers-reduced-motion: no-preference)` 里，开启“减少动态效果”时逐条关闭并 `@view-transition` 改为 `none`；不支持 View Transitions / 滚动驱动动画的浏览器直接瞬切、无入场动画，功能零影响。
- **v4（同日晚，纯页面改动）**：① 白闪根治——过渡快照层背后是 UA 的白色画布，旧版还给新页加了 `opacity .75` 起手、旧页加了 `brightness()` 压暗，半透明时直接透出白底，来回快速点几次就整页变白；现在只做位移，并把 `html` / `::view-transition` / `group` / `image-pair` / `old` / `new` 六层全部刷成页面底色 `#0e1320`。② 时长 520 / 600ms，缓出曲线 `cubic-bezier(.22,1,.36,1)`（长尾收速）。③ 共享元素跨页形变：`.pill-link`（难点词汇 ›）与 `.back`（‹ 返回今日速递）共用 `view-transition-name: kiki-pill`。④ 词汇页卡片改「错峰点亮」（`animation-delay: min(--kiki-i,10) * 45ms`），日报页仍走滚动驱动。⑤ 发音键点按水波纹。

## 依赖开源、机制补全、APK 自更新 (2026-11-21)

**一、先查现成实现再动手（本轮结论）**

| 需求 | 上游项目 | 星数 | 结论 |
| --- | --- | --- | --- |
| 词频证据 | `rspeer/wordfreq` | 1769★ | **采纳**：Zipf 词频（每十亿词出现次数）比 ECDICT 的 frq/bnc 排名连续得多，且能覆盖词库查不到的长词/复合词，作为额外一份“已认识”证据接入 |
| 近重复检测 | `seomoz/simhash-py` | 423★ | 不采纳：SimHash 靠几十上百个特征位的汉明距离，新闻标题只有 6–12 个词元，特征太少会随机碰撞；我们的重叠系数 + AI 语义两层在这个尺度上更稳 |
| CEFR 词表 | `michigan-musicer/cefr-text-vocab-scanner` | 4★ | 不采纳：思路与现有 CEFR-J + Octanove 完全相同，数据源一致 |
| Android 自更新 | `burgyl/SelfUpdatingApp` 18★、`alltechdev/APK-MultiUpdate` 10★ | — | 不引依赖，按同一套标准做法自实现：版本清单 → 下载 → FileProvider → 系统安装器 |

**二、词表：Zipf 词频接入 + 复核层闭环**

- `known_evidence` 增加 zipf 证据：≥4.15（≈前 1500）记 3 分，≥3.85（≈前 3000）记 2 分；没装 wordfreq 就跳过，判定退回 ECDICT。今天这期复算：再多去掉 `record-breaking`（zipf 4.61，透明复合词）与 `genocide`（3.91），38 张 → **29 张**，真难词（adjudicate 2.47 / extradition 3.28 / divider 2.83）一个没动。
- 复核裁决库跨期：`save_verdicts` 同时写 `data/` 与 `docs/vocab_verdicts.json`，随 Pages 发布，下一期开工先 `curl` 回来再追加，模型对每个词的判断变成可累积的资产。
- 今天这期已按新规则重建上线（29 卡，日期 2026-11-21），并自动修剪正文失效锚点（中英各一轮）。

**三、流水线**

- 新增 `scripts/prune_vocab_links.py`：按 `vocab_manifest.json` 把正文页里指向已删词的 `<a class="vw">` 还原成文字，build_latest 之后自动跑，死链不再上线。
- 新增 `scripts/touch_pages.py` + workflow 末尾「Pages 构建兜底」：轮询 `pages/builds/latest`，`errored` 就自动往 gh-pages 的 `_config.yml` 追加触发注释重建，不用再靠人发现。
- workflow：vocab 步骤前 `pip install wordfreq`（失败不阻塞）、先拉回 gh-pages 的复核缓存。

**四、APK 自更新（1.6.007）**

- `UpdateChecker.kt`：启动静默查一次 `https://…/KIKINEWS/app/version.json`（带 `Cache-Control: no-cache` 和随机串绕 CDN），比 `versionCode` 决定提示；同一版本只自动提示一次（prefs 记 `update_prompted_code`）；设置菜单常驻「检查更新」可手动触发。
- 下载到 `cache/apk/`，按清单里的 `sha256` 校验，`FileProvider`（authority `${applicationId}.files`，仅开放 cache/apk）交给系统安装器；Android 8+ 先检查 `canRequestPackageInstalls()`，没权限就跳 `ACTION_MANAGE_UNKNOWN_APP_SOURCES`。
- 清单字段：`versionCode / versionName / apk / sha256 / size / notes / minSdk`，由 `scripts/publish_apk.py` 从 `build.gradle.kts` 读版本、算哈希后生成，APK 放 `docs/app/`。
- 已发布并验证：`app/version.json` 160007、APK 2495 KB 可下载、sha256 一致；Pages 构建 built。

## 把“人工审计”做成流水线的一道关卡：卡片复核层 (2026-11-21)

起因：11-21 期那份逐条审计（38 张卡判出 7 张该删）是靠人读一遍判出来的，而规则层永远算不出“这个词 C1 读者到底认不认识”。既然模型判得准，就把它固定成一道关卡，而不是每次靠人工。

新增 `audit_cards()`（`scripts/build_vocab.py`）：

- 入口只送**规则层判不准的卡**：词频 4000–9000 的灰区词，以及全部“熟词生义”卡；每卡带单词、词库排位、中文释义、新闻义、原文语境。
- 两个判断：① 哪些词 C1 读者早就认识、出卡等于白占版面；② 哪些“新闻义”只是把词典释义重说一遍。
- **反向守卫**：删卡只对灰区生效——词频 ≥9000 的真难词、以及缺词频的长词，模型说删也不删（`AUDIT_MIN_RANK`/`AUDIT_MAX_RANK`）；`drop_sense` 只对带新闻义的卡生效。任何失败（无 key、输出不可解析）一律全部保留，绝不因复核挂掉而丢词。
- 结论按词落盘 `data/vocab_verdicts.json`（`word → keep/drop`），下一期同一个词直接复用、不再调用模型；因此每天的复核只需一次调用、几十行输入。

配套：`tests/test_vocab_rules.py` 追加 5 项（灰区外的词不接受删卡、纯单词卡不接受 drop_sense、缓存命中不重复调用、输出损坏时全部保留、无 key 时不调用），与原有 13 项、去重 12 项合计 30 项全绿。

同日把 11-21 这期按新规则重建上线：38 张 → 31 张，只去掉 tech / reportedly / trillion / landmark / precedent / paradigm / deepen，其余 31 张不增不减；同时把 `latest.html` 里指向这 7 个已删锚点的链接还原成普通文字（46 条锚点降到 37 条），避免正文链接跳到空处。无音标的只有 3 个长词（iteratively / record-breaking / unverified），离线重建拿不到联网音标，已与用户确认可接受。

## 11-21 期词表审计：常用词频段的 7 张假超纲卡，以及 AI 去重在生产失效的两处加固 (2026-11-21)

起因：11-21 期线上词表 38 张卡逐条对照 CEFR/词频后，发现有 7 个词是 C1 读者本来就认识的日常词（tech、reportedly、trillion、landmark、precedent、paradigm、deepen），另有 3 张“熟词生义”卡的注释只是把词典主释义重说一遍（bail、raid、organ）。追下去是两个独立成因。

1. **词库 4000–8000 名这一档被判成“零证据”**。`known_evidence` 只在词频 ≤4000 时给 4 分、C1/C2 给 2 分，其余一律 0 分；而词库给 tech（4973）、reportedly（4397）、trillion（5167）、landmark（4715）、precedent（5093）、paradigm（5201）、deepen（6730）都没挂 CEFR 等级，于是全部按超纲层出卡，还打了 ★★。
   改法：新增 `FAMILIAR_RANK = 5500`，词频落在 5500 名内一律给 2 分弱证据；5500–8000 名但 Collins ≥2 星（口语/新闻语料里明显常见）同样给 2 分。低于 1 星或更冷的一档不动，宁可多留一张也不漏真生词。
2. **AI 去重层在生产上两次都没跑成**。11-20 21:55 的 run 55（digest job 136593635730）日志里，`dedup: AI call failed (Error code: 400 ... "Failed to generate JSON", 'failed_generation': '')` 出现两次：Groq 对一次性输出整批重复组 JSON 直接拒绝，代码走 except 分支只留下确定性标题层，而当天 71 条候选在标题层最高只到 0.67，低于 0.72 阈值 → 线上仍是 UK/EU 脱欧协议 4 条、基辅桥梁 2 条、Nasdaq/Anthropic 3 条、锡克教刺杀 2 条。
   改法：`merge_topic_duplicates` 改为**分块评审**（`AI_DEDUP_BLOCK = 16`，抽出 `_ai_dedup_block`），单块被拒就二分递归再试（`_collect_ai_dedup_groups`），索引带 offset 回拼，任一块成功即生效，不再一条失败就整批放弃。标题层阈值由 0.72 降到 0.62（今天 71 条候选在 0.55–0.75 区间只有锡克教那一对，无假阳性），使“19 years”/“19-plus years”这类改措辞的同事件也能兜住。

验证：11-21 期真实英文正文离线重建（`VOCAB_AI=0`、`VOCAB_NO_NET=1`），38 张卡 → 31 张，正好去掉 tech、reportedly、trillion、landmark、precedent、paradigm、deepen，无新增、无误删（adjudicate / extradition / ballistic / retaliation 等真超纲词全部保留）。`tests/test_vocab_rules.py` 追加 4 项（词频段弱证据、Collins 弱证据、冷词边界、超 8000 名不收），`tests/test_title_dedup.py` 追加 3 项（改措辞同事件合并、单块被拒后二分仍能合并、跨块 offset 不串组），两套共 29 项全绿。

遗留：bail / raid / organ 仍以“熟词生义”卡出现，注释（保释、突袭、机关报）与词典主释义高度重合，属于注水卡；要治得改 `data/news_senses.json` 的注释口径（只写“本义之外”的新闻义），单靠代码过滤会误伤 hawk / sanction / bill / verdict 这批真正有用的法律政治义。

## 难点词汇的四个判定漏洞（变形词、C1 冷词、派生误判、短语重复） (2026-11-20)

起因：用户把 11-20 期词汇页的 27 张卡逐条对照 CEFR 与词频，认为至少要达到 C1 以上、并且是新闻里真正卡人的词。核对结果 20/24 合格，但有 2 个基础词混进来（dozens、organ），3 个短语与单词卡重复，另有 2 到 3 个真难词该出没出。逐条查下去是四个独立缺陷。

1. **变形词在词库里没有回指时，两个方向都会漏**。词库 exchange 字段不全：`dozens` 只登记了原形 `dozen`（CEFR B1），变形行没有挂回去，于是 dozens 查不到词频、被当成零证据的极难词收进来还打了五颗星；`reparations`（原形 reparation，词频 13025）反过来在正文里根本找不到原形词条，整条被跳过。
   改法：新增 `inflection_candidates()`，按规则后缀回推原形（ies/ied→y，ing/ed/es/s 去尾，双写辅音还原，补词尾 e），并把这些原形一并加入 `wanted` 参与扫库；`resolve()` 在 exchange 查不到时用回推结果，且只在原形确实在词库里时采用。
2. **C1 词被整类当成“读者已认识”**。`known_evidence` 对 C1 直接给 2 分，只有 0 分才进超纲层，于是 persecution（8852）、tribunal（3467）这种真冷词永远出不来。
   改法：C1 且词频 ≥8000（或没有任何词频）时按零证据处理，进超纲层；词频靠前的 C1 词（verdict 4163）仍然算认识。
3. **派生词排除把“词库里没有”误当成“读者肯定认识”**。`derived_from_known` 用 `known_evidence(bases.get(root))` 判根，而 `known_evidence(None)` 返回 99（表示缺词条），于是任何拆出来的根只要不在词库里就被判成“熟词”，reparation（拆出 repar）与 convene（拆出 nvene）被整年吞掉。
   改法：只有根**真的在 bases 里**且证据 ≥3 才算透明派生。
4. **短语与单词重复出卡**。AI 返回的 `flagrant violation` / `inaugural meeting` / `petroleum production` 与单词卡 flagrant / inaugural / petroleum 同页并列，等于同一个词占两张版面。
   改法：短语层与术语层在出卡前检查实词是否已经出过卡，命中就跳过。

另加一条词频下限：3000–4000 名以内且没有新闻义的词（`MIN_CARD_RANK=4000`）不再进超纲层，留给“熟词生义”层处理；organ 因此只以“新闻义：机关报、机构”的身份出现，不再冒充超纲词。

验证：用本期真实英文正文离线重建（`VOCAB_AI=0`、`VOCAB_NO_NET=1`），词表从 24 个单词（其中 dozens 误收、dynamics 被误吞）变为 31 张卡：dozens 消失，reparation、convene、persecution、exodus、escalation、compliant、precipitate 补上，3 个重复短语消失。新增 `tests/test_vocab_rules.py` 共 13 项，覆盖变形回推、原形优先、B1/B2 与 C1 冷词的证据分、缺失词条不参与派生判断，全部通过。

## 同一事件被写成多条精选：去重失效的根因与修正 (2026-11-20)

现象：11-20 期"共 16 条精选"里，缅甸/罗兴亚种族灭绝判决占了 4~5 条（措辞不同、指向同一判决），Anthropic IPO 两条（"hits $2T in Nasdaq debut" 与 "估值 1.76 万亿美元"），同一场特朗普-普京-习会面也出现多条。

根因两条，都在流水线侧（页面只是忠实渲染了 digest 的结果）：

1. `merge_topic_duplicates` 的 AI 去重是**单次 LLM 调用**，让模型一次性输出全部重复组 JSON。这份输出与生成摘要共用 `max_tokens=768`，一旦被截断，`parse_json_response` 返回 `None`，旧代码直接 `return items` —— **静默失效，等于完全没去重**，日志里也看不出来。
2. 只有 AI 一条路，没有确定性兜底。跨媒体转载同一稿、同义改写（`top UN court` / `world's top court`）、译成另一种语言、只改标题的聚合稿，都会各自成条。

改法：改成"先确定性、再语义"两阶段。

- 新增 `src/processing/title_dedup.py`：标题归一化（NFKC、去 HTML、统一弯引号、折叠标点、去 `'s`、剥掉 `- Reuters` / `| BBC News` 这类媒体尾巴）+ 词元化（拉丁词去停用词、中日韩取二元组）+ 并查集聚类。判定式取**重叠系数 ≥ 0.72 且 Jaccard ≥ 0.20**，不看 IDF —— IDF 在只有两三条的小批量里分母塌缩会压低分数，导致同一阈值在测试里灵、线上不灵。守卫：两侧各 ≥3 词元、至少共享 2 个词元，避免 `US news` 这类泛化短标题被合并。
- `src/orchestrator.py`：`merge_topic_duplicates` 先跑标题合并，只剩 ≤1 条就直接返回；再拼 prompt 调 AI，`max_tokens` 按条目数给足（`max(1024, 64 + 16*条数)`），与摘要预算解耦。AI 解析失败或普通异常时**保留已完成的标题合并结果**并打印 `keeping the deterministic title merge`，不再静默返回全量；并抽出 `_merge_duplicate_groups` 复用"重复正文并入主条、评论区合并、标注 `--- From <source> ---`"的语义，日志按 `dedup(title)` / `dedup(ai)` 区分来源。
- `src/ai/prompting/deduplication.py`：把"同事件"定义为"同主体 + 同动作/裁决 + 同对象/结果"，明确必须合并的四类（不同媒体同稿、头条与解读稿、另一语言译文、聚合标题）与必须分开的三类（同产品不同事件、数周后的新进展、不同受害者的不同事件），要求输出紧凑单行 JSON 以减少截断。
- 新增 `tests/test_title_dedup.py`（12 项）：归一化、词元、四种措辞聚成一组、不同事件不误合、泛化短标题守卫、AI 返回空/抛异常时仍保留标题合并、AI 调用带足 `max_tokens`、中文同事件合并。

实测：拿 11-20 期线上 80 条候选离线复算，4 组共去掉 8 条 —— 罗兴亚判决 5 条合 1、Anthropic 2 条合 1、特朗普普京习 3 条合 1、Fiona 河马 2 条合 1，逐对人工核验无假阳性。已知局限：仅差一个产品名的标题（`iOS 27 beta` 与 `macOS 27 beta`）在这一层会被误合，留给 AI 语义层纠正；`UK 强制 Apple 后门令`（0.67）、罗兴亚"判决说了什么/接下来会怎样"解读稿（0.54）分数不够，仍由 AI 层判断。

## 正文行尾大段空白的根因与修正 (2026-11-19)

现象：卡片正文（英文 note 块、中文段）有的行末尾空一大截，看着像"明明能放下却换行了"。

量测（无头 Edge 逐字 `getClientRects()`，卡片内宽 326px / note 299px）：

- note 段每行剩余宽度：23 / **62** / 23 / 128。62 出现在 `…mid-November after` 之后，因为下一词 `allegations` 宽约 85px > 剩余 62px，只能整体掉到下一行。
- 中文段每行剩余 15 / 14 / 1 / 9 / 21，本身是满的；截图里"他愿意重新担任｜CEO"的空档是 `CEO` 这个拉丁词整体不可分造成的。
- 对照实验：同一段分别用 `text-wrap: pretty` 与默认 `wrap`，逐行空隙**完全相同**（说明本引擎上 pretty 不改断行）。

结论：这不是 bug，是右参差排版的固有现象——浏览器只在词间断行，当一个不可分单位（长单词、`CEO` 这种拉丁串）宽于剩余空间时，它整体下移，行尾就留出最多一个词宽的空洞。另有两条我们自己造成的放大器：

1. `@media (max-width:520px)` 里写着 `hyphens:none`，手机上把断词关掉了，`leader-ship` 这类复合词只能整词换行，窄栏下空洞更明显。
2. 正文用了 `text-wrap: pretty`。它**不填行**，只是把词往下挪以避免末行孤字，3~5 行的短段整段都在它的回看范围内，反而会在行尾掏洞。

改法：

- 删除正文与词汇页的 `text-wrap: pretty`（`.card p`、`.t`、`.en`、`.ex`、`.ctx`）；`balance` 只留给标题 `.card h3` 与词汇页 `.w` 这类短块。
- 窄屏不再关断词：`.card p{hyphens:auto;-webkit-hyphens:auto}`，让长词在词内断开把行填满。
- 词汇页英文释义、例句、原文语境同样打开 `hyphens:auto`。
- 未采用两端对齐：窄栏下没有断词配合时词距拉伸会出"河流"，中文尤其明显（此前已因此撤掉 justify）。

## 主页正文的难点词可点，直接跳到词汇页对应卡片 (2026-11-19)

原来词汇页会把词在原文语境里加粗，但主页正文里的同一个词是"死"的，看到只能记住再去词汇页找。现在主页（含 `latest-en.html`）正文里命中当期难点词汇的词都标成行内链接，点一下直接落到词汇页那张卡。

- 词汇页每张词卡新增稳定锚点 `id="w-<词>"`（如 `w-lieutenant-colonel`）；用词本身而不是序号，跨期一致、选中词变化也不会整体错位。
- 词汇页额外输出 `vocab_manifest.json`（词 + 锚点，约 2KB），主页据此标注；**只在 `source` 与本期英文正文完全一致时生效**，换期自动失效，不会出现链着上一期词表。
- 只标正文、不标标题：标题本身是指向原文的外链，嵌套 `<a>` 非法且点不动。已在 `<a>` 里的文本同样跳过。
- 匹配支持屈折变化（severed / severing → sever，supersedes → supersede），只收规则变化，不做词干化，宁可漏标也不误标；长词优先（`lieutenant colonel` 不会被拆成 `lieutenant`）。
- 样式：颜色之外再加一条虚线下划线做第二指示（不靠颜色单独表达），悬停/键盘聚焦转实线并加 outline；用原生 `text-decoration` 而非 border/伪元素，折行时下划线跟着走。
- 实测本期 24 处标注、覆盖全部 19 个词条，锚点全部对得上。

## 修复「页面日期退回 11-12」（用本地过期正文覆盖线上）(2026-11-18)

线上两页一度显示 2026-11-12，原因不在流水线：本地仓库 `docs/_posts` 只到 11-12（流水线的每日出刊只在 Actions 里跑，本地不会自动同步），手工重建后直接推送，等于把旧一期发上线。

- 从 gh-pages 拉回 11-17 的中英正文，并取**该期 digest 提交**里的 `candidates.json`（`latest.json` 也取自同一提交），重新构建两页后推送；页面恢复为 16 条、日期 2026-11-18（北京时间出刊日），难点词汇 19 词。
- `latest.json` 的 `generated_at` 还原成那一期的原始时间（2026-11-17T22:26Z）。它同时是 guard 判断「该不该出下一期」的依据，重建会把它改成当前时间，等于把下一次出刊整整推后 12 小时。
- 新增 `scripts/rebuild_current.py`：以线上最新一期为准拉正文与候选数据重建，构建后自动还原 `latest.json`、校验页面日期与卡片数，`--push` 才推送（gh-pages 根 + main/docs 五件套）。以后手工重建一律用它，不要再直接跑 build_vocab/build_latest 后推送。

## 网页按 Modern Web Guidance 指南做的 CSS 修正(2026-11-18)

装了 Chrome 团队的 modern-web-guidance 指南库（210 篇，放在 `D:\AI\modern-web-guidance`），拿主页与词汇页逐条对照，改掉四处"自己造的土办法"：

- **标题与正文换行用反了**：`.card h3` 原来用 `text-wrap:pretty`（那是防孤行的正文算法），改为 `text-wrap:balance`；正文 `p` 反过来加 `text-wrap:pretty`。标题求两行等长、正文求不出孤字，两者算法不同不能互换。词汇页词头 `.w`（多词术语会折行）同样改 balance，译文 / 例句加 pretty。
- **取消正文两端对齐**：`text-align:justify` 在手机三行一条的窄栏里会产生词距忽大忽小的"河流"，中文尤其明显；改为左对齐，英文长词仍保留 `hyphens:auto` 断词防溢出。
- **补上滚动条与原生控件配色**：原来完全没设，深色页面在 Windows / 安卓上挂一条亮灰滚动条。新增 `--sb-thumb:#5b7196` / `--sb-track:#0b1018`（对比度约 3.6:1，满足 WCAG 1.4.11）+ `scrollbar-color`，并声明 `color-scheme:dark` 让原生控件跟随；Safari 18.2 前的浏览器走 `@supports not (scrollbar-color:auto)` 里的 `::-webkit-scrollbar` 回退。刻意不设 `scrollbar-width`（thin 的滑块热区太小，且会让 WebKit 伪元素失效）。
- **触控目标放大**：`@media (pointer: coarse)` 下目录胶囊 32→40px（平板 42px）、候选行 padding 加大、摘要三角加高；词汇页返回键加大、发音键视觉 32px 而热区用 `::after` 外扩到 48px。鼠标端尺寸完全不变。
- **词汇页锚点被吸顶栏压住**：给 `html` 加 `scroll-padding-top:64px`。

保留的部分（指南确认没有更优方案）：宽屏瀑布流仍然是自写的"当前最短栏"填充脚本——原生 grid lanes 目前只有 Safari 27.2 支持，指南给的替代（`grid-auto-flow:dense` 打乱 DOM 顺序、`columns` 列优先阅读）都不适合按序阅读的新闻流。

## 抓词算法改版：从「几条阈值筛人」改成「按已知证据自适应」(2026-11-18)

老算法是三条阈值同时成立才算超纲词（词频排位 > 9000 **且** Collins < 2 **且** tag 不含 cet4），
结果两头都错：`lieutenant` / `colonel` 被词库误标成 cet4 直接出局，`custody` 因为 Collins 给了 2 星被杀，
而部分四级词反而溜进来；`lieutenant colonel` 这种多词术语、`spying` 这种屈折变化、
`counter-terrorism` 这种连字符词，则在进入判断之前就被代码丢掉了。

- **判定改为集合归属**：`known_evidence()` 只看「有没有任何一条‘读者已经认识’的硬证据」——
  教材词表 A1–B2、牛津标注、Collins ≥ 3、词频前 4000，任一条命中即出局；`cet4` 标签噪声太大，
  只在词频 5000 以内算弱证据。不再要求多条阈值同时满足。
- **排序改为证据累加**：`rarity_score()` 把「无 CEFR 等级 / 词频档位 / Collins ≤ 1 / 无牛津 / 无标签 / 词长」累加，
  当天出现次数只做同分排序，不再用单一词频决定版面。
- **新增术语层**：正文 2–4 元片段与词库多词条目求交，出卡条件是「至少一个组成词本身没过已知判定」
  （`lieutenant colonel` 里的 lieutenant），带连字符的透明复合词（`end-to-end` / `sea-level`）不出卡。
- **连字符词不再丢弃**，`counter-terrorism` / `cyber-crime` 这类整体含义跑偏的仍出卡。
- **屈折变化不再当派生词砍掉**：`roots_of` 只处理构词派生（un- / -ness / -ation），
  `spying` 不再被判成 `spy` 的简单派生、「间谍活动」这条新闻义不再丢。
- **无音标也出卡**：`chokepoint` 这种词库没音标的词，从「整卡丢弃」改为「只省音标、保留发音按钮」。
- **噪声清理**：正文先剥 URL / 邮箱 / HTML 实体（裸链接曾灌进 `https` / `href` / `quot`）；
  句中大写次数 ≥ 小写次数的词按专名排除。
- 同一期日报（2026-11-12）出卡从旧算法 20 词变为 35 张，实测样本
  （`A U.S. Army lieutenant colonel was arrested...`）稳定产出 `lieutenant colonel` +
  `lieutenant` + `custody`。

## v1.6.006 修复「无法添加组件」（RemoteViews 控件白名单）(2026-11-18)

1.6.005 用纯 `android.view.View` 画那层外框。`View` 不在 RemoteViews 允许的控件名单里（只认 FrameLayout、LinearLayout、ImageView、TextView、ListView、GridLayout 等），launcher 一 inflate 就抛异常，于是「Couldn't add widget」：不能预览、也加不上，什么内容都没有。

- 把那层改成 `FrameLayout`（同样只用 `android:background`），结构不变、位置不变，仍然叠在底板之上、四角花边与内容之下。
- 顺带做了一次控件白名单自查：6 个布局里只出现 FrameLayout / LinearLayout / ImageView / TextView / ListView，全部在允许范围内。
- 版本 1.6.006（versionCode 160006）。
- **新增文档**：`KIKINEWS-小组件踩坑记录.md`（仓库根目录），把 1.5.000→1.6.006 期间所有失败过的做法、根因与正确写法整理成六类，含改前必读的两条和改完必做的自查清单；交接文档同步加 8.7 节指向它。

## v1.6.005 边框与底板分离（边框不再随透明度变淡）、4×1 头部不再压框线（2026-11-18）

- **边框跟着透明度变淡的问题**：11 档底板 `bg_widget_a000…a100` 里一直混着描边（`#C62C364A` 外圈、`#7E6FE3D4` 内细线），所以调透明度时连框一起淡掉。现在底板只画半透明色块，边框抽成独立的 `frame_widget.xml`（外圈 1dp `#E62C364A` + 内缩 5dp 的 0.7dp `#B36FE3D4` 细线，固定不透明），在 6 个布局里以一层 `View` 叠在底板之上、四角花边与内容之下。调透明度只影响底板，框线始终清晰；调到 0% 时只剩框和文字。
- **4×1 头部压着上框线**：紧凑版头部只有 14dp，且内容区从 y=0 开始，日期 / 条数 / ⚙ 正好压在顶部描边上。现在内容区加 `paddingTop`（手机 4dp、平板 6dp），左内边距从 10dp 提到 12dp（平板 14dp），右内边距 4dp 提到 6dp——避开内细线与四角花边。
- 版本 1.6.005（versionCode 160005）。

## v1.6.004 手机侧半行溢出花边框、透明度按组件独立（2026-11-18）

平板已经正常，这次只动手机侧表现，平板布局逻辑不变。

- **半行文字跑到框外**：列表填满整个卡片高度，固定行高（22/26dp）除不尽剩余高度，最后一行必然被切一半；而列表内容区一直顶到卡片最下沿，被切的文字就压在 1dp 描边上、右下角的评分也撞进角花里。修法是给 ListView 加 `paddingBottom`（手机 8–10dp、平板 10–12dp）与 `paddingEnd`（手机 10–12dp、平板 12–14dp），并让 `clipToPadding` 生效——切行发生在框内侧，文字与评分都不再越界、不再压角花。
- **最后半行本身保留**：它是列表「下面还有内容、可以继续滑」的视觉提示，和系统滚动列表一致；手机上滑动的确能翻出后面的条目，这个行为不变。
- **透明度改为按卡片独立**：旧版所有卡片共用 `bg_alpha` 一个键，后调的那次会覆盖前一次（4×2 调 20%、4×1 调 80%，两张都变 80%）。现在存在 `alpha_<组件id>`，每张桌面卡片各存各的；删除组件时一并清掉。未设置过的新卡片仍取全局默认 90%。
- 设置页文案补了一句「每张桌面卡片各自独立，这里只改你点开的那一个」。
- 版本 1.6.004（versionCode 160004）。

## v1.6.003 4×1 也改成集合型 + 点齿轮打不开、多组件互相串页的修复（2026-11-18）

**问题**：4×2 已经正常（平板能铺 11 条），但 4×1 还是单行布局，只有一条、其余空白——它天生不参与自适应。另外自查发现两处会出事的写法。

- **4×1 换成集合型**：改用 `widget_list_compact.xml` / `widget_list_compact_wide.xml`（头部 14dp / 18dp）+ `widget_row_compact.xml` / `widget_row_compact_wide.xml`（行高 22dp / 26dp）。手机 4×1（约 40dp 高）放「头部 + 1 条」，平板 4×1 自动铺 3–5 条。两个尺寸现在走同一套机制，不再有「一种尺寸是自适应、另一种是一次性」的分裂。
- **点 ⚙ 打不开（自查修复）**：旧版是「广播 → `startActivity`」，Android 10 起后台启动 Activity 会被系统拦掉，部分机型点齿轮没反应。改成直接用 `PendingIntent.getActivity` 打开 `WidgetConfigActivity`，并给 Intent 加 `kiki://widget/<id>/config` 的 data 保证每个组件各自独立。
- **多组件互相串页（自查修复）**：旧版所有组件的箭头/打开 App 共用固定 requestCode，加上 `FLAG_UPDATE_CURRENT` 后，后建的 PendingIntent 会覆盖先建的，点多组件里的箭头可能动的是另一个组件。现在 requestCode 改成 `(id*16 + 槽位)`，并给每个 Intent 附 `kiki://widget/<id>/...` 的 data，彻底隔离。
- 头部信息保持「日期 + 总条数」，‹ › 跳一屏（步长 3），跳完 `notifyAppWidgetViewDataChanged` 重取数据。
- 版本 1.6.003（versionCode 160003）。

## v1.6.002 小组件 4×2 改为集合型（ListView），平板不再只给三条（2026-11-18）

**1.6.001 为什么还不够**：1.6.001 用「响应式尺寸映射」把 1–8 行的布局全部交给系统挑，但这条路仍然依赖 launcher 回传一个可信的尺寸——这台平板的 launcher 给的尺寸明显小于真实高度，系统于是挑了 3 行那一档，剩下三分之二自然空着。任何「按数字挑布局」的写法都会在它上面失效。

- **改为集合型组件（Android 官方推荐做法）**：新增 `WidgetService.kt`（`RemoteViewsService` + `WidgetFactory`），4×2 的布局换成 `widget_list.xml` / `widget_list_wide.xml`——头部固定一行，下面 `ListView` 占满剩余高度。行数不再由 App 计算：装得下几条系统就排几条，超出部分可以滑动。所以「只给三条、底下空一大片」和「第三条只露半行」从原理上都不可能再出现，也不需要任何猜 dp 的算法。
- 行高仍写死（手机 26dp、平板 30dp，见 `widget_row.xml` / `widget_row_wide.xml`），保证条目不会被拉稀。
- 4×1 维持单行布局（`widget_card_single` / `widget_card_wide_single`），行为不变。
- **Manifest 补 `WidgetService` 声明**（`permission=android.permission.BIND_REMOTEVIEWS`、`exported=false`）；列表项点击改用 fill-in intent + `setPendingIntentTemplate`（S+ 用 `FLAG_MUTABLE`，S- 不加 `FLAG_IMMUTABLE`），点条目仍能跳正文锚点。
- **4×2 的 `initialLayout` / `previewLayout` 改指列表布局**，避免首帧和预览显示成固定三行版。
- 头部信息简化为日期 + 总条数；‹ › 仍是手动跳一屏（步长 3 条），跳完调 `notifyAppWidgetViewDataChanged` 重取数据。
- 版本 1.6.002（versionCode 160002）。

## v1.6.001 小组件：改成系统侧响应式布局，修手机半行被裁与平板只给三条（2026-11-18）

**两个现象**（用户真机截图）：手机上 4×2 显示的第三行只剩一半字；平板上拉大了仍然只有三条、下面空一大片。根因是 1.6.000 仍在用 `OPTION_APPWIDGET_MIN_HEIGHT` 自己算行数，而不同 launcher 回传这个值偏差很大——手机回传偏大（按宽的 30dp 行高排出 3 行，实际高度装不下，第三行被父容器裁掉），平板回传偏小（只排 3 行）。另外 1.6.000 用「组件宽度 ≥300dp」判断宽版，手机 4×2 的宽度正好过线，于是手机误用了平板字号和 30dp 行高，把问题放大。

- **改为响应式布局（Android 12 官方做法）**：把「能放 1 行 / 2 行 …… 8 行」的布局全部注册进 `RemoteViews(Map<SizeF, RemoteViews>)`，由系统按组件真实尺寸挑能装下的最大一档。不再自己猜高度，因此既不会出现半行被裁，也不会「只给三条」。宽度键统一给 1dp（表示任何宽度都接受），系统只按高度挑档。
- **布局按行数拆成静态资源**：`widget_card_r2.xml … r8.xml`（手机，行高 26dp）+ `widget_card_wide_r2.xml … r8.xml`（平板，行高 30dp）+ 两份单行版 `*_single.xml`，共 16 个，由生成脚本 `gen_widget_v161.py` 输出，行高写死。
- **窄宽不再看组件宽度**：手机还是平板由 `smallestScreenWidthDp ≥ 600` 判断，避免手机 4×2 被误判成宽版（这正是半行被裁的直接原因）。
- **翻页语义改为「首条下标」**：prefs 里的 `page_<id>` 现在存当前首条在 items 里的下标，翻页步长仍是 `baseSlots`（4×1 走 1 条、4×2 走 3 条），页码显示按 `baseSlots` 折算。条目按 `(start + i) % total` 循环取，最后一页也永远填满可见行。
- **picker 标签**：vivo 系 launcher 不认 `targetCellWidth`（只有 Android 12+ 原生 launcher 认），它仍按 `minWidth` 换算，所以手机上还可能显示 5×1 / 5×2。这是 launcher 侧行为，不影响组件本身按 4 列渲染；把 minWidth 改小会连带把平板的标签算成 3 列，所以维持 340dp。
- 版本 1.6.001（versionCode 160001）。


## v1.6.000 小组件重写：按格子声明尺寸、固定行高自适应、透明度可调、花边外框（2026-11-17）

**问题**（用户真机反馈）：手机上 picker 标 5×1 / 5×2，平板上标 4×1 / 4×2，且平板条目下方小字是 3×1 / 3×2；平板上把 4×2 拉高后行距被撑开、只显示 4 条却空一半；浅色壁纸上黑底突兀；平板字号偏小。

**为什么不是 Glance**：Glance 能声明响应式尺寸，但要引入整套 Compose 工具链（Compose 编译器 + runtime），APK 体积与编译链风险上升，且对 9-patch 花边、整块透明度的支持不如现有 RemoteViews 直接。这次改的其实是「按格子声明 + 固定行高」，这两点 RemoteViews 都能做到，收益相同而代价小得多。

- **picker 标签统一**：`widget_info_4x1/4x2.xml` 加 `android:targetCellWidth="4"` / `targetCellHeight="1|2"`（Android 12+）。launcher 直接用格子数标注，不再拿 `minWidth` 反推，手机与平板都读 4×1 / 4×2；Android 11 及以下仍走 `minWidth=340dp` 兜底。另加 `maxResizeWidth/Height`，免得被拉到超出布局上限。
- **行距不再撑开**：每行改为**固定行高**（手机 26dp、平板 30dp），删掉 `layout_weight` 平分。能显示几行由组件真实高度算：`slots = (高度 − 头部 − 内边距) / 行高`，上限 8 行（布局里补齐到 8 行，多出来的隐藏）。**拉高组件只会多显示条目**，不会再把行距拉大；平板 4×2 一格约 220dp 时能放 6 条。
- **窄/宽两套布局**：`OPTION_APPWIDGET_MIN_WIDTH ≥ 300dp` 用 `widget_card_wide.xml`（行高 30dp、标题 14.5sp、评分 11sp、头部 24dp），否则用 `widget_card.xml`（26dp / 12.5sp / 9.5sp）。平板字号偏小的问题就是靠这一层解决。
- **透明度可调（0–100%，10% 一档）**：预制 11 个背景 `bg_widget_a000…a100`（底板 `#0E1520` 带 alpha + 描边 + 内层细线），渲染时按偏好切换 `setBackgroundResource`，不画位图（避开 RemoteViews 位图大小限制）。入口：组件右上角新增 `⚙`，点开 `WidgetConfigActivity`（滑杆 + 预览块 + 保存），保存后立即重绘所有组件；provider 里也配了 `android:configure` + `widgetFeatures="reconfigurable"`，部分 launcher 长按组件可直接进设置。默认 90%。
- **现代花边外框**：新增 `ic_corner_curl.xml` 向量（两段弧 + 两个圆点），四角各放一个 ImageView 用 `android:rotation` 拼出完整边框，矢量缩放不糊。这也就是天气组件那种「小花边」的通行做法——要么 9-patch，要么四角装饰件拼。
- **行为保持**：`‹ ›` 手动翻页、系统 30 分钟刷新自动翻一页、点标题进 App 定位、点日期开 App。左右滑动翻页仍然做不了（RemoteViews 无手势）。
- 版本 1.6.000（versionCode 160000）。


## v1.5.002 小组件：picker 标签对齐 4 列、平板行距收紧（2026-11-17）

- **尺寸标签为什么显示 3×1 / 3×2**：picker 下面那行小字不是我们写的，是 launcher 拿 `minWidth` / `minHeight` 按自己的格子大小换算出来的。原来 `minWidth` 写 250dp，手机和平板都被算成 3 列（系统不认「4×1」这个名字，只认 dp）。现在 `minWidth` 提到 340dp（`minResizeWidth` 仍是 250dp，放上去以后可以往回拉窄），标签应该读成 4×1 / 4×2。
- **平板上行距过大**：行数是用 `OPTION_APPWIDGET_MIN_HEIGHT` 算的，launcher 回传的仍是手机尺度的值，平板上一个格子实际更高，于是只给了 4 行、剩余高度被行平分，看着又稀又空。现在在最小屏宽 ≥ 600dp 的设备上把估算高度放大 1.6 倍，行数跟得上真实高度，行距自然收紧；手机上比例保持 1.0，行数不变。
- 版本 1.5.002（versionCode 150002）。

## v1.5.001 小组件：picker 拆出 4×1 / 4×2，行高填满整块（2026-11-17）

**两个问题**（用户真机反馈）：一是桌面小组件选择器里只有一条「2×1」，找不到 4×1、4×2；二是平板上 4×1 一条字缩在中间、上下空一大片，4×2 三条挤在顶上、下面空一半。

- **picker 里拆成两个独立条目**：`KikiWidgetProvider4x1` 与 `KikiWidgetProvider4x2` 各带一份 provider 信息（`widget_info_4x1.xml` / `widget_info_4x2.xml`），标签分别是「KIKINEWS 4×1」「KIKINEWS 4×2」。原来只有一个 provider、`minWidth` 写 110dp，launcher 就按最小尺寸把它标成「2×1」——不是卡片真的只有 2×1。两个条目共用同一套渲染逻辑，只是 `baseSlots`（默认行数）不同：4×1 给 1，4×2 给 3。
- **行高不再写死 24dp**：六行改成 `layout_height=0dp` + `layout_weight=1`，可见的行平分剩余高度。这样平板上一个格子本来就高，行会被撑开填满，不会出现「上面几行、下面空白」。
- **行数按真实高度算**：`slots = (可用高度 - 28dp 头部) / 24dp`，上限 6；`OPTION_APPWEDGET_MIN_HEIGHT` 拿不到（刚添加、launcher 还没回传）时退回 provider 的 `baseSlots`，避免 4×2 被渲染成一条。平板 4×1 一个格子够高时会自动显示 3 行，不再是一条字缩在中间。
- **箭头热区加宽**：30dp × 整行高度，比原来的 24dp 好点。
- **关于左右滑动翻页**：Android 小组件的 RemoteViews 不支持手势监听（只能点，不能滑），所以保留 `‹ ›` 两个按钮，没有做滑动。要做滑动得换成 App 内控件，桌面小组件做不到。

## v1.5.000 桌面小组件（2026-11-17）

**为什么做**：网页一屏能读 16 条，桌面小组件没这么大空间，直接搬会挤成一团。做法是只放「最值得看的几条标题」，一条一行、不折行、不写摘要，想看正文点进去。

**先摸了一遍同类产品**：Google News 只有一个小部件，默认 3×2（图标 + 一条标题 + 出处时间 + Full Coverage 按钮），往任意方向拉大就变成可滚动的 7 条列表，实测**不轮播**；Flipboard 两个尺寸，靠组件自带的左右箭头**手动翻文章**，更新频率给「从不 / 每小时 / 每天」三档。官方文档写明 `updatePeriodMillis` **最小 30 分钟**，想在小组件里做秒级自动轮换只能自己挂闹钟，代价是耗电和被系统冻结。

**实现**：
- **一套逻辑适配多尺寸**：`slots = 组件实际高度能放下几行（行高 24dp）`，`items = 全部标题[page*slots : (page+1)*slots]`。4×2（约 110dp）显示 3 条，4×1 / 2×1（约 40dp）显示 1 条；加尺寸只需要改 `slotsFor()` 一处判断，不用为每个尺寸另写布局。布局只有一个 `widget_card.xml`，内部 `w_multi`（列表模式）与 `w_single`（单行模式）互斥显示。
- **轮换**：跟随系统 30 分钟刷新自动翻一页（零耗电、零权限）；`‹ ›` 手动翻，翻到末页回卷第一页。首次添加不轮换，避免一加就跳页。
- **呈现**：标题取英文原文（`widget.json` 里英文版条目优先），单行 `ellipsize="end"`；右侧 9sp 青色评分；列表模式顶部一行 `11-17 06:05` + `1/6` + `‹ ›`。
- **点击**：点标题 → 开 App 并滚到那条新闻（`MainActivity` 新增 `EXTRA_ANCHOR`，`onPageFinished` 里 `scrollIntoView`）；点 `‹ ›` → 只翻页不跳转；点日期/空白 → 开 App。
- **数据源（免翻墙）**：新增 `docs/widget.json`（2.5KB，含 `date/updated/total/items[t,s,a,sec]`），`build_latest.py` 每次出刊一并生成。APK 按顺序取：`dearwood777.github.io/KIKINEWS/widget.json`（与网页同域，网页能开这里就能开）→ `fastly.jsdelivr.net` 镜像 → `ghfast.top` 代理的 raw。都取不到就用本地缓存，仍没有则用安装包内置的 `assets/widget_cache.json` 快照。
- **无数据时**显示「打开 App 同步今日新闻」，点一下直接开 App。

**版本号改分段**：`1.5.000`（主.次.微），`versionCode = 主×100000 + 次×10000 + 微`（现值 150000）。以后每次小改动只递增最后一段（1.5.001、1.5.002…），只有功能性大改才动第二段；CHANGELOG 与交接文档按同一编号记录。

**产物**：`KIKINEWS-日报-v1.5.000.apk`（2,501,827 B，release 签名，证书 SHA-256 与 v1.4 一致，可直接覆盖安装）。

## 两页统一深色皮肤 + 项目交接文档（2026-11-16）

**为什么改**：同一台平板上主页是浅色、难点词汇页是深色，一明一暗很割裂——根因是主页 CSS 里写了 `@media (prefers-color-scheme: dark)`（系统是浅色就白底），而词汇页把深色写死在 `:root` 里。

- 两页改为**固定深色**，不再跟随系统明暗；共用同一套 token：`--bg:#0e1320`、`--card:#161d2b`、`--fg:#e2e8f4`、`--muted:#8b93a7`、`--line:#242d40`、`--chip:#242e42`、`--accent:#5aa6ff`、`--accent2:#4fd1c5`
- hero 渐变由亮蓝→青改为深蓝→墨绿 `#1b3f78 → #0f6560`，整页亮度降下来不刺眼
- `theme-color` 统一为 `#0e1320`（词汇页原来没有这个标签，一并补上）
- 删掉主页里所有 `prefers-color-scheme` 分支（配色、hero 各一处），词汇页 token 对齐
- **卡片底色二次微调**：`--card` 从 `#161d2b` 一路压到 `#111926`（中间试过 `#121a27` 仍偏亮）。卡片几乎与页面同色，只靠 `--line` 描边区分，标题纯白 + 轻微字距。
- **手机窄屏圆角收小**：≤520px 时卡片圆角 16 → 10、内边距收紧，标题折两行时圆角不再显得笨重（平板宽度维持原样）
- **目录药丸改版**（用户实际吐槽的是目录条目，不是卡片）：`.toc a` 原来用 `--chip`（`#242e42`）亮底 + `999px` 全圆角，标题折两行时圆弧显得笨。先压到 `#151c29` + 12px 圆角，结果和正文卡片（`#111926`，几乎与页面同色）撞色、层次消失；最终定为 `#1b2436` 底 + `#333e59` 描边 + 12px 圆角（窄屏 `#1a2334` / 10px），比正文卡片亮一档，两者重新分开。
- **英文断词与两端对齐**：英文卡片与目录条目标题加 `lang="en"`，配合 `hyphens:auto`；同时 `.toc a` 与 `.card p` 设 `text-align:justify`（`text-justify:inter-word`），窄屏折行后行尾不再空一大片。页面本身是 `lang="zh-CN"`，不加语言标记浏览器不会对英文断词。
- **目录条目改深蓝**：不再靠“亮一档”区分（会牺牲白字对比度），改为与正文卡片同等暗度的深蓝 `#0f1a2e` + `#25314b` 描边。亮度不变、白字对比度不变，靠色相与正文的近黑蓝区分开。
- **目录改等宽等高网格**（已废弃）：`.toc` 改成 grid（手机单列、≥760px 两列），每条 `min-height:46px`、满宽、`-webkit-line-clamp:2`。整齐了，但平板被压成两列、短标题被拉成长条，手机变成一条条很宽的横幅。
- **目录单行 + 慢速滚动（当前）**：用户自出方案。`.toc` 回到 `flex-wrap`，每条 `height:32px`（后续再压缩，目录从 830px 降到约 640px）、宽度随文字自适应、只允许单行；平板上一行自然并排三四个，短标题不会被拉长。手机放不下一行时**不截断**，由页尾 `tocScroll()` 按 `offsetWidth - 可用宽度` 算溢出量，分两种处理：溢出 ≤44px（一两个字）走 `nudge`（左右轻移，露出那截再移回来）；溢出更多则复制一份文字追加到条目尾部（中间留 28px 空），整条按 **25px/秒** 匀速左滚，滚到副本接上时无缝循环（`--dist` 给位移、`--dur` 给时长，最短 8s）。`resize` 后 260ms 重算并清掉旧副本；`prefers-reduced-motion` 时关闭动画。**裁剪只做在条目容器 `.toc a` 上**——早前把 `overflow:hidden` 写在 `.tt` 上，一平移就把文字自己裁没了，滚动后显示空白。
  - 第一版踩过的坑：把 `overflow:hidden` 写在 `.tt` 上，`.tt` 一平移就把自己裁掉了，滚着滚着文字整段消失、后边一片空白。现在裁剪只放在 `.toc a` 上，`.tt` 自身不裁剪。
- **同日九次微调（2026-11-17）**：目录与正文卡片撞色、候选行/摘要折行、间距过大三个问题一起收。
  - **目录改藏蓝、再压暗一档**：`#0f1a2e` → `#0d1c3a` → 最终 `#091426`，描边 `#25314b` → `#27406b` → 最终 `#1f3557`。原来和正文卡片（`#111926`）只差一点点色相，白字对比度有了但层次没了；中间那版偏亮了一档，用户反馈"暗主题就该更暗"，最后压到几乎与正文同亮度、只靠更蓝的色相和描边区分。
  - **滚动条目边缘渐隐**：`.sc` / `.nudge` 条目在左右各叠 14px 渐变（伪元素，`z-index:1`）。早前用 `mask-image` 直接做在 `.toc a` 上，会把胶囊自己的描边和圆角一起淡掉，看起来像没有边框；改成内部渐隐后描边完整保留。
  - **候选行压成一行**：`.cbtn` 从 `inline-block` 单段文字改成 `display:flex` 三段——`.l` 左、`.t` 时间、`.r` 右（`margin-left:auto`），`white-space:nowrap`。原来「从 74 条内容中筛出 · 展开全部 74 条 · 11-17 06:05」在 420px 宽下时间会掉到第二行、右边空一大块。文案同步收短为「从 N 条中筛出」/「展开全部 N 条 ›」。
  - **本期摘要压成一行**：`.summary` 改 `display:flex;align-items:center`，`padding:9px 12px`、`font-size:13.5px`；同时 `render_bilingual()` 用正则去掉摘要开头的「从 N 条内容中筛出 」前缀（英文页去 `From N items, `），避免窄屏再折。
  - **两个小容器间距 18px → 6px**：`.cands{margin:0 0 18px}` 与 `.summary{margin-bottom:16px}` 收到 6px。
  - **窄屏正文取消两端对齐**：≤520px 时 `.card p{text-align:left;hyphens:none}`。英文段落在 420px 宽下 `justify` 会把词间空隙拉得很宽（"protest in"、"critical" 后面那片大空就是这么来的），窄屏改左对齐，宽屏仍保留两端对齐 + 断词。
- **同日十次微调（报头）**：只动报头，不动正文与目录。
  - **渐变换同色系**：`linear-gradient(135deg,#1b3f78,#0f6560)` 的青色和整页冷蓝不是一个色系，手机上青色正好落在右下角，像随手抓的模板配色。改成 `160deg` 的 `#16294a → #0c1526`，蓝到近黑、不再出现青绿，整块沉下去与页面衔接。
  - **标题从两行变一行**：原来 h1 是「日期 + 主题」整串，420px 宽下必然折两行。现在日期移到报头右上角（与品牌行左右分列），h1 只放「科技 · 财经 · 国际速递」，手机 23px、宽屏 30px，永远一行。时间行相应去掉重复的日期，只留「06:05 北京时间 · 自动生成」。
  - **层级重排**：品牌行 13 → 11.5px、字距 .14 → .16em、透明度 .85 → .7；标题上 11px 下 7px（原来 6/8 是各凭感觉）；时间行 12.5 → 11.5px；药丸上边距 14 → 15px。三行文字现在有统一的递进关系。
  - **药丸去掉毛玻璃**：`rgba(255,255,255,.18)` + `backdrop-filter:blur(6px)` 原本是全页最亮的东西、比标题还抢眼，改成 6% 白底 + 1px 16% 白描边，不与标题争。
  - **整块收边**：`padding` 30/22/22 → 24/20/20（宽屏 34/26/26 → 30/26/24），底边圆角 22 → 16px。
  - **同日十一次微调（报头再收一行）**：日期与时间并到报头右上角同一行「2026-11-17 · 北京时间 06:05」，原来的独立时间行整个删掉，报头从四行降到三行；时间文案原为「06:05 北京时间」，改成中文语序的「北京时间 06:05」。渐变方向反转成上下垂直（`180deg`，`#152847 → #070d18`），顶部淡、往下越来越深，与页面本身往下变深的趋势一致；整体色阶比上一版再压暗一档。品牌行 11.5 → 11px、字距 .16 → .14em，给右侧的日期时间腾出空间。
  - **同日十二次微调（给设置按钮让位）**：APK 右上角那个原生「设置」按钮浮在 WebView 上层，正好压在报头右上角的日期时间上，时间末尾被挡。`.topline` 加 `padding-right:60px`（宽屏 66px）给按钮留位，日期行整体左移；同时收紧文字腾空间——品牌行 11 → 10.5px、字距 .14 → .12em、把「KIKI DAILY · 每日速递」中间的点两侧空格去掉（改成 `KIKI DAILY·每日速递`），日期行 11.5 → 11px、字距归零。
  - **同日十三次微调（报头三行定稿）**：报头恢复成「品牌行 / 日期时间行 / 标题」三行，不再全部挤一行。品牌行 `KIKI DAILY · 每日速递` 单独一行、11px；第二行日期 13px（宽屏 14px）正常字号，后面接 `<span class="upd">北京时间 06:05 · 自动生成</span>` 11px 小字——只有日期放大，时间和"自动生成"保持小字，这样"北京时间 06:05 自动生成"的意思完整，也不会长到压到设置按钮底下。日期与小字之间用 `margin-left:9px` 拉开（flex 的 `gap` 在纯文本节点上没吃到，改用 margin）。
  - **顺带修掉一个既有 bug**：`@media (min-width:760px)` 那块写在 `.hero` 基础规则**之前**，基础规则声明在后、同优先级直接覆盖，导致宽屏的 `.hero` padding、`h1 30px`、日期字号从来没生效过（宽屏标题一直是 23px）。现已把宽屏覆盖挪到基础规则之后。
  - **踩坑：本地补丁脚本把换行写翻倍了**。用 `open(...,'w')` 文本模式写回文件时，内容里已有的 `\r\n` 会被再翻译一次变成 `\r\r\n`，反复打补丁就 1→2→4→8 个空行，`str.replace` 的多行匹配全部失效。现在补丁脚本统一 `replace('\r','')` + `re.sub(r'\n{2,}','\n',s)` 规整，并用 `newline='\n'` 写回。


**新增交接文档**：`KIKINEWS-项目交接说明.docx`（仓库根目录）。写给"下一个接手的人或 AI"：项目目标与三条硬约束、架构与每日时序、目录职责、词表三层筛选算法与全部参数、模型复核的踩坑史（403 UA / 推理模型吃 token / Gemini 超时）、页面生成与时间的 UTC 锚点、宽屏瀑布流四版演进与当前实现（含收尾通栏与滚动保护）、深色 token、发布与核验脚本、凭据与安全、已知坑与禁忌、维护约定、接手清单、待决事项。**每次改动后要同步更新这份文档**（用户明确要求），文档里刻意不写明文密钥（仓库是 public）。

## 横屏/平板宽屏自适应（2026-11-16）

平板上竖屏正常、横屏两边大片留白（正文 `max-width:720px` 居中，在横屏里两侧各空几百像素）。只改生成脚本里的 CSS，不动 APK。

- **第一版（多栏方案，已废弃）**：`column-count:2` + `column-span:all` 让分组标题横跨整行。桌面 Edge 截图挺好看，但 iPad 上翻车：Safari 一直单列、使劲往下滑动才偶尔变成两栏；Edge/iPad 打开是两栏，切到别的 App 再切回来又退回单列，刷新才恢复。同一个 WebKit 内核在不同时刻给出不同结果 → 多栏 + spanner 在移动 Safari 上重排不稳定，不能留
- **第二版（Grid，已废弃）**：`grid-template-columns:1fr 1fr` 稳定了，但同一行的两张卡被强行等高对齐——一行里右边那条新闻很长时，短卡下面只能一直空着，等下一条才能开始
- **第三版（当前，连续瀑布流）**：还是 Grid 那版之后的问题——源码按"分组"切容器，而每组只有 3–4 张卡，其中一张特别长时，短的那栏怎么排都要差 300–500px，只能等下一组开始才有内容（iPad 实拍里那块空白就是这么来的）。现改成**全页一条连续瀑布流**：宽屏时把各组的卡片合并成一个池、隐藏分组标题（手机窄屏仍然保留分组标题），卡片依次塞进当前最短的栏，跨组连续填充，页面底部两栏基本齐平
- **第三版补丁（2026-11-16）**：
  - **结尾长卡通栏**：两栏排完后若底部高度差 ≥240px，且高栏最后一张卡本身也 ≥240px 高，就把这张卡从栏里摘出来、整行通栏放到两栏下方（最多 3 轮）。它本来就是这一栏的最后一张，阅读顺序不变，但页面不会以"一栏早早结束、另一栏拖得很长"收尾。词汇页未加这条（词卡都很短，不存在这个问题）。
  - **滑到底上滑不再跳回顶部**：根因是 iPad 上下滑动时工具栏收放会触发 `resize`，脚本每次都把卡片摘下来重建两栏，容器高度瞬间塌陷，滚动位置被浏览器夹回文档顶部。现在 `resize` 只在**宽度真的变了**时才重排（iPad 工具栏收放只改高度），重排前后还会保存/恢复 `pageYOffset`（`scrollTo` + `requestAnimationFrame` 再 `scrollTo`）。词汇页脚本同步加了这两条。
- **断点放宽到 760px**：iPad 竖/横切换时 CSS 宽度常在 780–1024 之间，原 900 阈值会漏掉一部分
- 主页 `.wrap` 720 → 1320px（≥760），hero 的负边距与标题字号同步放大；词汇页同样 1320 上限
- 顺手修 `.toc a{max-width:100%}`：极窄屏下一个过长的目录胶囊会顶出屏幕右边被裁掉
- 760px 以下（手机竖屏、APK WebView）样式与之前完全一致

## AI 复核为什么一直没跑起来（2026-11-16）

早上那次 06:00 的流水线里，词表步骤确实调了模型，但 Groq 返回 403，日志只有一行 `[warn] AI 复核跳过：HTTP Error 403`，所以那期 25 个词是纯规则层的结果。

排查（用一次性探测工作流在 Actions 里实测）：
- **Groq 在 Actions 里其实可用**：`/models` 与 `/chat/completions` 都是 200，用 curl 默认 UA 也通 → 403 不是密钥/额度问题，是 `urllib` 默认的 `Python-urllib` UA 被 Cloudflare 挡了
- 修法：所有模型请求统一带浏览器 UA；`HTTPError` 时把响应体打进日志（以前只看得到状态码）
- 另一个更隐蔽的坑：`openai/gpt-oss-20b` 是推理模型，思考过程也吃 token，`max_tokens=1200` 被推理吃光后 `content` 为空、只留 `reasoning`，JSON 就"消失"了。改为 `reasoning_effort=low` + `max_tokens=1600`，并对不认该字段的接口自动退回普通调用
- 兜底：Groq 失败时改用 `GOOGLE_API_KEY` 调 Gemini（实测该接口从 Actions 侧 60s 超时，所以基本不会生效，但不会拖垮出刊）
- 条目上限对齐 30（原来代码里切的是 24，与提示词的 30 不一致）
- 探测用的临时工作流 `probe-groq.yml` 验完即删（它跑出的 6 次失败通知是探测脚本最后一步 Gemini 超时 exit 28，与日报无关）

## 页面细节修复（2026-11-16）

**词汇页与主页的历史修复对齐**
- **撇号空隙**：主页 11-14 修过"中文页面里弯引号被交中文字体渲染、撇号前撑出全角空隙"，词汇页当时没跟上。现 `build_vocab.py` 复用 `build_latest.plain_quotes()`，写盘前整体把 `’ ‘` 换成 ASCII，两页行为一致
- **长词不撑破卡片**：`.w` 加 `overflow-wrap:break-word`
- **词汇页页脚**：`KIKI · 难点词汇 · 释义取自开源词库 ECDICT 与公开词典接口` → `KIKI 难点词汇 · 释义取自开源词库`（原文太长会折到第二行，末尾"口"字单独掉行），居中沿用既有 `footer{text-align:center}`
- **主页链接双重转义**：RSS 链接里自带 `&amp;`，`html.escape` 后再转一次变成 `&amp;amp;`，页面上显示 `…RSS&amp;at_campaign=rss`，查询参数也被打成 `amp;at_campaign`。新增 `esc_url()`（先 `html.unescape` 再 `html.escape`），替换标题链接、英文页链接、原文链接、候选面板链接、`inline_md()` 里的 href 共 6 处

**横向体检（把修过的问题在另一处复检一遍）**
- 已确认两边一致：日期按 `candidates.json` 的 UTC 锚点换算北京时间（重建不漂移）、标题不用 `text-wrap:balance`、页面上没有"点 🔊 跟读"提示、"未调用模型"、"deployed on" 这类多余文案
- 本轮同时纠正一次误覆盖：手工发布的词汇页是上一期（11-15）稿，已按当期 `2026-11-15-summary-en.md`（页面日期 11-16）重建为 25 词

## v1.4（2026-11-15）

**APK**
- 设置菜单改为**从设置按钮位置向下弹出的下拉菜单**（PopupMenu，靠右对齐），不再用居中对话框挡住正文
- 改用**正式签名（release）**构建：新建专用密钥 `CN=KIKINEWS`（RSA 2048，有效期 10000 天）
  - 密钥存本机 `D:\AI\KIKINEWS\keystore\kiki-release.jks`，配置写 `android/keystore.properties`
  - 两者都进 `.gitignore`，不进公开仓库；缺配置时自动回退 debug 签名，别人 clone 下来能直接编译
  - **注意**：与 v1.3 的 debug 签名不同，装 v1.4 前必须先卸载旧版
  - 体积 3.15 MB → 2.49 MB（release 去掉调试信息）
- versionCode 4 → 5，versionName 1.3 → 1.4

## v1.3（2026-11-15）

**APK**
- 设置菜单默认只保留 4 项：重新加载、强制刷新（清缓存）、回到顶部、调整字号
- **长按设置键满 6 秒**才解锁「在浏览器中打开」「复制日报链接」：按住 6 秒弹提示「已解锁高级选项，松手后显示」，松手后菜单出现这两项；提前松手恢复正常菜单
  - 目的：这两项是自用调试项，分享给别人时默认不暴露
  - 触摸事件计时（ACTION_DOWN 起定时器，ACTION_UP 判定，ACTION_CANCEL 复位），`onDestroy` 清 Handler
- 菜单项改为按名称分发，不再硬编码下标，避免以后增删项错位
- versionCode 3 → 4，versionName 1.2 → 1.3

## 页面与流水线（2026-11-13 ~ 11-15）

**词表过滤第五版（2026-11-16 凌晨，加一次 AI 复核，规则漏掉的由模型补）**
- 之前是"规则先筛、模型后看"，会有一个隐患：**规则误判的词，模型根本看不到**（被当成简单派生词或 CEFR 标成 B2 其实很难的词，就直接被丢掉）
- 改成**规则 + 模型并集**：`ai_review()` 让模型独立读一遍正文，自己挑"C1 读者会卡住"的单词与固定说法（`clamp down`/`shore up`/`hawk` 这类），规则结果与模型结果取并集
  - 模型挑中的词即使规则判它"简单"也保留；模型说不出中文义的不收
  - 模型给的短语直接进短语卡层
- 成本：输入约 1.5k token（正文截前 7000 字符）+ 输出约 600 token，单次约 2k，占 Groq 免费 200k/天 的 1%
- **补词按难度排，不按词频**：模型按"最卡住→较容易"返回，取前 12 个最难的；原来的词频升序是反着的（最能读懂的排最前）
- 两道保险：① A1–B2 等级仍排除（`crucial` 模型也可能挑，但读者确实认识）② 词频排名 5000 以内不补（`amid`/`bypass` 这种 C1 标签里的高频词会被拦下）
- 用桩数据验证过：`crucial`（B2）、`amid`（frq 3825）都被拦下，`insolvency`、`overhaul` 正常补入；`clamp down` 短语卡正常出
- 失败不影响日报：没 key、超时、JSON 解析失败都只打一行 warn 后跳过，页面照常用规则结果生成
- 开关：`VOCAB_AI=0` 可关掉复核（本地调试用）
- 工作流：`Build vocabulary page` 步骤补 `GROQ_API_KEY` 环境变量

**词表过滤第四版（2026-11-16 凌晨，接入 CEFR 等级，从"词频近似"改成"直接判级"）**
- 接入开源 CEFR 词表 `openlanguageprofiles/olp-en-cefrj`（CC-BY）：
  - `data/cefrj.csv` CEFR-J A1–B2（7,801 词条）
  - `data/octanove.csv` Octanove C1–C2
  - 共 8,845 条去重词条，`load_cefr()` 建词→等级映射（同一词多档取低档）
- `is_hard()` 新增第一判据：**命中 A1/A2/B1/B2 直接排除**。这比词频可靠得多——`crucial`=B2、`password`=B1、`thousand`=A2、`ecosystem`=B1、`unauthorized`=B2，都直接出局
- C1/C2 不做"直接收录"，只当参考：`amid`/`bypass`/`regulatory` 也在 C1/C2 表里，对 C1 读者仍太常见，继续走词频判据
- 词表未收录（8,845 条覆盖不到的技术/法律生词）时，仍按原词频 + 派生 + 常用词表兜底
- 工作流同步：`Cache English-Chinese dictionary` 增加两个 CSV 的 cache path；构建步骤新增两个 `curl`（缺文件才下，走 raw.githubusercontent，文件小、秒级）
- 本期实测（11-14 正文）：14 词，与第三版所选一致，说明旧规则本就筛对，CEFR 只是把"crucial 这类漏网"的口子彻底堵死

**词表过滤第三版（2026-11-15 深夜，针对"熟词生义列的都是初中词"）**
- 熟词生义层加**难度门槛**：只收词频排名 3000 之后的词，`hold / hit / source / official / drive / seat` 这类初中词即使有新闻义也不再占版面
- 新增**新闻短语层** `data/news_phrases.json`（82 条）：`clamp down`、`push back`、`shore up`、`water down`、`rule out`、`double down`、`dial back` 这类"每个词都认识、整句仍读不懂"的说法
  - 支持动词变形（clamped down / stepping up / pushed back），单独成卡，标"短语 / 新闻常见说法"，带原文语境高亮
  - 与熟词生义一样是纯查表，零 token
- 效果：本期 14 个词（12 生僻 + `hike` 加息、`curb` 遏制两个新闻义），短语层本期正文未命中（这期英文正文里没有这些说法）

- 第一版只按词频判难度，仍是粗筛：`crucial / password / scanner / timeline / thousands / crypto` 这类照样进表
- 加**简单派生词过滤**：去掉前缀（un- / re- / non- / pre- / over- …）与后缀（-ly / -ness / -tion / -er / -able …）最多两层，只要能落回一个"本来就会"的词，就不算生词
  - 例：`unconfirmed ← confirm`、`negotiator ← negotiate`、`redesign ← design`、`governorship ← govern`
- 词库兜底表再扩一批日常/科技词（`password / scanner / timeline / ecosystem / metadata / app` 及品牌名）
- 六级词按"新闻常见书面语"标准保留：真生僻的留，词频靠前的（C1 早该认识的）仍排除
- **新增"熟词生义"层**：ECDICT 自带的领域标注（[法] / [医] / [经]）质量太差（`idea` 被标成 [医]"观念"），自动判断会灌进噪声，因此改用人工维护的 `data/news_senses.json`
  - 命中即出卡，卡片上单独标一条"新闻义"（如 `hold` 执政、`source` 消息人士、`drive` 外交攻势、`seat` 议席）
  - 运行时纯查表，零 token；新词直接往 JSON 里加，不用改代码
- 顶部说明改为「今日超纲词汇（已排除四六级等低于 C1 的高频词）。」
- 效果：同一期正文抽样，词表 40 → 12 个纯生僻词 + 6 个熟词生义词

**难点词汇页（新功能，全程不耗 AI token）**
- 新增 `scripts/build_vocab.py`：用离线词典 ECDICT（76 万词条）查表 + 规则筛选，从当天英文正文挑超纲词
- 首页加「难点词汇 ›」入口（仅当词汇页存在时渲染），词汇页顶部有「‹ 返回今日速递」
- 卡片内容：音标、词性、中英释义、英文例句、原文语境句（高亮原词）、点按发音、稀有度星标
- 发音走有道公开接口（`dict.youdao.com/dictvoice`，WebView 里系统 TTS 基本无效），失败再回退 TTS
- 英文释义/例句来自 Wiktionary 公开接口，结果缓存到 `data/vocab_enrich.json`（进 Actions 缓存）
- 工作流新增两步：`Cache English-Chinese dictionary` + `Build vocabulary page (no AI)`，排在日报页生成之前

**词表准确性（多轮返工）**
- 出词表**先还原原形再判定难度**：用词库 `exchange` 的 `0:原形` 标记做变形映射，`countries/parties/policies` 按 `country/party/policy` 判定，不再把极常见词当生僻词
- 一词多原形（`does → do / doe`）按词频挑最常见的那个
- 难度判定同时用 `frq`（当代语料）与 `bnc`（英式语料）两套词频，任一套显示为常用词即排除
- 新增 C1/专八必备词兜底表（`demo / emails / millions / backup / notification / dashboard / startup` 等词库排名偏宽松的高频词）
- 排除含连字符的复合词（`front-end / real-time`）
- 音标兜底：词条缺音标时回查原形、再查公开词典接口，仍查不到的不出卡（列出来却不会读没有意义）
- 语境匹配纳入该词族的所有变形（`underpinned / countermeasures / reshaping`），并以命中处为中心裁剪，保证高亮不被截断
- 效果：63 词（20 个缺音标）→ 24 词（音标 24/24、语境 24/24）

**页面修复**
- 撇号字距：`lang="zh-CN"` 下浏览器把弯引号 `’` 当中文字体标点渲染，字形带全角侧边距 → 生成时统一转成 ASCII 单引号
- 标题右侧大片留白：`text-wrap: balance` 主动把多行调等长 → 改 `text-wrap: pretty`
- 标题里 `Jensen\!` 的 Markdown 反斜杠漏到页面 → `clean_text` 清转义
- 页面署名改为「由 AI 筛选与总结，可能存在偏差，请以原文为准。」
- 词汇页删掉「点 🔊 跟读发音…」提示句

**日期与时间（两轮修复）**
- 第一轮：Horizon 用 UTC 日期给本期命名，北京时间早上读到的这期日期会差一天 → 显示日期 +1
- 第二轮：重建页面时用「构建时刻」推算，导致日期退回前一天、时间写成重建时间 → 改为**以 `candidates.json` 的 UTC `generated_at` 为唯一锚点**换算北京时间，重建不再漂移；`latest.json` 的 UTC 时间保持不变（guard 依赖它）

**候选面板**
- 修复 `HttpUrl` 不可 JSON 序列化导致候选从未落盘（`src/orchestrator.py` 改 `str(item.url)`）
- 页面拒绝渲染非当日候选，避免旧列表冒充本次候选

**流水线**
- guard 改为「距上次发布小时数 < 12 则跳过」，修掉跨 UTC 零点导致次日整轮被跳过的问题
- 定时保持 `0 22 * * *` + 兜底 `0 23 * * *`（UTC）= 北京 06:00 / 07:00
- 外部定时器 cron-job.org 每天 05:55（北京时间）POST dispatch 作为兜底

## v1.2（2026-11-12）

**APK**
- 改为沉浸式全屏：隐藏状态栏（时间 / WiFi / 电量）和导航栏，从屏幕边缘滑动可临时唤出，松手自动收起
- 设置菜单去掉「更新说明」，版本记录统一放在仓库 `CHANGELOG.md` / `README.md`
- 构建产物的文件名带版本号（如 `KIKINEWS-日报-v1.2.apk`），便于区分旧包

**页面**
- 中文稿实际仍是英文原文的条目不再输出「中文」块，避免「标着中文、内容是英文」
- 顶部 pills 增加真实双语统计（如「共 16 条精选 · 双语 11 条」）
- 候选面板在无评分时如实标注「本次抓取候选 N 条（未评分）· 抓取时间」

## v1.1（2026-11-12）

**页面**
- 每条新闻卡片新增「🔗 原文链接」，点击直达原文
- 新增「展开全部候选」面板：展开后是本次抓到的全部候选标题 + 原文链接，纯前端渲染，不消耗任何 AI 额度
- 移除顶部「英文在上 · 中文在下」提示
- 移除页脚「deployed on GitHub Pages」
- 品牌统一为 KIKI

**流水线**
- 分析阶段输入以标题为主（每条 500 字符），enrich 阶段 800 字符，token 消耗约为原来的 1/5
- 模型切到 `openai/gpt-oss-20b`，max_tokens 768
- 4 个 profile 阈值统一降到 2.0，避免「抓 70 条只出 3 条」
- 新增 `world-news`（国际要闻）分类，覆盖地缘政治、冲突、选举、灾害、司法、科学突破
- 采集面收敛：HN 10 条 / Google News 10 / GDELT 10 / 4 个 RSS / Telegram 1 频道，12 小时窗口
- 429 退避重试上限压到 2 次、最长 45 秒
- 新增 `scripts/collect_candidates_only.py`：无 AI 的纯采集脚本，保证候选面板始终有数据

**APK**
- 设置菜单去掉「修改日报地址」
- 新增：强制刷新（清缓存）、回到顶部、调整字号、复制日报链接、更新说明
- 「在浏览器中打开」「重新加载」保留
- versionCode 1 → 2，versionName 1.0 → 1.1

## v1.0（2026-11-11）

- 首个可用版本：GitHub Actions 定时抓取 → GitHub Pages → Android WebView
- 中文 / 英文同卡片上下对照
- 品牌改为 KIKI 每日速递
