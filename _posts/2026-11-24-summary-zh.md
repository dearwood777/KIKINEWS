---
layout: default
title: "Horizon Summary: 2026-11-24 (ZH)"
date: 2026-11-24
lang: zh
---

> 从 76 条内容中筛选出 16 条重要资讯。

---

**科技新闻**
1. [vCenter 再曝 9.8 分免鉴权漏洞，几天前刚被零日利用](#item-tech-news-1) ⭐️ 10.0/10
2. [Amazon 收购 Decart 以软件缩小与 Nvidia 的硅差距](#item-tech-news-2) ⭐️ 9.0/10
3. [Check Point HFS PRNG Exploit Campaign](#item-tech-news-3) ⭐️ 8.0/10
4. [Even the best AI agents struggle with everyday life](#item-tech-news-4) ⭐️ 8.0/10
5. [UK warns AI-driven cyberattacks are exposing years of weak security](#item-tech-news-5) ⭐️ 8.0/10
6. [Uber 与 Nuro 开始 Lucid 机器人出租车无人驾驶测试](#item-tech-news-6) ⭐️ 8.0/10
7. [Why a Crusoe investor is betting on solar and batteries to power future AI data centers](#item-tech-news-7) ⭐️ 8.0/10
8. [FCC 提议对外星座运营商实施对等限制](#item-tech-news-8) ⭐️ 7.0/10

**国际要闻**
1. [Democrat Victoria Broderick unseats eight-term Republican incumbent in Tennessee to win election](#item-world-news-1) ⭐️ 9.0/10
2. [Huawei found guilty of stealing trade secrets but acquitted of racketeering](#item-world-news-2) ⭐️ 8.0/10
3. [俄罗斯在马里冲突中损失逾 300 名士兵](#item-world-news-3) ⭐️ 8.0/10
4. [EU to impose cap on Chinese hybrid EV imports next month](#item-world-news-4) ⭐️ 8.0/10
5. [Schumer 指控黄仁勋违反出口管制](#item-world-news-5) ⭐️ 8.0/10
6. [前法国总统萨科齐与妻子将受审](#item-world-news-6) ⭐️ 7.0/10
7. [Israeli air strike kills Hamas internal security chief in Gaza](#item-world-news-7) ⭐️ 7.0/10

**财经新闻**
1. [美联储威廉姆斯暗示未来加息以抑制通胀](#item-finance-news-1) ⭐️ 8.0/10

---

## 科技新闻

<a id="item-tech-news-1"></a>
### [vCenter 再曝 9.8 分免鉴权漏洞，几天前刚被零日利用](https://thehackernews.com/2026/11/vmware-vcenter-hit-by-another-critical.html) ⭐️ 10.0/10

A 9.8‑rated zero‑day authentication bypass in VMware vCenter has been publicly disclosed and exploited, posing a major security risk for virtualization environments.

telegram · zaihuapd · 11月24日 14:50

**标签**: `#security`, `#vulnerability`, `#VMware`, `#zero-day`

---

<a id="item-tech-news-2"></a>
### [Amazon 收购 Decart 以软件缩小与 Nvidia 的硅差距](https://techcrunch.com/2026/11/24/amazons-decart-acquisition-is-a-bet-on-using-software-to-narrow-the-gap-with-nvidia-in-the-ai-chip-race/) ⭐️ 9.0/10

亚马逊以 75 亿美元收购了 AI 模型优化初创公司 Decart，获得其针对非 Nvidia 芯片的优化技术和团队。此次收购使亚马逊能够在自有硬件上更高效地运行 AI 模型，缩小与 Nvidia 在硅层面的差距。该技术尚未公开发布，整合进亚马逊生态的时间表仍未确定。

rss · TechCrunch · 11月24日 15:51

**「背景」** Decart 是一家以色列 AI 初创公司，专注于实时世界模型和优化技术，使 AI 模型能在非 Nvidia 芯片上高效运行。Amazon 以 75 亿美元收购其技术，旨在提升云端 AI 基础设施并缩小与 Nvidia 的硅芯差距。

**「影响」** 亚马逊开发者将能够使用 Decart 的优化工具，将模型迁移到自家或第三方非 Nvidia 芯片，从而降低对 Nvidia GPU 的依赖并可能降低推理成本。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://techcrunch.com/2026/11/23/amazon-snaps-up-decarts-ai-optimization-tech-for-7-5b-as-it-prepares-to-sell-trainium-chips/">Amazon snaps up Decart &#x27;s AI optimization tech for... | TechCrunch</a></li>
<li><a href="https://en.wikipedia.org/wiki/Decart">Decart - Wikipedia</a></li>

</ul>
</details>

**标签**: `#AI hardware`, `#software optimization`, `#Amazon`, `#Nvidia`, `#Decart`

---

<a id="item-tech-news-3"></a>
### [Check Point HFS PRNG Exploit Campaign](https://www.greynoise.io/blog/check-point-security-management-servers-intrusion-campaign) ⭐️ 8.0/10

Check Point 的 HFS 服务器因 PRNG 漏洞（CVE‑2026‑16232）被攻击者利用 Math.random 重建 V8 PRNG 状态，恢复签名密钥并伪造管理员会话 cookie，已在多家组织中展开入侵活动。

hackernews · louiereederson · 11月24日 16:32 · [社区讨论](https://news.ycombinator.com/item?id=50630594)

**「先前的身份验证绕过漏洞」** Check Point 的 SmartConsole 在 2026 年 7 月公开披露了一个身份验证绕过漏洞（CVE‑2026‑16232），攻击者可通过应用程序登录令牌获得完整管理员权限。该漏洞已被修补并成为安全更新的重点。新的入侵活动利用 HFS 服务器中的 PRNG 漏洞来伪造管理员会话 cookie，进一步扩大了攻击面。

**「影响」** 受影响的组织必须立即修补 HFS 服务器或实施会话签名密钥轮换，以防止未经授权的管理员访问。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://nvd.nist.gov/vuln/detail/cve-2026-16232">NVD-CVE-2026-16232</a></li>
<li><a href="https://support.checkpoint.com/results/sk/sk185169">sk185169 - CVE-2026-16232 - Authentication bypass with ...</a></li>
<li><a href="https://www.sentinelone.com/vulnerability-database/cve-2026-16232/">CVE-2026-16232: Check Point SmartConsole Auth Bypass</a></li>

</ul>
</details>

**标签**: `#security`, `#vulnerability`, `#software engineering`, `#cybersecurity`, `#systems`

---

<a id="item-tech-news-4"></a>
### [Even the best AI agents struggle with everyday life](https://techcrunch.com/2026/11/24/even-the-best-ai-agents-struggle-with-everyday-life/) ⭐️ 8.0/10

ShellBench reveals that even advanced AI agents struggle with everyday tasks, underscoring safety and reliability challenges for personal assistants.

rss · TechCrunch · 11月24日 21:33

**标签**: `#AI`, `#personal assistants`, `#benchmarks`, `#safety`, `#research`

---

<a id="item-tech-news-5"></a>
### [UK warns AI-driven cyberattacks are exposing years of weak security](https://techcrunch.com/2026/11/24/uk-warns-ai-driven-cyberattacks-are-exposing-years-of-weak-security/) ⭐️ 8.0/10

UK’s cybersecurity unit warns of a surge in AI‑driven attacks exploiting weak defenses, underscoring a growing threat to software and system security.

rss · TechCrunch · 11月24日 18:02

**标签**: `#cybersecurity`, `#AI`, `#cyberattacks`, `#NCSC`, `#UK`

---

<a id="item-tech-news-6"></a>
### [Uber 与 Nuro 开始 Lucid 机器人出租车无人驾驶测试](https://techcrunch.com/2026/11/24/uber-and-nuro-begin-driverless-testing-of-lucid-robotaxis-ahead-of-2027-launch/) ⭐️ 8.0/10

Uber 与 Nuro 已在旧金山湾区公共道路上开始测试 Lucid Gravity SUV 的全无人驾驶模式，已获得取消安全驾驶员的许可。此次测试是向员工提供无人驾驶乘车服务并在 2027 年第一季度推出商业机器人出租车服务的关键一步。车辆为 Lucid Gravity SUV，配备 Nuro 开发的自动驾驶技术，Uber 之前已向 Lucid 投资 3 亿美元。

rss · TechCrunch · 11月24日 16:40

**「背景」** Uber 与 Nuro 在 2025 年宣布投资 3 亿美元给 Lucid 并计划采购 20,000 辆配备 Nuro 自动驾驶系统的 Lucid Gravity SUV，随后 Nuro 获得加州 DMV 许可可在公共道路上无安全驾驶员测试车辆。

**「影响」** 取消安全驾驶员的许可使 Uber 与 Nuro 能够进行完全无人驾驶的道路测试，缩短测试周期并降低成本，从而更快地推进 2027 年的商业机器人出租车发布。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://lucidmotors.com/stories/lucid-nuro-uber-partner">Lucid , Nuro &amp; Uber Launch Robotaxis | Lucid Motors</a></li>
<li><a href="https://electrek.co/guides/nuro/">Nuro | Electrek</a></li>
<li><a href="https://techcrunch.com/2025/07/17/uber-makes-multi-million-dollar-investment-in-lucid-nuro-to-build-robotaxi-service/">Uber makes multimillion-dollar investment in Lucid and Nuro to build...</a></li>

</ul>
</details>

**标签**: `#autonomous vehicles`, `#driverless cars`, `#robotaxi`, `#Uber`, `#Nuro`

---

<a id="item-tech-news-7"></a>
### [Why a Crusoe investor is betting on solar and batteries to power future AI data centers](https://techcrunch.com/2026/11/24/why-a-crusoe-investor-is-betting-on-solar-and-batteries-to-power-future-ai-data-centers/) ⭐️ 8.0/10

A Crusoe investor is backing solar and battery solutions to meet the growing power demands of AI data centers, reflecting a notable shift toward renewable energy in AI infrastructure.

rss · TechCrunch · 11月24日 16:10

**标签**: `#AI infrastructure`, `#renewable energy`, `#data centers`, `#investment`, `#technology`

---

<a id="item-tech-news-8"></a>
### [FCC 提议对外星座运营商实施对等限制](https://www.theregister.com/networks/2026/11/24/fcc-proposes-tit-for-tat-restrictions-on-foreign-satellite-operators/5311889) ⭐️ 7.0/10

美国联邦通信委员会（FCC）计划于 12 月投票通过一项提案，若外国卫星运营商对美国供应商实施限制，FCC 将对当地企业实施同等限制。该提案主要是对欧盟 2 GHz 频谱计划的回应，欧盟要求三分之二的 2 GHz 频谱仅限本土运营商，已将 SpaceX 和亚马逊 LEO 排除在外。

telegram · zaihuapd · 11月24日 15:12

**「背景」** 欧盟在其 2 GHz 频谱计划中规定，至少 66%的频谱必须由本土运营商使用，旨在保护欧洲本土卫星业务，已导致 SpaceX 和亚马逊 LEO 被排除。

**「影响」** 若 FCC 批准该提案，SpaceX、亚马逊 LEO 等美国卫星运营商可能面临与欧盟相同的限制，迫使其在美国市场上与本土供应商竞争时受到约束。

**标签**: `#regulation`, `#satellite`, `#FCC`, `#EU`, `#spectrum`

---

## 国际要闻

<a id="item-world-news-1"></a>
### [Democrat Victoria Broderick unseats eight-term Republican incumbent in Tennessee to win election](https://www.theguardian.com/us-news/2026/nov/24/democrat-victoria-broderick-election-win-tennesee-midterms) ⭐️ 9.0/10

Democrat Victoria Broderick defeats long‑time Republican incumbent Scott DesJarlais in Tennessee’s 4th district, boosting the Democratic majority in the U.S. House.

rss · The Guardian World · 11月24日 20:20

**标签**: `#US politics`, `#midterm elections`, `#House of Representatives`, `#Tennessee`, `#political upset`

---

<a id="item-world-news-2"></a>
### [Huawei found guilty of stealing trade secrets but acquitted of racketeering](https://www.bbc.co.uk/news/articles/cmy49ngydqzpo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Huawei was convicted of trade‑secret theft and bank fraud, but cleared of racketeering in a landmark U.S. trial.

rss · BBC World · 11月24日 21:32

**标签**: `#Huawei`, `#US trial`, `#trade secrets`, `#China-US relations`, `#technology`

---

<a id="item-world-news-3"></a>
### [俄罗斯在马里冲突中损失逾 300 名士兵](https://www.theguardian.com/world/2026/nov/24/russian-fighters-killed-in-mali-africa-leaked-data) ⭐️ 8.0/10

根据泄露的报告，俄罗斯在马里连续三年共计有 349 名军人死亡，事件发生在 2026 年 4 月 25 日的基达尔袭击中。

rss · The Guardian World · 11月24日 16:00

**「俄罗斯非洲军团在马里的部署」** 自 2021 年起，俄罗斯的“非洲军团”已在马里部署约 300-350 名部队，并与瓦格纳集团合作，为马里军队提供军事援助。

**「潜在影响」** 这高死亡率可能促使俄罗斯重新评估其在非洲的军事部署和外交政策，影响其在该地区的战略布局。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Africa_Corps_%28Russia%29">Africa Corps ( Russia ) - Wikipedia</a></li>
<li><a href="https://www.yahoo.com/news/articles/russias-africa-corps-fights-mali-052131039.html">As Russia &#x27;s Africa Corps fights in Mali , witnesses describe atrocities...</a></li>

</ul>
</details>

**标签**: `#Russia`, `#Mali`, `#military casualties`, `#foreign policy`, `#African conflict`

---

<a id="item-world-news-4"></a>
### [EU to impose cap on Chinese hybrid EV imports next month](https://www.theguardian.com/business/2026/nov/24/eu-cap-chinese-hybrid-ev-imports-tariff-uk) ⭐️ 8.0/10

The EU will impose quotas on Chinese hybrid electric vehicles next month, also affecting hybrids from Japan, Turkey, South Korea and the UK.

rss · The Guardian World · 11月24日 10:59

**标签**: `#EU trade policy`, `#electric vehicles`, `#China`, `#automotive industry`, `#global trade`

---

<a id="item-world-news-5"></a>
### [Schumer 指控黄仁勋违反出口管制](https://www.theguardian.com/technology/2026/nov/24/nvidia-jensen-huang-congress) ⭐️ 8.0/10

参议院少数党领袖查克·舒默在推特上指责 Nvidia 首席执行官黄仁勋向中国运送“极其先进的芯片”，并违反美国出口管制法。舒默称此举相当于在太空竞赛期间向苏联出售火箭发动机。黄仁勋已于本周被重新任命为 Nvidia CEO。

rss · The Guardian World · 11月24日 20:05

**「Nvidia 出口管制背景」** 美国政府已在 2026 年 11 月对 Nvidia 最高端芯片实施出口管制，并成立专门委员会以监控向中国的销售。此前，特朗普政府已限制中国通过间接渠道获取这些芯片。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.cbsnews.com/news/nvidia-export-control-committee-china-chips/">Nvidia forms export control panel amid concerns over China sales</a></li>
<li><a href="https://apnews.com/article/nvidia-export-controls-chips-china-remote-access-60f868d3bb430b85a8657b27d421096e">Trump administration moves to restrict China from indirect ...</a></li>

</ul>
</details>

**标签**: `#US politics`, `#technology`, `#export controls`, `#China`, `#Nvidia`

---

<a id="item-world-news-6"></a>
### [前法国总统萨科齐与妻子将受审](https://www.bbc.co.uk/news/articles/c65y17pwv1z7o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 7.0/10

前法国总统尼古拉·萨科齐及其妻子卡拉·布鲁尼将于明年受审，指控与前利比亚独裁者穆阿迈尔·加达菲资金支持其竞选活动有关。审判聚焦于一名关键证人撤回其最初声称拥有能使萨科齐受牵连的证据的证词。两人否认任何不当行为。萨科齐在去年九月因同案被判五年监禁，成为首位入狱的法国前总统，实际服刑仅 20 天。上诉判决预计于下周一公布。

rss · BBC World · 11月24日 16:49

**「Sarkozy 的政治与司法背景」** 尼古拉·萨科齐（1955 年生）曾于 2007 年至 2012 年担任法国总统，2019 年因涉嫌与利比亚前独裁者穆阿迈尔·加达菲的资金往来而被判五年有期徒刑，成为首位入狱的法国前总统。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.elysee.fr/en/nicolas-sarkozy">Nicolas Sarkozy | Élysée</a></li>
<li><a href="https://williambowles.info/2018/03/30/frances-bling-bling-sarkozy-haunted-by-ghost-of-gaddafi-by-finian-cunningham/">France’s Bling-Bling Sarkozy Haunted by Ghost of Gaddafi By Finian...</a></li>

</ul>
</details>

**标签**: `#politics`, `#France`, `#legal`, `#former president`, `#campaign finance`

---

<a id="item-world-news-7"></a>
### [Israeli air strike kills Hamas internal security chief in Gaza](https://www.bbc.co.uk/news/articles/c6rrg7ggq190o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 7.0/10

Israeli air strike killed Hamas internal security chief Naeem Abu Nahel in Gaza, marking a high‑level blow to Hamas leadership.

rss · BBC World · 11月24日 15:35

**标签**: `#Israel-Hamas conflict`, `#Gaza`, `#military strike`, `#Hamas leadership`, `#regional security`

---

## 财经新闻

<a id="item-finance-news-1"></a>
### [美联储威廉姆斯暗示未来加息以抑制通胀](https://www.cnbc.com/2026/11/23/john-williams-fed-inflation-rate-hikes.html) ⭐️ 8.0/10

美联储纽约联储主席约翰·威廉姆斯表示，未来可能需要进一步加息，以在 2027 年前将通胀率降至 2%目标。

rss · CNBC Finance · 11月24日 13:33

**「背景」** 威廉姆斯在纽约蒙特圣文森特大学的演讲中重申，通胀将随着经济增长而逐步回落，并表示人工智能对价格的影响有限。

**标签**: `#Fed`, `#interest rates`, `#inflation`, `#monetary policy`

---