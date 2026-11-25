---
layout: default
title: "Horizon Summary: 2026-11-25 (ZH)"
date: 2026-11-25
lang: zh
---

> 从 85 条内容中筛选出 16 条重要资讯。

---

**科技新闻**
1. [FCC 批准 SpaceX 在太空部署 AI 数据中心](#item-tech-news-1) ⭐️ 9.0/10
2. [1Password 2026 侵入事件：源代码泄露与恶意代码推送](#item-tech-news-2) ⭐️ 8.0/10
3. [I checked Clojure&\#x27;s core with Lean and found unreported bugs](#item-tech-news-3) ⭐️ 8.0/10
4. [Nvidia GPU 走私案：黄仁勋仍需回答的问题](#item-tech-news-4) ⭐️ 8.0/10
5. [Minecraft 曝高危 RCE 漏洞，Java 版 1.20.5 起全版本受影响](#item-tech-news-5) ⭐️ 8.0/10
6. [DOJ accuses former cyber executive of defrauding ransomware victims by secretly paying hackers](#item-tech-news-6) ⭐️ 7.0/10
7. [Character.AI’s plan to auction off users’ private chats challenged by state AGs](#item-tech-news-7) ⭐️ 7.0/10

**国际要闻**
1. [俄罗斯官方数据显示乌克兰战争已失去近 50 万士兵](#item-world-news-1) ⭐️ 9.0/10
2. [美国对包括中国在内的多国征收新关税](#item-world-news-2) ⭐️ 8.0/10
3. [Israeli judges recommend dropping most serious charges against Netanyahu](#item-world-news-3) ⭐️ 8.0/10
4. [Huawei found guilty of stealing US trade secrets but acquitted of racketeering](#item-world-news-4) ⭐️ 8.0/10
5. [China misusing Interpol to target dissidents, says leading UK lawyer](#item-world-news-5) ⭐️ 8.0/10
6. [德国总理警告俄罗斯追求的不仅是乌克兰](#item-world-news-6) ⭐️ 8.0/10
7. [全球首次出现连续六天温度高于工业化前 2°C](#item-world-news-7) ⭐️ 8.0/10
8. [中国如何在禁令下获得英伟达 AI 芯片](#item-world-news-8) ⭐️ 8.0/10
9. [Images of asteroid targeted to test Earth&\#x27;s defences reveal stadium-sized crater](#item-world-news-9) ⭐️ 7.0/10

---

## 科技新闻

<a id="item-tech-news-1"></a>
### [FCC 批准 SpaceX 在太空部署 AI 数据中心](https://techcrunch.com/2026/11/25/fcc-approves-spacex-plan-to-put-ai-data-centers-in-space/) ⭐️ 9.0/10

美国联邦通信委员会（FCC）授予 SpaceX 在轨道上部署多达 100 万颗卫星的条件批准，以支持其在太空建造 AI 数据中心的计划。该批准使 SpaceX 能够继续推进其星际数据中心业务，但须满足 FCC 设定的技术和环境条件。尽管亚马逊、Viasat 和美国天文学会对轨道碎片、频谱干扰和环境影响提出异议，FCC 仍认为申请符合监管要求。

rss · TechCrunch · 11月25日 20:56

**「先前的提案」** SpaceX 此前提出了在轨部署多达 100 万颗卫星数据中心的计划，并向联邦通信委员会提交了相关申请。

**「影响」** SpaceX 现在可以开始规划和部署其卫星星座，但必须满足 FCC 的条件，包括碎片管理、频谱使用和环境评估，否则可能面临监管处罚。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://news.google.com/stories/CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pwM2NXM0VCRlljQXdZZUZFaTl5Z0FQAQ?hl=en-NA&amp;gl=NA&amp;ceid=NA:en">SpaceX proposes constellation of one million orbital data centers ...</a></li>
<li><a href="https://cointelegraph.com/news/fcc-authorizes-spacex-1m-satellites-orbital-ai-data-centers">SpaceX Wins FCC Approval for Orbital AI Computing Network</a></li>

</ul>
</details>

**标签**: `#AI infrastructure`, `#satellite technology`, `#regulatory approval`, `#SpaceX`, `#FCC`

---

<a id="item-tech-news-2"></a>
### [1Password 2026 侵入事件：源代码泄露与恶意代码推送](https://1password.com/blog/update-on-nov-2026-security-incident) ⭐️ 8.0/10

1Password 在 2026 年 11 月 19 日确认一次内部系统入侵，攻击者利用员工的 GitHub 账户推送恶意代码到公司内部服务器，随后下载了部分客户信息（姓名和登录邮箱）。但未获取加密的密码库或其他机密。

hackernews · lxhrstn · 11月25日 17:18 · [社区讨论](https://news.ycombinator.com/item?id=50644817)

**「背景」** 1Password 将源代码托管在 GitHub 上，员工账户被攻击后可直接推送代码至内部部署环境。

**「影响」** 受影响的客户仅泄露了姓名和邮箱，未暴露加密密码库；但泄露的联系信息可能被用于钓鱼攻击。

**「社区讨论」** 评论者指出此类攻击凸显 SaaS 代码推送安全的重要性，建议加强分支保护和禁止自合并，以防止恶意代码被部署。

**标签**: `#security`, `#SaaS`, `#incident`, `#source-code`, `#password-manager`

---

<a id="item-tech-news-3"></a>
### [I checked Clojure&\#x27;s core with Lean and found unreported bugs](https://s.conao3.com/blog/2026/e4f733) ⭐️ 8.0/10

Clojure’s core library was formally verified with Lean, revealing unreported bugs and highlighting the potential of theorem proving for mainstream languages.

hackernews · encyclopedism · 11月25日 14:56 · [社区讨论](https://news.ycombinator.com/item?id=50642939)

**标签**: `#formal verification`, `#Clojure`, `#Lean`, `#program correctness`, `#software engineering`

---

<a id="item-tech-news-4"></a>
### [Nvidia GPU 走私案：黄仁勋仍需回答的问题](https://techcrunch.com/2026/11/25/the-questions-jensen-huang-and-nvidia-will-still-have-to-answer-about-megaspeed/) ⭐️ 8.0/10

Nvidia 仍面临关于其先进 GPU 被客户 Megaspeed 走私至中国的指控，违反美国出口管制。调查重点是公司是否知晓芯片最终去向，以及黄仁勋与 Megaspeed 高管的关系是否影响其对 Megaspeed 保障的信任。黄仁勋重返 CEO 并未解决这些疑问，联邦检察官、加州总检察长和国会仍在继续追问。

rss · TechCrunch · 11月25日 13:00

**「背景」** Megaspeed 是一家总部位于新加坡的云计算服务商，前身为 7Road International，2015 年成立，2023 年被中国投资者收购并更名为 Megaspeed。该公司因涉嫌将 Nvidia 高端 GPU 通过其数据中心转运至中国而受到调查，进一步说明了本次事件的背景。

**「影响」** 若调查确认违规，Nvidia 可能面临美国政府的制裁、出口禁令或罚款，并可能被迫暂停向中国的出口，影响其 AI 硬件供应链和股价。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Megaspeed">Megaspeed - Wikipedia</a></li>
<li><a href="https://www.briefs.co/news/singapore-cloud-firm-megaspeed-faces-scrutiny-over-alleged-n/">Singapore Cloud Firm Megaspeed Probed Over Nvidia Chips</a></li>

</ul>
</details>

**标签**: `#Nvidia`, `#ExportControls`, `#AIHardware`, `#China`, `#Regulation`

---

<a id="item-tech-news-5"></a>
### [Minecraft 曝高危 RCE 漏洞，Java 版 1.20.5 起全版本受影响](https://github.com/bikini/minecraft2shell) ⭐️ 8.0/10

Critical RCE vulnerability in Minecraft Java Edition versions 1.20.5–1.21.10 and 26.1–26.4, with community‑issued temporary fixes and mitigation advice.

telegram · zaihuapd · 11月25日 12:46

**标签**: `#security`, `#vulnerability`, `#Minecraft`, `#RCE`, `#gaming`

---

<a id="item-tech-news-6"></a>
### [DOJ accuses former cyber executive of defrauding ransomware victims by secretly paying hackers](https://techcrunch.com/2026/11/25/doj-accuses-former-cyber-executive-of-defrauding-ransomware-victims-by-secretly-paying-hackers/) ⭐️ 7.0/10

DOJ indicts former ransomware recovery firm executive for fraudulently defrauding victims.

rss · TechCrunch · 11月25日 17:36

**标签**: `#cybersecurity`, `#ransomware`, `#legal`, `#fraud`

---

<a id="item-tech-news-7"></a>
### [Character.AI’s plan to auction off users’ private chats challenged by state AGs](https://techcrunch.com/2026/11/25/state-ags-fight-character-ais-plan-to-auction-off-users-private-chats/) ⭐️ 7.0/10

A coalition of 42 state attorneys general is blocking Character.AI’s plan to auction users’ private chats amid bankruptcy, underscoring growing legal and privacy scrutiny of AI companies.

rss · TechCrunch · 11月25日 17:35

**标签**: `#AI`, `#Data Privacy`, `#Legal`, `#Regulation`, `#Industry Impact`

---

## 国际要闻

<a id="item-world-news-1"></a>
### [俄罗斯官方数据显示乌克兰战争已失去近 50 万士兵](https://www.bbc.co.uk/news/articles/cmx27g533zwyo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 9.0/10

俄罗斯官方统计显示，自 2022 年乌克兰战争开始以来，已死亡 490,334 名俄罗斯士兵。该数字来自俄罗斯统计局泄露的数据，BBC 已对其进行分析。

rss · BBC World · 11月25日 12:21

**「背景说明」** 俄罗斯在 2022 年对乌克兰发动全面入侵，原本预计冲突短暂，但已持续近五年。

**「影响」** 这一数字凸显战争对俄罗斯军队的人力成本，可能影响其军事部署和国内舆论。

**标签**: `#Russia-Ukraine conflict`, `#military casualties`, `#war statistics`, `#human cost`, `#international relations`

---

<a id="item-world-news-2"></a>
### [美国对包括中国在内的多国征收新关税](https://www.bbc.co.uk/news/articles/c893r9ke5p97o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

美国总统唐纳德·特朗普政府宣布对包括中国、欧盟及 12 个其他司法管辖区在内的多国征收新关税。中国将面临最高 40%的关税，越南最高 35%，其余国家则为 20%或 25%。这些关税预计将于明年生效。

rss · BBC World · 11月25日 16:21

**「前期“解放日”关税案」** 在 2025 年 4 月，特朗普总统宣布“解放日”关税，随后最高法院裁定其非法，促使白宫对其他国家的贸易做法展开调查。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Liberation_Day_tariffs">Liberation Day tariffs - Wikipedia</a></li>
<li><a href="https://www.bbc.com/news/live/cqglr4708r85t">US tariffs : New proposals on EU, China, and other trade... - BBC News</a></li>
<li><a href="https://www.theguardian.com/world/2026/feb/25/wednesday-briefing-is-the-tide-turning-against-trump-on-tariffs">Wednesday briefing: Is the tide turning against Trump on tariffs ?</a></li>

</ul>
</details>

**标签**: `#US trade policy`, `#tariffs`, `#China`, `#global trade`, `#US‑China relations`

---

<a id="item-world-news-3"></a>
### [Israeli judges recommend dropping most serious charges against Netanyahu](https://www.bbc.co.uk/news/articles/cxj05mv723r2o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Israeli judges advised prosecutors to drop the most serious bribery charges against Netanyahu, potentially boosting his political survival.

rss · BBC World · 11月25日 19:47

**标签**: `#Israel`, `#Netanyahu`, `#Judiciary`, `#Politics`, `#Legal`

---

<a id="item-world-news-4"></a>
### [Huawei found guilty of stealing US trade secrets but acquitted of racketeering](https://www.bbc.co.uk/news/articles/cmy49ngydqzpo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

A US court found Huawei guilty of stealing trade secrets but acquitted it of racketeering.

rss · BBC World · 11月25日 10:52

**标签**: `#Huawei`, `#US court`, `#trade secrets`, `#tech industry`, `#China-US relations`

---

<a id="item-world-news-5"></a>
### [China misusing Interpol to target dissidents, says leading UK lawyer](https://www.theguardian.com/world/2026/nov/25/china-misusing-interpol-target-dissidents-uk-lawyer) ⭐️ 8.0/10

China is accused of abusing Interpol’s red notices to silence dissidents, a claim made by a leading UK lawyer amid Hong Kong’s hosting of Interpol’s general assembly.

rss · The Guardian World · 11月25日 11:00

**标签**: `#Interpol`, `#China`, `#Human rights`, `#Dissidents`, `#Hong Kong`

---

<a id="item-world-news-6"></a>
### [德国总理警告俄罗斯追求的不仅是乌克兰](https://www.theguardian.com/world/live/2026/nov/25/ukraine-russia-energy-strikes-mark-rutte-donald-trump-friedrich-merz-germany-latest-news-updates) ⭐️ 8.0/10

德国总理弗里德里希·梅尔茨于 2026 年 11 月 25 日在德国发表演讲，称俄罗斯的野心超越乌克兰，并形容莫斯科的行动正在“以大规模升级”。演讲中，他指出俄罗斯正对乌克兰进行大规模军事行动。与此同时，有报道称两组黑客在上月访问俄罗斯主要统计数据库，发现一份包含 1100 万份死亡证明的缓存，显示自 2022 年以来俄罗斯在乌克兰的损失近 50 万，其中约 1000 人自杀。

rss · The Guardian World · 11月25日 16:20

**「德国总理警告俄罗斯野心超越乌克兰」** 德国总理弗里德里希·梅尔茨在国会发表讲话，警告俄罗斯的野心超越乌克兰。此前，俄罗斯自 2022 年入侵乌克兰以来一直在欧洲各地加剧紧张局势，德国在乌克兰危机中一直是欧盟的重要支持者。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.theguardian.com/world/live/2026/nov/25/ukraine-russia-energy-strikes-mark-rutte-donald-trump-friedrich-merz-germany-latest-news-updates?page=with:block-6b06b5648f0814f45d3cf909">‘ Russia wants more than Ukraine ,’ Germany’s Merz ... | The Guardian</a></li>
<li><a href="https://timesofindia.indiatimes.com/world/europe/russia-wants-more-than-ukraine-german-chancellor-merz-sounds-alarm-over-moscows-ambitions-across-europe/articleshow/136159209.cms">&#x27; Russia wants more than Ukraine &#x27;: German Chancellor Merz sounds...</a></li>

</ul>
</details>

**标签**: `#Germany`, `#Russia`, `#Ukraine`, `#International Relations`, `#Political Speech`

---

<a id="item-world-news-7"></a>
### [全球首次出现连续六天温度高于工业化前 2°C](https://news.google.com/rss/articles/CBMiuwFBVV95cUxPR0p3bVRkTGZLb0pMa3lYVjR0VFdtSld3VmRVN0FTa0FpT2MtMDRLUXBIYmpRc0NGRktDTEp4bVcxQnY3amZMbC0tdVdnVkcwU3JpaUlKenBaMlY3MXU5Z3lfcUF2Q0owa1RGdEFXbU1Rb1pRdmRpb3ZQNGNSZnJmS1hFdHRZeUNGRzdnN1lhb0gySS0tTjdNcVNoQk8yTGIyNi0xRmVNTmQtemxFSUY1enVqUHR0LVp0N1lV?oc=5) ⭐️ 8.0/10

2026 年 11 月 25 日，全球首次连续六天温度超过工业化前水平 2°C。该记录由全球气候监测机构确认，涉及全球平均温度。

google\_news · The Guardian · 11月25日 21:25

**「全球温度基准线背景」** 全球表面温度相对于 1850-1900 年平均值的基准线进行测量，巴黎协定将 1.5°C 和 2°C 视为关键阈值。此前，全球温度已偶尔超过 2°C，但从未连续六天保持在此水平。

**「影响」** 此记录表明全球气候变暖趋势加速，可能促使各国加强减排承诺。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.theguardian.com/environment/2026/nov/25/world-six-consecutive-days-2c-above-preindustrial-levels-first-time">World has six consecutive days 2C above preindustrial levels ...</a></li>
<li><a href="https://climate.copernicus.eu/why-do-we-keep-talking-about-15degc-and-2degc-above-pre-industrial-era">Why do we keep talking about 1.5°C and 2°C above the pre ...</a></li>

</ul>
</details>

**标签**: `#climate change`, `#temperature record`, `#global warming`, `#environmental science`, `#world news`

---

<a id="item-world-news-8"></a>
### [中国如何在禁令下获得英伟达 AI 芯片](https://news.google.com/rss/articles/CBMiywFBVV95cUxOX1lSZWZmNXhBWDlaellZdnhpb0hEUFd6Q010dDZlUjBQZjV0Skplb0ozbUtwWEF1VVR0YkpHQXJGYjZlQl9HcE5jdzhEdExrTTAxTHVjcUpvTFBBY3FUMTVUOEcyWTRRNzJUMUw3djROQjB3OTRucGd2akVHNExDOFJSbkticW4xZjBpVTBqdERxbzlKWmdFSG9ERmNnZS1XZThQYXc2OEhIVEdaUVgzeTRiODBwcXRXWUpFVEtCTkZDS0Z1NmtSV0xJQQ?oc=5) ⭐️ 8.0/10

美国出口管制规定禁止向中国出口英伟达 AI 芯片；据报道，中国已获得这些芯片，违反规定。事件发生在 2026 年 11 月，具体渠道未公开。

google\_news · U.S. News &amp; World Report · 11月25日 19:37

**「背景」** 美国对向中国出口 Nvidia AI 芯片实施出口管制，限制其高端型号。此前，中国军方已寻求获取这些芯片以提升 AI 武器能力。

**「影响」** 此事件可能削弱美国在 AI 芯片市场的主导地位，并加剧两国在技术竞争中的紧张关系。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.reuters.com/world/china/how-china-got-access-nvidias-ai-chips-despite-rules-stop-them-2026-11-25/">How China got access to Nvidia&#x27;s AI chips despite rules to ...</a></li>
<li><a href="https://www.reuters.com/world/china/china-seeks-advanced-nvidia-chips-ai-weapons-despite-us-curbs-report-says-2026-11-18/">China seeks advanced Nvidia chips for AI weapons despite US ...</a></li>

</ul>
</details>

**标签**: `#China`, `#Nvidia`, `#AI chips`, `#export controls`, `#US-China relations`

---

<a id="item-world-news-9"></a>
### [Images of asteroid targeted to test Earth&\#x27;s defences reveal stadium-sized crater](https://www.bbc.co.uk/news/articles/cw8dv112r5gmo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 7.0/10

NASA’s DART mission impact on Dimorphos produced a stadium‑sized crater, confirming the effectiveness of kinetic‑impactor planetary defense.

rss · BBC World · 11月25日 17:30

**标签**: `#planetary defense`, `#asteroid impact`, `#NASA`, `#ESA`, `#space science`

---