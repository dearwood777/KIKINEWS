---
layout: default
title: "Horizon Summary: 2026-11-18 (ZH)"
date: 2026-11-18
lang: zh
---

> 从 79 条内容中筛选出 16 条重要资讯。

---

**科技新闻**
1. [Nginx HTTP/2 RCE 漏洞已修复](#item-tech-news-1) ⭐️ 8.0/10
2. [黄仁勋辞职，OpenAI CEO 评行业影响](#item-tech-news-2) ⭐️ 8.0/10
3. [Xint 披露 5 个 nginx 漏洞，可打到主机 root](#item-tech-news-3) ⭐️ 8.0/10

**国际要闻**
1. [民主党提名贾弗里斯为美国众议院议长](#item-world-news-1) ⭐️ 9.0/10
2. [特朗普、普京、习近平在深圳握手 预备亚太峰会会谈](#item-world-news-2) ⭐️ 8.0/10
3. [以色列在加沙黄线外发动罕见地面行动](#item-world-news-3) ⭐️ 8.0/10
4. [Kuwait says it repelled first Iranian attack in two months after US strikes island](#item-world-news-4) ⭐️ 8.0/10
5. [普京、特朗普、习近平深圳小型峰会已排定](#item-world-news-5) ⭐️ 8.0/10
6. [The seven Anthropic founders who are about to become multi-billionaires](#item-world-news-6) ⭐️ 8.0/10
7. [英国‑欧盟关系重置草案：宠物护照、奶酪与青年流动](#item-world-news-7) ⭐️ 8.0/10
8. [以色列因英国制裁推迟约旦河西岸定居点建设合同](#item-world-news-8) ⭐️ 8.0/10
9. [Anthropic IPO 定价 83 美元，超预期](#item-world-news-9) ⭐️ 8.0/10
10. [尼泊尔在 COP31 面临严峻需求，考验全球](#item-world-news-10) ⭐️ 8.0/10
11. [William and Kate meet PM Modi as they wrap up India tour](#item-world-news-11) ⭐️ 7.0/10

**财经新闻**
1. [美联储官员预计进一步加息并警示 AI 对通胀的影响](#item-finance-news-1) ⭐️ 9.0/10
2. [Fed’s Waller says central bank may need to ‘shock people’ with half-point rate hike](#item-finance-news-2) ⭐️ 7.0/10

---

## 科技新闻

<a id="item-tech-news-1"></a>
### [Nginx HTTP/2 RCE 漏洞已修复](https://www.wiz.io/blog/nginx-http2-rce-vulnerabilities) ⭐️ 8.0/10

Nginx 的 HTTP/2 实现存在未授权远程代码执行漏洞（CVE‑2026‑123633 和 CVE‑2026‑123007），影响已启用 HTTP/2 的服务器。漏洞已在开源仓库中修复，官方建议立即升级或禁用 HTTP/2 以防止攻击。

hackernews · speedping · 11月18日 15:19 · [社区讨论](https://news.ycombinator.com/item?id=50547374)

**「背景」** Nginx 的 HTTP/2 实现存在整数下溢漏洞（CVE‑2026‑123007 与 CVE‑2026‑123633），被评为严重（CVSS 9.2），影响 1.9.5 至 1.31.8 版本在启用 HTTP/2 时的服务器。修复已在 1.30.7（稳定）和 1.31.9（主线）中发布，或通过禁用 HTTP/2 作为临时缓解措施。

**「影响」** 受影响的 Nginx 服务器管理员必须应用官方补丁或禁用 HTTP/2，否则服务器易被远程执行任意代码。

**「社区讨论」** 社区评论指出漏洞已在一周前修复，且仅约 12% 的服务器启用 HTTP/2，建议通过禁用 HTTP/2 作为临时缓解措施。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.wiz.io/blog/nginx-http2-rce-vulnerabilities">Unauthenticated Remote Code Execution in NGINX ... | Wiz Blog</a></li>
<li><a href="https://ma.ttias.be/nginx-http2-cve-2026-123633-123007/">nginx HTTP/2 RCE (CVE-2026-123633, CVE-2026-123007): patch ...</a></li>

</ul>
</details>

**标签**: `#security`, `#nginx`, `#remote code execution`, `#http2`, `#vulnerability`

---

<a id="item-tech-news-2"></a>
### [黄仁勋辞职，OpenAI CEO 评行业影响](https://techcrunch.com/2026/11/18/openai-ceo-sam-altman-says-its-hard-to-imagine-the-ai-industry-without-jensen/) ⭐️ 8.0/10

Nvidia 联合创始人兼前 CEO 黄仁勋于上周辞职，原因是涉及两名员工的婚外情和涉嫌中国间谍的指控。OpenAI CEO Sam Altman 在纽约时报 DealBook 峰会上表示，黄仁勋的离职让人难以想象 AI 行业的未来。此举可能影响 AI 硬件供应链、国家安全政策和行业合作。

rss · TechCrunch · 11月18日 16:14

**「背景」** Nvidia 联合创始人兼前 CEO 黄仁勋因涉及多起丑闻，包括与两名员工的婚外情和涉嫌与中国间谍合作，已于上周辞去 CEO 职务，并由首席财务官科莱特·克雷斯暂时接任。

**「影响」** 黄仁勋的辞职可能导致 Nvidia 在 AI 加速器市场的供应链不确定性，影响 OpenAI 等 AI 研发机构的硬件采购计划。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.theguardian.com/technology/2026/nov/12/nvidia-ceo-jensen-huang-resigns">Jensen Huang resigns as Nvidia CEO after alleged affairs</a></li>
<li><a href="https://www.bbc.com/news/live/c6zjry11v8w1t">Huang agrees to appear before Congress, US lawmakers... - BBC News</a></li>
<li><a href="https://www.bbc.co.uk/news/articles/ckgel338xql3o">Jensen Huang : What we know as Nvidia CEO resigns after adultery...</a></li>

</ul>
</details>

**标签**: `#AI industry`, `#Nvidia`, `#Jensen Huang`, `#OpenAI`, `#security`

---

<a id="item-tech-news-3"></a>
### [Xint 披露 5 个 nginx 漏洞，可打到主机 root](https://nginx2root.com/) ⭐️ 8.0/10

Xint publicly discloses five nginx vulnerabilities that allow attackers to gain root access, prompting immediate patching and mitigation actions.

telegram · zaihuapd · 11月18日 16:21

**标签**: `#security`, `#nginx`, `#vulnerabilities`, `#root`, `#CVE`

---

## 国际要闻

<a id="item-world-news-1"></a>
### [民主党提名贾弗里斯为美国众议院议长](https://www.bbc.co.uk/news/articles/cmy49873dn95o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 9.0/10

美国众议院民主党正式提名哈基姆·贾弗里斯为议长，预示他有望成为首位担任该职务的黑人议员。众议院将于 1 月 3 日选举新议长，届时民主党将占多数。贾弗里斯在投票后表示此举是“极大的荣誉和特权”。

rss · BBC World · 11月18日 21:13

**「背景：杰弗里斯的政治历程」** Hakeem Jeffries 自 2013 年起担任纽约第八选区的美国众议员，已连任七届。2023 年 1 月，他在 Nancy Pelosi 退任后接任众议院民主党领袖。

**「潜在影响」** 若当选，贾弗里斯将主持党内最大规模的众议院多数，并在参议院也由民主党控制的情况下，进一步巩固两院的协同治理。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Hakeem_Jeffries">Hakeem Jeffries - Wikipedia</a></li>
<li><a href="https://jeffries.house.gov/about/">About – Congressman Hakeem Jeffries</a></li>
<li><a href="https://patriot.university/knowledge-base/people/04-federal-legislators/us-house/hakeem-jeffries-profile/">Hakeem Jeffries : Biden Withdrawal Role and Prior Knowledge</a></li>

</ul>
</details>

**标签**: `#US politics`, `#Speaker of the House`, `#Hakeem Jeffries`, `#political leadership`

---

<a id="item-world-news-2"></a>
### [特朗普、普京、习近平在深圳握手 预备亚太峰会会谈](https://www.bbc.co.uk/news/articles/ck9d75x5wwwwo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

前美国总统特朗普在中国深圳与俄罗斯总统普京和中国国家主席习近平握手，准备在亚太峰会前进行会谈。特朗普与普京首次会面超过一年，双方将于峰会期间进行一对一会谈，可能讨论乌克兰战争。

rss · BBC World · 11月18日 16:10

**「APEC 峰会背景」** 2026 年 11 月 18 日至 19 日在中国深圳举行的第 33 届亚太经合组织（APEC）领导人会议，主题为“构建亚太共同体，促进共享繁荣”，汇聚了 21 个成员经济体的领导人。

**「可能影响」** 此次会晤为双方在峰会期间讨论乌克兰战争提供了机会，可能影响后续外交决策。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://sputnikglobe.com/20261118/live-updates-apec-summit-day-one-1125085587.html">LIVE UPDATES: APEC Summit Day One | Sputnik International</a></li>
<li><a href="https://www.scmp.com/video/china/3374821/live-apec-leaders-deliver-opening-remarks-apec-summit">Live: Leaders speak at Apec summit | South China Morning Post</a></li>

</ul>
</details>

**标签**: `#international relations`, `#diplomacy`, `#US`, `#Russia`, `#China`

---

<a id="item-world-news-3"></a>
### [以色列在加沙黄线外发动罕见地面行动](https://www.bbc.co.uk/news/articles/cw8r7510degno?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

以色列地面部队于 2026 年 11 月 18 日在加沙中部黄线以外发动罕见行动，先后向居民发出撤离命令并派遣坦克向努塞里亚难民营东侧推进，随后在主要南北向道路上展开行动。以色列军方称此次行动旨在拆除黄线西侧的恐怖隧道。哈马斯则指责以色列违反了 2025 年 10 月的停火协议。

rss · BBC World · 11月18日 20:14

**「黄线的设立背景」** 黄线是在 2025 年 10 月停火协议后设立的，划分加沙地带为以色列控制的东部和哈马斯控制的西部。该线旨在限制以色列的军事存在并划分双方势力范围。

**「直接影响」** 当地居民被迫撤离，导致人道状况恶化并可能引发进一步的紧急救援需求。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Yellow_Line_%28Gaza%29">Yellow Line (Gaza) - Wikipedia</a></li>
<li><a href="https://www.inss.org.il/publication/gaza-day-after/">Interactive Map: The Yellow Line in Gaza (Archive - November ...</a></li>
<li><a href="https://news.un.org/en/story/2026/09/1168320">‘Where do we go?’: How Israel’s ‘yellow line’ is closing in ...</a></li>

</ul>
</details>

**标签**: `#Israel`, `#Gaza`, `#military operation`, `#ground invasion`, `#Yellow Line`

---

<a id="item-world-news-4"></a>
### [Kuwait says it repelled first Iranian attack in two months after US strikes island](https://www.bbc.co.uk/news/articles/cw4gn9jeqjq7o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Kuwait and Bahrain repelled an Iranian drone attack on a U.S. airbase, marking the first such strike in over two months amid rising Iran‑U.S. tensions.

rss · BBC World · 11月18日 13:04

**标签**: `#Iran`, `#United States`, `#Kuwait`, `#Drone attack`, `#Regional conflict`

---

<a id="item-world-news-5"></a>
### [普京、特朗普、习近平深圳小型峰会已排定](https://www.bbc.co.uk/news/articles/c9n70gd320mpo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

2026 年 11 月 18 日，俄罗斯总统普京、美国前总统特朗普和中国国家主席习近平将于深圳举行一次三方小型峰会，已被确认安排在本周四举行。

rss · BBC World · 11月18日 10:53

**「APEC 三边会晤背景」** 在 2022 年俄罗斯入侵乌克兰后，普京被国际社会孤立。2026 年，亚太经合组织（APEC）在深圳举行，主办国中国邀请普京、特朗普和习近平三国领导人举行三边会晤。

**「可能影响」** 据报道，此次峰会被视为普京在全球政治中的一次重要提升。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www.nytimes.com/live/2026/11/18/world/trump-china-asia-apec">Xi Greets Trump as He Lands in China for Summit Meeting: Live...</a></li>
<li><a href="https://www.bbc.com/news/articles/c9n70gd320mpo">Steve Rosenberg: Historic talks with Xi and Trump are a coup for Putin</a></li>
<li><a href="https://www.dw.com/en/apec-summit-xi-trump-and-putin-gather-in-shenzhen-china/live-79964719">APEC summit : Xi , Trump and Putin gather in Shenzhen , China</a></li>

</ul>
</details>

**标签**: `#international relations`, `#politics`, `#Russia`, `#China`, `#US`

---

<a id="item-world-news-6"></a>
### [The seven Anthropic founders who are about to become multi-billionaires](https://www.bbc.co.uk/news/articles/cmd7159vlr85o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Anthropic, a leading AI startup, is going public with a valuation over $1 trillion, making its founders multi‑billionaires.

rss · BBC World · 11月18日 13:55

**标签**: `#AI`, `#Anthropic`, `#IPO`, `#Tech`, `#Business`

---

<a id="item-world-news-7"></a>
### [英国‑欧盟关系重置草案：宠物护照、奶酪与青年流动](https://www.theguardian.com/politics/2026/nov/18/uk-eu-relationship-reset-draft-explainer) ⭐️ 8.0/10

2026 年 11 月 18 日，英国与欧盟官员计划在布鲁塞尔签署“关系重置”草案。泄露的第二版文本共 72 段，涵盖宠物护照、奶酪进口、学生费用、艺术家签证以及一项青年流动计划，允许欧盟和英国公民在对方国家居住最长三年，进行工作、学习、志愿服务等活动。已确认的事实包括签署时间和草案基本达成；仍有部分细节未最终敲定，青年计划可能要等到 2030 年才生效。

rss · The Guardian World · 11月18日 17:56

**「背景说明」** 该协议由英国首相基尔·斯塔默在脱欧后启动，旨在正式化英国与欧盟的后脱欧关系。

**「潜在影响」** 若草案生效，欧盟与英国公民可在对方国家居住三年，可能提升人员流动与文化交流，但因可能推迟至 2030 年才生效，短期内效益有限。

**标签**: `#UK`, `#EU`, `#Diplomacy`, `#Trade`, `#Mobility`

---

<a id="item-world-news-8"></a>
### [以色列因英国制裁推迟约旦河西岸定居点建设合同](https://www.theguardian.com/world/2026/nov/18/israel-construction-contracts-e1-west-bank-settlement-uk-sanctions) ⭐️ 8.0/10

以色列已推迟发放约旦河西岸大型定居点建设合同，原因是英国对八家在该地区运营的建筑公司实施制裁。以色列外交官表示，此举并非对英国措施的回应，而是由内阁决定。英国外交官则认为制裁过早。

rss · The Guardian World · 11月18日 14:05

**「英国对以色列建筑公司实施制裁」** 英国在本周对八家从事约旦河西岸定居点建设的以色列建筑公司实施制裁，旨在遏制该地区的定居扩张。此前，英国已在 2026 年 9 月修订制裁框架，以更有效地针对支持定居点的企业。

**「直接影响」** 以色列土地管理局和住房部已被命令暂停招标程序，阻止该定居点的进一步建设。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://apnews.com/article/britain-israel-sanctions-west-bank-construction-8e4de81ef0b6fdbf0fd5f687e95de163">UK sanctions Israeli companies building West Bank settlements</a></li>
<li><a href="https://commonslibrary.parliament.uk/research-briefings/CBP-12195/">UK-Israel relations 2026: E1 settlement plan, trade and sanctions</a></li>
<li><a href="https://www.jta.org/2026/11/17/israel/britain-sanctions-israeli-aid-blocking-group-and-settlement-construction-companies">Britain sanctions Israeli aid-blocking group and settlement ...</a></li>

</ul>
</details>

**标签**: `#Israel`, `#West Bank`, `#UK sanctions`, `#settlement expansion`, `#international diplomacy`

---

<a id="item-world-news-9"></a>
### [Anthropic IPO 定价 83 美元，超预期](https://www.theguardian.com/technology/2026/nov/18/anthropic-share-price-stock-market-ipo) ⭐️ 8.0/10

Anthropic 公司于 2026 年 11 月 18 日宣布其首次公开募股（IPO）股票定价为 83 美元，预计将成为历史上规模最大的 IPO 之一。该公司将于次日以 ANT 为代码在纳斯达克交易所上市，首席执行官 Dario Amodei 与联合创始人一起敲响开市钟。此前，Anthropic 在上周公布的预估价格区间为 70 至 78 美元，最终估值介于 1.26 万亿美元至 1.41 万亿美元之间，排名第二，仅次于 SpaceX。

rss · The Guardian World · 11月18日 21:39

**「Anthropic 的创立背景」** Anthropic 于 2021 年由前 OpenAI 研究员达里奥·阿莫迪（Dario Amodei）及其妹妹达尼埃拉（Daniela Amodei）创立，致力于开发 Claude 系列大型语言模型。

**「直接影响」** 此次 IPO 将使 Amodei 及其六位联合创始人共计出售约 2.6 亿美元的股份，为公司和创始团队带来可观的资金流入。

<details><summary>参考链接</summary>
<ul>
<li>Dario Amodei - Wikipedia</li>

</ul>
</details>

**标签**: `#IPO`, `#Artificial Intelligence`, `#Finance`, `#Technology`

---

<a id="item-world-news-10"></a>
### [尼泊尔在 COP31 面临严峻需求，考验全球](https://news.google.com/rss/articles/CBMifEFVX3lxTFBhVjNBM0hjaU9xM0Myak93ZmRxcS1BbEVVUzloam42UmFBRHcxaUFabUY2cjFTOEh5OWtUY2R6OW9yYjhHMXVNNnJFenpLdmE4YTNsZVYtaHhkVWN0Y0pPNjA5UDBMOGJNdjRwS3p4dW90NHVMVHk3MHdVYXI?oc=5) ⭐️ 8.0/10

尼泊尔代表团在 2026 年 11 月的 COP31 会议上发出紧急呼吁，强调其迫切需求。该国在会议上请求全球采取行动，但具体措施尚未公布。

google\_news · The New York Times · 11月18日 20:08

**「先前的气候行动与合作呼吁」** 在 COP31 之前，尼泊尔环保组织已呼吁跨境合作，回应 8 月尼泊尔-中国边境泥石流灾害，并提出“萨加尔马塔到海洋”伙伴关系，旨在将喜马拉雅与太平洋岛国联手应对共同的气候风险。

<details><summary>参考链接</summary>
<ul>
<li><a href="https://www3.nhk.or.jp/nhkworld/news/20261112de75004/">Nepali climate activists appeal for urgent action at COP31</a></li>
<li><a href="https://nepalincop.org/">Nepal in COP</a></li>

</ul>
</details>

**标签**: `#COP31`, `#Climate Change`, `#International Relations`, `#South Asia`, `#Environmental Policy`

---

<a id="item-world-news-11"></a>
### [William and Kate meet PM Modi as they wrap up India tour](https://www.bbc.co.uk/news/articles/cq62ped2ypy4o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 7.0/10

Prince William and Kate meet PM Modi, concluding a UK royal visit to India and presenting Earthshot environmental prizes.

rss · BBC World · 11月18日 20:07

**标签**: `#royalty`, `#diplomacy`, `#UK-India`, `#environmental awards`, `#Earthshot`

---

## 财经新闻

<a id="item-finance-news-1"></a>
### [美联储官员预计进一步加息并警示 AI 对通胀的影响](https://www.cnbc.com/2026/11/18/fed-minutes-october-2026.html) ⭐️ 9.0/10

美联储官员在 10 月会议中表示，可能需要进一步加息，其中部分成员提议加息 0.25 个百分点，甚至在 12 月会议上考虑更大幅度加息。

rss · CNBC Finance · 11月18日 19:41

**「背景」** 会议讨论将人工智能视为通胀的“重要来源”，并指出经济中的通胀压力是广泛的。

**标签**: `#Fed`, `#interest rates`, `#AI`, `#inflation`, `#monetary policy`

---

<a id="item-finance-news-2"></a>
### [Fed’s Waller says central bank may need to ‘shock people’ with half-point rate hike](https://www.cnbc.com/2026/11/18/federal-reserve-governor-christopher-waller.html) ⭐️ 7.0/10

Fed Governor Waller indicates a possible half‑point rate hike to curb inflation.

rss · CNBC Finance · 11月18日 15:13

**标签**: `#Federal Reserve`, `#Interest Rates`, `#Monetary Policy`, `#Inflation`, `#Economic Policy`

---