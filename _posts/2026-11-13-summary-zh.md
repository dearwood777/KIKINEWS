---
layout: default
title: "Horizon Summary: 2026-11-13 (ZH)"
date: 2026-11-13
lang: zh
---

> 从 91 条内容中筛选出 16 条重要资讯。

---

**科技新闻**
1. [Rust 1.100 发布：永远类型、定制分配器与 Cargo 新功能](#item-tech-news-1) ⭐️ 9.0/10
2. [Jensen Huang is out at Nvidia — who is Colette Kress, his interim replacement?](#item-tech-news-2) ⭐️ 9.0/10
3. [NVIDIA CEO 黄仁勋辞职，CFO 克雷斯临时接任](#item-tech-news-3) ⭐️ 9.0/10
4. [Jensen Huang resigns](#item-tech-news-4) ⭐️ 8.0/10
5. [I&\#x27;m making LLMs work on small and old devices](#item-tech-news-5) ⭐️ 8.0/10
6. [Google’s latest Search upgrade promises better answers to your most complicated questions](#item-tech-news-6) ⭐️ 8.0/10
7. [Jensen Huang’s exit puts Nvidia’s support for open source in question](#item-tech-news-7) ⭐️ 8.0/10
8. [Hugging Face CEO vows to keep fighting for open source AI after Jensen Huang’s exit](#item-tech-news-8) ⭐️ 8.0/10

**国际要闻**
1. [普京警告美方俄方将针对乌克兰驻军](#item-world-news-1) ⭐️ 9.0/10
2. [援助是苏丹数百万人的唯一希望，WFP 首席警告资金削减加剧饥饿危机](#item-world-news-2) ⭐️ 9.0/10
3. [US envoys meet Zelensky in Dublin after talks with Putin in Moscow](#item-world-news-3) ⭐️ 8.0/10
4. [Democrat Scott Colom makes history as Mississippi&\#x27;s first black senator since 19th Century](#item-world-news-4) ⭐️ 8.0/10
5. [Millions of Ebola dollars missing with staff unpaid while virus spreads, charity says](#item-world-news-5) ⭐️ 8.0/10
6. [The rise and fall of Jensen Huang - how the tech superstar became mired in scandal](#item-world-news-6) ⭐️ 8.0/10
7. [Jensen Huang has resigned, what&\#x27;s next for Nvidia?](#item-world-news-7) ⭐️ 8.0/10
8. [China rules out hosting Cop33 climate summit in 2028](#item-world-news-8) ⭐️ 8.0/10

---

## 科技新闻

<a id="item-tech-news-1"></a>
### [Rust 1.100 发布：永远类型、定制分配器与 Cargo 新功能](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/) ⭐️ 9.0/10

Rust 1.100 版正式发布，核心改动包括：永远类型（\`\!\`）正式稳定；支持自定义内存分配器；引入依赖冷却（dependency cooldowns）配置，限制 Cargo 解析最近发布的版本；Cargo 现在会警告未使用的依赖；并新增多项 API 如 \`bool::toggle\`、\`Box::map\`、\`str::trim\_prefix\`/\`trim\_suffix\`、\`Path::trim\_prefix\`。

hackernews · mbStavola · 11月12日 18:39 · [社区讨论](https://news.ycombinator.com/item?id=50472038)

**「背景」** Rust 1.100 于 2026 年 11 月发布，继承了之前的 1.90 系列，继续推进语言和 Cargo 的功能。此前，never 类型（\!）在 1.90 之前仅为实验性，已在 1.100 中正式稳定；Cargo 通过 RFC 3923 实现了依赖冷却（dependency cooldowns），旨在减少供应链攻击窗口；同时新增了 cargo::unused\_dependencies lint，帮助开发者发现未使用的依赖。

**「影响」** 开发者现在可以直接使用永远类型来表达无返回值的函数，利用自定义分配器实现更细粒度的内存管理；依赖冷却功能帮助团队控制依赖升级节奏；Cargo 的未使用依赖警告促使项目保持依赖清洁，减少不必要的包。

**「社区讨论」** 社区成员对新功能表现出热情，指出博客未提及的实用 API（如 \`bool::toggle\`、\`Box::map\` 等），并对 DropGuard 的实现表示赞赏。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://releases.rs/docs/1.100.0/">1.100.0 | Rust Changelogs - releases.rs</a></li>
<li><a href="https://byteiota.com/rust-1100-cargo-cooldowns/">Rust 1.100: Cargo Dependency Cooldowns Are Here — Enable Them</a></li>
<li><a href="https://www.linkedin.com/posts/rustjobs-dev_%F0%9D%90%91%F0%9D%90%AE%F0%9D%90%AC%F0%9D%90%AD%F0%9D%90%AC-%F0%9D%90%8D%F0%9D%90%9E%F0%9D%90%AF%F0%9D%90%9E%F0%9D%90%AB-%F0%9D%90%93%F0%9D%90%B2%F0%9D%90%A9%F0%9D%90%9E-%F0%9D%90%8D%F0%9D%90%9E%F0%9D%90%9A%F0%9D%90%AB%F0%9D%90%A2%F0%9D%90%A7%F0%9D%90%A0-activity-7470805631520788481-DKi8">Rust Never Type Stabilization Nears Completion | LinkedIn</a></li>

</ul>
</details>

**标签**: `#Rust`, `#Language Features`, `#Cargo`, `#Systems Programming`

---

<a id="item-tech-news-2"></a>
### [Jensen Huang is out at Nvidia — who is Colette Kress, his interim replacement?](https://techcrunch.com/2026/11/12/jensen-huang-is-out-at-nvidia-who-is-colette-kress-his-interim-replacement/) ⭐️ 9.0/10

Jensen Huang’s immediate resignation from Nvidia signals a significant shift in a key AI hardware leader.

rss · TechCrunch · 11月12日 15:37

**标签**: `#Nvidia`, `#CEO resignation`, `#AI hardware`, `#leadership change`

---

<a id="item-tech-news-3"></a>
### [NVIDIA CEO 黄仁勋辞职，CFO 克雷斯临时接任](https://nvidianews.nvidia.com/news/nvidia-announces-ceo-transition) ⭐️ 9.0/10

英伟达宣布黄仁勋立即辞去总裁、CEO 及董事职务，现任执行副总裁兼 CFO 科莱特·克雷斯被任命为临时 CEO 并继续兼任 CFO。董事会已启动永久继任者搜寻，并任命 Harvey C. Jones 为首位董事会主席。公司表示运营、客户承诺和产品路线不会中断，第三季度财报仍按原计划于 11 月 17 日发布。

telegram · zaihuapd · 11月12日 13:52

**「NVIDIA CEO 背景」** NVIDIA 自 1993 年成立以来，黄仁勋一直担任总裁兼 CEO，领导公司成为 AI 硬件领军者。

**「影响」** 投资者和合作伙伴将需要关注董事会对永久继任者的搜寻进展，以评估对公司治理和长期战略的潜在影响。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.globenewswire.com/news-release/2026/11/12/3401635/0/en/nvidia-announces-ceo-transition.html">NVIDIA Announces CEO Transition | GlobeNewswire News Room</a></li>

</ul>
</details>

**标签**: `#NVIDIA`, `#CEO transition`, `#AI hardware`, `#industry leadership`

---

<a id="item-tech-news-4"></a>
### [Jensen Huang resigns](https://apnews.com/article/nvidia-megaspeed-china-singapore-huang-5403f152a601cf82ce939f1d24fffa0f) ⭐️ 8.0/10

Nvidia CEO resignation is a high‑impact industry event with broad implications for AI and technology markets.

hackernews · lldb · 11月12日 13:52 · [社区讨论](https://news.ycombinator.com/item?id=50467087)

**标签**: `#Nvidia`, `#AI`, `#Leadership`, `#ExportControls`, `#IndustryImpact`

---

<a id="item-tech-news-5"></a>
### [I&\#x27;m making LLMs work on small and old devices](https://github.com/hyperionaidev/smolmaxxing/) ⭐️ 8.0/10

Open‑source effort shows 16B LLMs running on 1GB‑memory devices, offering impactful edge‑AI insights.

hackernews · mrashad74 · 11月12日 15:23 · [社区讨论](https://news.ycombinator.com/item?id=50468888)

**标签**: `#edge AI`, `#LLM optimization`, `#low-resource inference`, `#open source`, `#hardware acceleration`

---

<a id="item-tech-news-6"></a>
### [Google’s latest Search upgrade promises better answers to your most complicated questions](https://techcrunch.com/2026/11/12/googles-latest-search-upgrade-promises-better-answers-to-your-most-complicated-questions/) ⭐️ 8.0/10

Google’s Gemini 4 Hydrogen model promises a major upgrade to Search, offering faster, more accurate answers to complex queries.

rss · TechCrunch · 11月12日 19:27

**标签**: `#AI`, `#Search`, `#Google`, `#Gemini`, `#NLP`

---

<a id="item-tech-news-7"></a>
### [Jensen Huang’s exit puts Nvidia’s support for open source in question](https://techcrunch.com/2026/11/12/jensen-huangs-exit-puts-nvidias-support-for-open-source-in-question/) ⭐️ 8.0/10

Nvidia CEO Jensen Huang’s resignation raises concerns about the company’s future support for open‑source AI amid national‑security scrutiny.

rss · TechCrunch · 11月12日 18:39

**标签**: `#open-source`, `#AI`, `#Nvidia`, `#executive resignation`, `#national security`

---

<a id="item-tech-news-8"></a>
### [Hugging Face CEO vows to keep fighting for open source AI after Jensen Huang’s exit](https://techcrunch.com/2026/11/12/hugging-face-ceo-vows-to-keep-fighting-for-open-source-ai-after-jensen-huangs-exit/) ⭐️ 8.0/10

Hugging Face CEO reacts to Nvidia’s acquisition and Jensen Huang’s exit, underscoring the impact on open‑source AI.

rss · TechCrunch · 11月12日 17:36

**标签**: `#Nvidia`, `#Hugging Face`, `#Open Source AI`, `#Acquisition`, `#Leadership`

---

## 国际要闻

<a id="item-world-news-1"></a>
### [普京警告美方俄方将针对乌克兰驻军](https://www.theguardian.com/world/2026/nov/12/vladimir-putin-russia-target-foreign-troops-ukraine-elon-musk-starlink) ⭐️ 9.0/10

在克里姆林宫与美国代表的会谈中，普京警告美国谈判者，俄罗斯将针对部署在乌克兰的任何外国部队。与此同时，乌克兰军方再次遭遇埃隆·马斯克的 Starlink 卫星服务中断。普京在会谈中坚持不放松领土要求，并拒绝接受外国维和部队。

rss · The Guardian World · 11月12日 22:26

**「俄乌冲突背景」** 自 2022 年 9 月 30 日，俄罗斯宣布吞并顿涅茨克、赫尔松、卢甘斯克和扎波罗热四个乌克兰地区，并在这些地区设立占领行政机构，试图将其纳入俄罗斯政治体系。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Russian_annexation_of_Donetsk,_Kherson,_Luhansk_and_Zaporizhzhia_oblasts">Russian annexation of Donetsk, Kherson, Luhansk and ...</a></li>
<li><a href="https://www.osw.waw.pl/en/publikacje/analyses/2022-10-03/russia-announces-annexation-four-regions-ukraine">Russia announces the annexation of four regions of Ukraine</a></li>

</ul>
</details>

**标签**: `#Russia`, `#Ukraine`, `#United States`, `#Diplomacy`, `#Military`

---

<a id="item-world-news-2"></a>
### [援助是苏丹数百万人的唯一希望，WFP 首席警告资金削减加剧饥饿危机](https://news.google.com/rss/articles/CBMiV0FVX3lxTE9Sb255ek9CX0dfdjdIWUNqWDNzbUFKYWVjV1BQcDhXYXRkMV9kcjlaRG9EMGx1bWtBS1M4RmJCNW00N0d3MmJNa19DTm51S3c3cmZsLUVMcw?oc=5) ⭐️ 9.0/10

联合国世界粮食计划署（WFP）首席警告，苏丹数百万民众的唯一生存希望是援助。 他指出，随着国际捐助资金的削减，饥饿危机正迅速恶化。 目前尚不清楚未来援助水平将如何调整，导致人道主义需求持续上升。

google\_news · UN News · 11月12日 18:37

**「背景：世界粮食计划署援助面临削减」** 世界粮食计划署（WFP）一直为苏丹提供紧急粮食援助，但因资金短缺，计划在 2026 年底前削减约 80 万人接受援助，并警告苏丹正面临全球最大饥饿危机，援助物资可能在两个月内耗尽。

**「粮食援助削减导致数千万人面临饥饿风险」** 世界粮食计划署援助削减使苏丹内部的粮食供应在两个月内可能耗尽，导致超过 2100 万民众面临急性饥饿，伴随营养不良和药品短缺等严重后果。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.wfp.org/emergencies/sudan">Risk of Famine in Sudan | World Food Programme</a></li>
<li><a href="https://indonesianpost.com/2026/02/15/un-report-21-million-sudanese-face-acute-hunger-wfp-funding-crunch/">More than 21 million people in Sudan at risk of hunger as WFP aid...</a></li>
<li><a href="https://allafrica.com/stories/202610230024.html">Sudan Hunger Crisis Deepens As Aid Cuts Collide... - allAfrica.com</a></li>
<li><a href="https://indonesianpost.com/2026/02/15/un-report-21-million-sudanese-face-acute-hunger-wfp-funding-crunch/">More than 21 million people in Sudan at risk of hunger as WFP aid...</a></li>

</ul>
</details>

**标签**: `#Sudan`, `#Humanitarian crisis`, `#WFP`, `#Aid`, `#Hunger`

---

<a id="item-world-news-3"></a>
### [US envoys meet Zelensky in Dublin after talks with Putin in Moscow](https://www.bbc.co.uk/news/articles/cwrkgmymk55zo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

US envoys Jared Kushner and Steve Witkoff met with Russian President Vladimir Putin and then Ukraine’s President Volodymyr Zelensky, agreeing on a new round of trilateral talks amid ongoing war discussions.

rss · BBC World · 11月12日 21:00

**标签**: `#diplomacy`, `#Ukraine war`, `#US-Russia relations`, `#trilateral talks`, `#Zelensky`

---

<a id="item-world-news-4"></a>
### [Democrat Scott Colom makes history as Mississippi&\#x27;s first black senator since 19th Century](https://www.bbc.co.uk/news/articles/cw7vppyr80eeo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Scott Colom, a Democrat, won Mississippi&\#x27;s U.S. Senate seat, becoming the state&\#x27;s first black senator since the 1800s.

rss · BBC World · 11月12日 12:56

**标签**: `#US politics`, `#elections`, `#diversity`, `#Mississippi`, `#Senate`

---

<a id="item-world-news-5"></a>
### [Millions of Ebola dollars missing with staff unpaid while virus spreads, charity says](https://www.bbc.co.uk/news/articles/cx98757ymm6zo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

MSF warns that millions of Ebola relief funds are missing and frontline staff in the DRC are unpaid, jeopardizing the outbreak response.

rss · BBC World · 11月12日 15:18

**标签**: `#Ebola`, `#DRC`, `#MSF`, `#funding`, `#public health`

---

<a id="item-world-news-6"></a>
### [The rise and fall of Jensen Huang - how the tech superstar became mired in scandal](https://www.bbc.co.uk/news/articles/cmze750zg0jeo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Nvidia’s founder Jensen Huang resigns after a scandal, a development that could reshape the company and affect the global technology landscape.

rss · BBC World · 11月12日 17:11

**标签**: `#technology`, `#business`, `#scandal`, `#Nvidia`, `#Jensen Huang`

---

<a id="item-world-news-7"></a>
### [Jensen Huang has resigned, what&\#x27;s next for Nvidia?](https://www.bbc.co.uk/news/videos/cmdx1r99kp9wo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Jensen Huang steps down as Nvidia CEO, triggering an interim leadership change and a brief stock market dip.

rss · BBC World · 11月12日 19:33

**标签**: `#Nvidia`, `#CEO resignation`, `#tech industry`, `#stock market`, `#business`

---

<a id="item-world-news-8"></a>
### [China rules out hosting Cop33 climate summit in 2028](https://www.theguardian.com/environment/2026/nov/12/china-rules-out-hosting-cop33-climate-summit-in-2028) ⭐️ 8.0/10

China has declined to host the 2028 COP33 climate summit, opening the bid to other Asian nations and altering the dynamics of global climate diplomacy.

rss · The Guardian World · 11月12日 22:00

**标签**: `#Climate Change`, `#COP33`, `#China`, `#International Relations`

---