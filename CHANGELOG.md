# 更新记录

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
