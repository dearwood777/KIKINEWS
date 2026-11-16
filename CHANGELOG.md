# 更新记录

## 横屏/平板宽屏自适应（2026-11-16）

平板上竖屏正常、横屏两边大片留白（正文 `max-width:720px` 居中，在 1554×1080 的横屏里两侧各空约 400px）。只改生成脚本里的 CSS，不动 APK。

- **主页**：`@media (min-width:900px)` 把 `.wrap` 720 → 1140px、正文走 `column-count:2`（`.summary`/`.toc`/`.group` 用 `column-span:all` 横跨整行，`.card` 用 `break-inside:avoid` 不许拆断），hero 负边距与标题、meta 字号同步放大；`(min-width:1400px)` 再把 `.wrap` 拉到 1320px
- **踩到的坑**：第一版把分栏规则挂在 `section[data-lang]` 上，线上截图里容器是变宽了但正文仍单列——`render_bilingual()` 实际返回的是纯拼接，页面里根本没有 `<section>`（那段是 `render_lang()` 的死代码）。改为给正文包一层 `<div class="flow">`，分栏才真正生效
- **词汇页**：词卡包进 `<div class="cards">`，900px 起两栏、1400px 起三栏，`.wrap` 720 → 1120/1300px
- 900px 以下（手机竖屏、APK WebView）样式与之前完全一致

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
