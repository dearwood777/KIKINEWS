---
layout: default
title: "Horizon Summary: 2026-11-23 (ZH)"
date: 2026-11-23
lang: zh
---

> 从 80 条内容中筛选出 16 条重要资讯。

---

**科技新闻**
1. [CrowdStrike 收购 Zscaler 43.9 亿美元](#item-tech-news-1) ⭐️ 9.0/10
2. [GLM‑5.4：首次循环 Transformer 提升代码生成](#item-tech-news-2) ⭐️ 8.0/10
3. [Amazon snaps up Decart’s AI optimization tech for $7.5B as it prepares to sell Trainium chips](#item-tech-news-3) ⭐️ 8.0/10

**国际要闻**
1. [The FIFA World Cup is returning to the U.S. - Deseret News](#item-world-news-1) ⭐️ 10.0/10
2. [民主党夺得自 1992 年以来最大众议院多数席位](#item-world-news-2) ⭐️ 9.0/10
3. [COP31 峰会崩溃：气候谈判为何破裂？](#item-world-news-3) ⭐️ 9.0/10
4. [欧盟公布第 22 轮制裁 目标削弱俄方战争融资](#item-world-news-4) ⭐️ 9.0/10
5. [Trump administration deported US citizen to Mexico, DoJ admits in court](#item-world-news-5) ⭐️ 8.0/10
6. [Leaked data shows more than 1,000 Russian military suicides during Ukraine war](#item-world-news-6) ⭐️ 8.0/10
7. [US Imposes Sanctions on Dozens Linked to Iran&\#x27;s Shadow Banking Networks - U.S. News &amp; World Report](#item-world-news-7) ⭐️ 8.0/10
8. [德国认真对待俄罗斯可能将核武器送入太空的报告](#item-world-news-8) ⭐️ 8.0/10
9. [What strike on Russian ship in Libya says about spread of Ukraine war](#item-world-news-9) ⭐️ 7.0/10
10. [Israeli attacks have turned Gaza into &\#x27;toxic wasteland&\#x27;, Oxfam says](#item-world-news-10) ⭐️ 7.0/10
11. [India pledges $1.6bn to Nepal in reset of ties](#item-world-news-11) ⭐️ 7.0/10
12. [Lucy Powell to visit China to promote UK education weeks after MI5 warning](#item-world-news-12) ⭐️ 7.0/10

**财经新闻**
1. [Fed&\#x27;s John Williams indicates higher interest rates likely &\#x27;over time&\#x27; to address inflation](#item-finance-news-1) ⭐️ 8.0/10

---

## 科技新闻

<a id="item-tech-news-1"></a>
### [CrowdStrike 收购 Zscaler 43.9 亿美元](https://techcrunch.com/2026/11/23/crowdstrike-to-acquire-zscaler-for-44-billion/) ⭐️ 9.0/10

CrowdStrike 宣布以 43.9 亿美元全股交易收购 Zscaler，双方称此举将形成“最大单一可寻址市场”，并为 AI 时代的网络安全布局奠定基础。Zscaler 拥有约 8,000 家企业客户，提供零信任云安全技术；CrowdStrike 以终端防护为主。

rss · TechCrunch · 11月23日 16:20

**「背景」** CrowdStrike 是一家成立于 2011 年的网络安全公司，提供基于云的端点和工作负载保护，并在 2019 年上市。Zscaler 是总部位于加州圣何塞的云安全公司，向约 8,000 家企业提供零信任网络访问解决方案，零信任技术要求每次访问内部资源时都进行身份验证，以防止凭证被盗。

**「影响」** 此次收购将促使 CrowdStrike 将 Zscaler 的零信任云安全与其终端防护平台整合，预计为企业客户提供更完整的端到端安全解决方案，并可能在未来几个月内调整产品组合与定价。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/CrowdStrike">CrowdStrike - Wikipedia</a></li>
<li><a href="https://www.crowdstrike.com/en-us/">CrowdStrike : We Stop Breaches with AI-native Cybersecurity</a></li>
<li><a href="https://www.crowdstrike.com/en-us/about-us/">About CrowdStrike : Our Story, Mission, &amp; Team | CrowdStrike</a></li>

</ul>
</details>

**标签**: `#cybersecurity`, `#acquisition`, `#cloud`, `#zero‑trust`, `#AI`

---

<a id="item-tech-news-2"></a>
### [GLM‑5.4：首次循环 Transformer 提升代码生成](https://z.ai/blog/glm-5.4) ⭐️ 8.0/10

Zhipu AI 发布 GLM‑5.4，首次引入循环 Transformer 架构，专为代码生成优化。该模型仅在 Z.ai 的 Coding Plan API 计划下可用，OpenRouter 及常规计划尚未接入。循环 Transformer 通过在一次推理中多次复用同一层权重，显著降低了内存带宽瓶颈，提升了代码生成效率。

hackernews · foohis · 11月23日 10:06 · [社区讨论](https://news.ycombinator.com/item?id=50609685)

**「循环 Transformer 先前概念」** 循环 Transformer 是一种参数高效的设计，通过多次重复使用同一 Transformer 块来模拟更深层网络的推理能力。此前已有研究（如 EmergentMind 的文章）阐述了权重共享与递归迭代的实现方式，并在实验中证明其可在保持参数量不变的情况下提升算法推理性能。

**「影响」** 使用 Z.ai Coding Plan 的开发者可在推理时获得更快的响应时间，尤其在需要多层权重复用的代码生成任务中。

**「社区讨论」** 评论者赞赏 Zhipu 的透明度，并指出循环 Transformer 能解决传统 Transformer 的内存带宽瓶颈；有人提到中文模型在“马拉松思考”模式下仍显慢。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://anyrouter.dev/model/z-ai/glm-5.4">GLM - 5 . 4 · Zhipu AI · pricing &amp; API · AnyRouter</a></li>
<li><a href="https://www.emergentmind.com/topics/looped-transformer-architecture">Looped Transformer Architecture - emergentmind.com</a></li>

</ul>
</details>

**标签**: `#LLM`, `#loop transformer`, `#Zhipu`, `#AI architecture`, `#software engineering`

---

<a id="item-tech-news-3"></a>
### [Amazon snaps up Decart’s AI optimization tech for $7.5B as it prepares to sell Trainium chips](https://techcrunch.com/2026/11/23/amazon-snaps-up-decarts-ai-optimization-tech-for-7-5b-as-it-prepares-to-sell-trainium-chips/) ⭐️ 8.0/10

Amazon’s purchase of Decart’s AI optimization technology signals a major shift in AI infrastructure, potentially enhancing model performance on Nvidia, Amazon, and Google hardware.

rss · TechCrunch · 11月23日 17:14

**标签**: `#AI optimization`, `#cloud computing`, `#hardware`, `#Amazon`

---

## 国际要闻

<a id="item-world-news-1"></a>
### [The FIFA World Cup is returning to the U.S. - Deseret News](https://news.google.com/rss/articles/CBMinAFBVV95cUxPa1pjcW9rOGt3TTA5SjgxYmRNU3Jvam96TjNhdnF6SEs4MC1KUHNKN2k2bHRpYW9lRHdMeGd2TlA5RjdLSXZVTkZETG5zQ0VnUFp5X0VORHM4VmZXbHBjZ21lUmNYYWpKVWoxSE94OGR5aFFFelNUMzFjbVhvcTNaM0JTeHhndEU0ZFRfYmRodU9kU0YtVXdhYUJyb1U?oc=5) ⭐️ 10.0/10

The FIFA World Cup is scheduled to return to the United States, marking a major international sporting event.

google\_news · Deseret News · 11月23日 19:34

**标签**: `#sports`, `#world cup`, `#fifa`, `#us`, `#international`

---

<a id="item-world-news-2"></a>
### [民主党夺得自 1992 年以来最大众议院多数席位](https://www.bbc.co.uk/news/articles/c6vg29g7dlyno?at_medium=RSS&amp;at_campaign=rss) ⭐️ 9.0/10

2026 年中期选举中，民主党候选人查克·哈伯德在北卡罗来纳州击败共和党议员弗吉尼亚·福克斯，票数差距为 330 票，已计入 99%的选票。此举使民主党在众议院席位至少达到 258 席，超过共和党 173 席，四个选区仍未计票。

rss · BBC World · 11月23日 13:02

**「背景信息」** 1992 年，克林顿当选总统，民主党在众议院获得 258 席，成为自那时以来的最高席位数。

**「影响」** 民主党在众议院获得多数席位，增强了其推进议程的能力。

**标签**: `#US politics`, `#Elections`, `#House of Representatives`, `#North Carolina`, `#Democratic Party`

---

<a id="item-world-news-3"></a>
### [COP31 峰会崩溃：气候谈判为何破裂？](https://www.theguardian.com/news/audio/2026/nov/23/cop31-collapses-why-did-climate-talks-fall-apart-the-latest) ⭐️ 9.0/10

在 2026 年 11 月的 COP31 气候峰会上，来自各国的代表未能达成关键协议，这是 17 年来首次出现此类失败。峰会由土耳其和澳大利亚共同主持，原计划通过一项协议为气候行动和对脆弱国家的融资注入紧迫性。然而，关于化石燃料和对受气候危机影响国家的支持的僵局导致协议未能达成。

rss · The Guardian World · 11月23日 17:19

**「COP31 先前的背景」** COP31 气候峰会在土耳其举行，联合土耳其和澳大利亚共同主持，成为历史上最长的联合国气候峰会，持续超过 45 小时。峰会旨在制定一项约束性协议，推动气候行动并为脆弱国家提供融资支持。

**「直接影响」** 峰会的失败意味着全球未能制定新的具有约束力的气候协议，标志着全球气候政策和国际合作的重大倒退。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.nytimes.com/2026/11/22/climate/cop31-climate-summit-ends-climate.html">COP 31 Talks Collapse in Turkey in a Clash Over Fossil Fuels</a></li>
<li><a href="https://www.independent.co.uk/climate-change/news/cop31-summit-deal-turkey-failure-fossil-fuels-b3089390.html">Cop 31 ends with no deal as longest climate summit ever collapses ...</a></li>
<li><a href="https://www.youtube.com/watch?v=i8vSLgXNCQk">The worst COP ever? Climate talks collapse in chaos... - YouTube</a></li>

</ul>
</details>

**标签**: `#climate change`, `#COP31`, `#international relations`, `#environment`, `#policy`

---

<a id="item-world-news-4"></a>
### [欧盟公布第 22 轮制裁 目标削弱俄方战争融资](https://www.theguardian.com/world/live/2026/nov/23/russia-ukraine-war-zelenskyy-libya-benghazi-drone-attack-ship-merkury-un-nato-europe-latest-news-updates) ⭐️ 9.0/10

欧盟委员会主席乌尔苏拉·冯德莱恩于 2026 年 11 月 23 日宣布第 22 轮制裁包，针对俄罗斯以限制其战争融资。该包共包含多项措施，旨在削弱俄罗斯在乌克兰冲突中的经济支持。

rss · The Guardian World · 11月23日 16:42

**「欧盟第 22 轮制裁背景」** 自 2022 年俄乌冲突爆发以来，欧盟已陆续推出多轮制裁，旨在限制俄罗斯的金融资源并削弱其战争能力。此次第 22 轮制裁继续沿用此前的策略，重点打击与武器制造、能源出口和金融服务相关的俄罗斯实体。

**标签**: `#EU sanctions`, `#Russia`, `#Ukraine war`, `#international policy`, `#economic impact`

---

<a id="item-world-news-5"></a>
### [Trump administration deported US citizen to Mexico, DoJ admits in court](https://www.theguardian.com/us-news/2026/nov/23/trump-administration-deported-citizen-mexico) ⭐️ 8.0/10

The Trump administration admitted in federal court that it deported a U.S. citizen to Mexico after mistakenly identifying him as undocumented.

rss · The Guardian World · 11月23日 11:00

**标签**: `#Wrongful Deportation`, `#Immigration`, `#US-Mexico`, `#Trump Administration`, `#Legal`

---

<a id="item-world-news-6"></a>
### [Leaked data shows more than 1,000 Russian military suicides during Ukraine war](https://www.theguardian.com/world/2026/nov/23/leaked-data-shows-more-than-1000-russian-military-suicides-during-ukraine-war) ⭐️ 8.0/10

Leaked death certificates reveal more than 1,000 Russian soldiers died by suicide during the Ukraine conflict.

rss · The Guardian World · 11月23日 16:00

**标签**: `#Russia-Ukraine conflict`, `#war casualties`, `#leaked data`, `#military suicides`, `#humanitarian impact`

---

<a id="item-world-news-7"></a>
### [US Imposes Sanctions on Dozens Linked to Iran&\#x27;s Shadow Banking Networks - U.S. News &amp; World Report](https://news.google.com/rss/articles/CBMiwgFBVV95cUxPVFZCbGVlWUNUdWFkYU9Uc2JLM0Y0M1RyMnlfZnZuZDVTNS1aZnhsNDJjUzJBcEhjcG9YRk15QnpBV2xNeG9yZWNERzdrMktNZ2dfanJaa2NxYkczSVF1WHR0Y3lrQjBsaHhtU09XaUpnektuYl8wSWdFdUVPZ01UNkFzRmZuWkZqVnZ1MTNzczVBSFpVd0NaRjRYU0VEcHdIWGptZ05XaG5PTWxzazdUMVYwQ2ZKT3FzTEtuZm1Tb1dJZw?oc=5) ⭐️ 8.0/10

The U.S. has imposed sanctions on dozens of people and entities linked to Iran’s shadow banking networks.

google\_news · U.S. News &amp; World Report · 11月23日 19:38

**标签**: `#sanctions`, `#Iran`, `#shadow banking`, `#U.S. foreign policy`, `#international finance`

---

<a id="item-world-news-8"></a>
### [德国认真对待俄罗斯可能将核武器送入太空的报告](https://news.google.com/rss/articles/CBMimgFBVV95cUxOOUtWdVJPaUZZOXBmZ0VhUzJTaWNKQVNwUFhzMmVaRWY3MW9ITXVnbWpMd2h0cmdyTEtmaDloN2E1VmNQd056ZTMwSVFPazRtSWtLZ1NXa1NBMUkzQ3VwNjJUajFhZ3B3UXlGNnF3WWhNNUxHelhoZUkzWS1XZERMZ25lSDcxcHVYZHBUbmJlb0FHaGlNSFU1eXF3?oc=5) ⭐️ 8.0/10

德国政府正认真对待有关俄罗斯可能计划将核武器送入太空的报道。德国外交部表示已收到情报并正在评估。俄罗斯方面尚未作出回应，相关计划是否真实仍在调查中。

google\_news · The Guardian · 11月23日 20:26

**「俄罗斯核武与太空背景」** 俄罗斯继承苏联核武库，拥有发射火箭的技术和经验。自 1991 年独立以来，俄罗斯继续发展其太空计划，并在国际上保持核武器大国地位。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://en.m.wikipedia.org/wiki/Russia">Russia - Wikipedia</a></li>
<li><a href="https://en.m.wikipedia.org/wiki/History_of_Russia">History of Russia - Wikipedia</a></li>
<li><a href="https://www.britannica.com/place/Russia">Russia | History, Flag, Population, Map, President, &amp; Facts ...</a></li>

</ul>
</details>

**标签**: `#Russia`, `#nuclear weapons`, `#space`, `#Germany`, `#international security`

---

<a id="item-world-news-9"></a>
### [What strike on Russian ship in Libya says about spread of Ukraine war](https://www.bbc.co.uk/news/articles/cm894p88jzxpo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 7.0/10

Ukraine coordinated a night‑time attack on a Russian corvette in Benghazi, Libya, demonstrating the conflict’s reach beyond its borders.

rss · BBC World · 11月23日 20:48

**标签**: `#Ukraine war`, `#Russia`, `#Libya`, `#military strike`, `#international conflict`

---

<a id="item-world-news-10"></a>
### [Israeli attacks have turned Gaza into &\#x27;toxic wasteland&\#x27;, Oxfam says](https://www.bbc.co.uk/news/articles/c8r4gzzxvxl3o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 7.0/10

Oxfam reports that Israeli attacks have turned Gaza into a toxic wasteland, with 99% of the territory showing environmental contamination.

rss · BBC World · 11月23日 17:07

**标签**: `#Gaza`, `#Oxfam`, `#environmental contamination`, `#war`, `#humanitarian`

---

<a id="item-world-news-11"></a>
### [India pledges $1.6bn to Nepal in reset of ties](https://www.bbc.co.uk/news/articles/cwx2ervemj4ko?at_medium=RSS&amp;at_campaign=rss) ⭐️ 7.0/10

India pledged $1.6 billion to Nepal as part of a reset of bilateral ties.

rss · BBC World · 11月23日 13:39

**标签**: `#India`, `#NePAL`, `#Diplomacy`, `#Economic Aid`, `#South Asia`

---

<a id="item-world-news-12"></a>
### [Lucy Powell to visit China to promote UK education weeks after MI5 warning](https://www.theguardian.com/politics/2026/nov/23/uk-visit-china-lucy-powell-education-mi5-universities-warning) ⭐️ 7.0/10

UK education secretary Lucy Powell is traveling to Beijing to promote UK education after MI5 warned universities about Chinese interference.

rss · The Guardian World · 11月23日 16:42

**标签**: `#UK-China relations`, `#education`, `#MI5`, `#academic security`, `#diplomacy`

---

## 财经新闻

<a id="item-finance-news-1"></a>
### [Fed&\#x27;s John Williams indicates higher interest rates likely &\#x27;over time&\#x27; to address inflation](https://www.cnbc.com/2026/11/23/john-williams-fed-inflation-rate-hikes.html) ⭐️ 8.0/10

Fed official John Williams signals likely future rate hikes to bring inflation toward the 2% target.

rss · CNBC Finance · 11月23日 21:02

**标签**: `#Monetary Policy`, `#Inflation`, `#Federal Reserve`, `#Interest Rates`, `#Economic Outlook`

---