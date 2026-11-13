---
layout: default
title: "Horizon Summary: 2026-11-13 (EN)"
date: 2026-11-13
lang: en
---

> From 91 items, 16 important content pieces were selected

---

**Technology News**
1. [Rust 1.100 Release Adds Never Type, Custom Allocators, and Cargo Enhancements](#item-tech-news-1) ⭐️ 9.0/10
2. [Jensen Huang is out at Nvidia — who is Colette Kress, his interim replacement?](#item-tech-news-2) ⭐️ 9.0/10
3. [NVIDIA CEO Jensen Huang Resigns, CFO Kris Kres Becomes Interim CEO](#item-tech-news-3) ⭐️ 9.0/10
4. [Jensen Huang resigns](#item-tech-news-4) ⭐️ 8.0/10
5. [I&\#x27;m making LLMs work on small and old devices](#item-tech-news-5) ⭐️ 8.0/10
6. [Google’s latest Search upgrade promises better answers to your most complicated questions](#item-tech-news-6) ⭐️ 8.0/10
7. [Jensen Huang’s exit puts Nvidia’s support for open source in question](#item-tech-news-7) ⭐️ 8.0/10
8. [Hugging Face CEO vows to keep fighting for open source AI after Jensen Huang’s exit](#item-tech-news-8) ⭐️ 8.0/10

**World News**
1. [Putin Threatens to Target Foreign Troops Amid Starlink Disruptions](#item-world-news-1) ⭐️ 9.0/10
2. [WFP warns aid is Sudan’s only lifeline amid funding cuts](#item-world-news-2) ⭐️ 9.0/10
3. [US envoys meet Zelensky in Dublin after talks with Putin in Moscow](#item-world-news-3) ⭐️ 8.0/10
4. [Democrat Scott Colom makes history as Mississippi&\#x27;s first black senator since 19th Century](#item-world-news-4) ⭐️ 8.0/10
5. [Millions of Ebola dollars missing with staff unpaid while virus spreads, charity says](#item-world-news-5) ⭐️ 8.0/10
6. [The rise and fall of Jensen Huang - how the tech superstar became mired in scandal](#item-world-news-6) ⭐️ 8.0/10
7. [Jensen Huang has resigned, what&\#x27;s next for Nvidia?](#item-world-news-7) ⭐️ 8.0/10
8. [China rules out hosting Cop33 climate summit in 2028](#item-world-news-8) ⭐️ 8.0/10

---

## Technology News

<a id="item-tech-news-1"></a>
### [Rust 1.100 Release Adds Never Type, Custom Allocators, and Cargo Enhancements](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/) ⭐️ 9.0/10

Rust 1.100 stabilizes the never type and custom allocators, introduces dependency cooldowns, Cargo warnings for unused dependencies, and new APIs such as bool::toggle, Box::map, str::trim\_prefix/suffix, Path::trim\_prefix, and DropGuard. Cargo install now defaults to using the lockfile in the crate tarball, making --locked a no‑op.

hackernews · mbStavola · Nov 12, 18:39 · [Discussion](https://news.ycombinator.com/item?id=50472038)

**「Background」** Rust 1.100 builds on the long‑term Cargo dependency cooldown feature defined in RFC 3923, which was first discussed in early 2026 and added to Cargo to delay adoption of newly published crate versions. It also finalizes the never type, a language feature that had been in development for years and was announced as stabilizing in earlier releases. These prior discussions and stabilizations set the stage for the new language and tooling changes in 1.100.

**「Impact」** Developers can now use the never type for functions that never return, write custom allocators for fine‑grained memory control, enforce reproducible builds with dependency cooldowns, and clean Cargo.toml files by removing unused dependencies flagged by Cargo warnings.

<details><summary>References</summary>
<ul>
<li><a href="https://releases.rs/docs/1.100.0/">1.100.0 | Rust Changelogs - releases.rs</a></li>
<li><a href="https://rust-lang.github.io/rfcs//3923-cargo-min-publish-age.html">3923-cargo-min-publish-age - The Rust RFC Book</a></li>
<li><a href="https://www.linkedin.com/posts/rustjobs-dev_%F0%9D%90%91%F0%9D%90%AE%F0%9D%90%AC%F0%9D%90%AD%F0%9D%90%AC-%F0%9D%90%8D%F0%9D%90%9E%F0%9D%90%AF%F0%9D%90%9E%F0%9D%90%AB-%F0%9D%90%93%F0%9D%90%B2%F0%9D%90%A9%F0%9D%90%9E-%F0%9D%90%8D%F0%9D%90%9E%F0%9D%90%9A%F0%9D%90%AB%F0%9D%90%A2%F0%9D%90%A7%F0%9D%90%A0-activity-7470805631520788481-DKi8">Rust Never Type Stabilization Nears Completion | LinkedIn</a></li>

</ul>
</details>

**Tags**: `#Rust`, `#Language Features`, `#Cargo`, `#Systems Programming`

---

<a id="item-tech-news-2"></a>
### [Jensen Huang is out at Nvidia — who is Colette Kress, his interim replacement?](https://techcrunch.com/2026/11/12/jensen-huang-is-out-at-nvidia-who-is-colette-kress-his-interim-replacement/) ⭐️ 9.0/10

Jensen Huang’s immediate resignation from Nvidia signals a significant shift in a key AI hardware leader.

rss · TechCrunch · Nov 12, 15:37

**Tags**: `#Nvidia`, `#CEO resignation`, `#AI hardware`, `#leadership change`

---

<a id="item-tech-news-3"></a>
### [NVIDIA CEO Jensen Huang Resigns, CFO Kris Kres Becomes Interim CEO](https://nvidianews.nvidia.com/news/nvidia-announces-ceo-transition) ⭐️ 9.0/10

NVIDIA announced that Jensen Huang has resigned as president, CEO, and director, effective immediately. CFO Kris Kres is stepping in as interim CEO while continuing his CFO duties, and the board has begun a search for a permanent successor. Harvey C. Jones has been named the new board chair, and the company says operations, customer commitments, and the product roadmap will remain uninterrupted, with the Q3 earnings release still scheduled for November 17.

telegram · zaihuapd · Nov 12, 13:52

**「Background」** NVIDIA, a major AI hardware manufacturer, has been led by founder Jensen Huang, who served as president and CEO. When a CEO resigns, the board can appoint interim leadership; in this case it named CFO Colette Kress interim CEO and appointed Harvey C. Jones as chair.

**「Impact」** The leadership change may prompt investors to reassess NVIDIA’s valuation and could influence partner confidence, but the board’s assurance that product development and the Q3 earnings release will proceed as planned mitigates immediate operational risk.

<details><summary>References</summary>
<ul>
<li><a href="https://www.globenewswire.com/news-release/2026/11/12/3401635/0/en/nvidia-announces-ceo-transition.html">NVIDIA Announces CEO Transition | GlobeNewswire News Room</a></li>

</ul>
</details>

**Tags**: `#NVIDIA`, `#CEO transition`, `#AI hardware`, `#industry leadership`

---

<a id="item-tech-news-4"></a>
### [Jensen Huang resigns](https://apnews.com/article/nvidia-megaspeed-china-singapore-huang-5403f152a601cf82ce939f1d24fffa0f) ⭐️ 8.0/10

Nvidia CEO resignation is a high‑impact industry event with broad implications for AI and technology markets.

hackernews · lldb · Nov 12, 13:52 · [Discussion](https://news.ycombinator.com/item?id=50467087)

**Tags**: `#Nvidia`, `#AI`, `#Leadership`, `#ExportControls`, `#IndustryImpact`

---

<a id="item-tech-news-5"></a>
### [I&\#x27;m making LLMs work on small and old devices](https://github.com/hyperionaidev/smolmaxxing/) ⭐️ 8.0/10

Open‑source effort shows 16B LLMs running on 1GB‑memory devices, offering impactful edge‑AI insights.

hackernews · mrashad74 · Nov 12, 15:23 · [Discussion](https://news.ycombinator.com/item?id=50468888)

**Tags**: `#edge AI`, `#LLM optimization`, `#low-resource inference`, `#open source`, `#hardware acceleration`

---

<a id="item-tech-news-6"></a>
### [Google’s latest Search upgrade promises better answers to your most complicated questions](https://techcrunch.com/2026/11/12/googles-latest-search-upgrade-promises-better-answers-to-your-most-complicated-questions/) ⭐️ 8.0/10

Google’s Gemini 4 Hydrogen model promises a major upgrade to Search, offering faster, more accurate answers to complex queries.

rss · TechCrunch · Nov 12, 19:27

**Tags**: `#AI`, `#Search`, `#Google`, `#Gemini`, `#NLP`

---

<a id="item-tech-news-7"></a>
### [Jensen Huang’s exit puts Nvidia’s support for open source in question](https://techcrunch.com/2026/11/12/jensen-huangs-exit-puts-nvidias-support-for-open-source-in-question/) ⭐️ 8.0/10

Nvidia CEO Jensen Huang’s resignation raises concerns about the company’s future support for open‑source AI amid national‑security scrutiny.

rss · TechCrunch · Nov 12, 18:39

**Tags**: `#open-source`, `#AI`, `#Nvidia`, `#executive resignation`, `#national security`

---

<a id="item-tech-news-8"></a>
### [Hugging Face CEO vows to keep fighting for open source AI after Jensen Huang’s exit](https://techcrunch.com/2026/11/12/hugging-face-ceo-vows-to-keep-fighting-for-open-source-ai-after-jensen-huangs-exit/) ⭐️ 8.0/10

Hugging Face CEO reacts to Nvidia’s acquisition and Jensen Huang’s exit, underscoring the impact on open‑source AI.

rss · TechCrunch · Nov 12, 17:36

**Tags**: `#Nvidia`, `#Hugging Face`, `#Open Source AI`, `#Acquisition`, `#Leadership`

---

## World News

<a id="item-world-news-1"></a>
### [Putin Threatens to Target Foreign Troops Amid Starlink Disruptions](https://www.theguardian.com/world/2026/nov/12/vladimir-putin-russia-target-foreign-troops-ukraine-elon-musk-starlink) ⭐️ 9.0/10

On 12 November 2026, Russian President Vladimir Putin warned U.S. negotiators Jared Kushner and Steve Witkoff at the Kremlin that Russia would target any foreign troops deployed to Ukraine, while also refusing to accept peacekeeping forces and insisting on full control of four annexed regions. The remarks came as the Ukrainian military reported renewed disruptions to Elon Musk’s Starlink satellite service.

rss · The Guardian World · Nov 12, 22:26

**「Background of the conflict and Starlink」** In September 2022, Russia unilaterally declared annexation of Donetsk, Kherson, Luhansk and Zaporizhzhia, establishing occupation administrations in those oblasts. The Ukrainian military has relied on Elon Musk’s Starlink satellite network for communications, which has been intermittently disrupted during the conflict.

**「Impact」** The threat may deter the deployment of foreign peacekeeping troops to Ukraine and heighten the risk of escalation between Russia and the United States.

<details><summary>References</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Russian_annexation_of_Donetsk,_Kherson,_Luhansk_and_Zaporizhzhia_oblasts">Russian annexation of Donetsk, Kherson, Luhansk and ...</a></li>
<li><a href="https://en.wikipedia.org/wiki/Starlink">Starlink - Wikipedia</a></li>

</ul>
</details>

**Tags**: `#Russia`, `#Ukraine`, `#United States`, `#Diplomacy`, `#Military`

---

<a id="item-world-news-2"></a>
### [WFP warns aid is Sudan’s only lifeline amid funding cuts](https://news.google.com/rss/articles/CBMiV0FVX3lxTE9Sb255ek9CX0dfdjdIWUNqWDNzbUFKYWVjV1BQcDhXYXRkMV9kcjlaRG9EMGx1bWtBS1M4RmJCNW00N0d3MmJNa19DTm51S3c3cmZsLUVMcw?oc=5) ⭐️ 9.0/10

The World Food Programme chief warned that aid is the only hope for millions of Sudanese as funding cuts worsen the hunger crisis. The cuts have reduced the programme’s ability to deliver food assistance, leaving many families without essential supplies. The warning comes as the UN reports a growing number of people facing acute food insecurity.

google\_news · UN News · Nov 12, 18:37

**「WFP Funding Cuts and Rising Hunger」** The World Food Programme has been cutting assistance due to funding shortfalls, threatening to remove aid for 800,000 vulnerable people by the end of 2026, and the risk of famine has risen as crop failures and malnutrition spread.

**「Risk of Food Assistance Depletion」** The World Food Programme’s funding shortfall could exhaust its Sudan supplies in about two months, leaving more than 21 million people—especially displaced families—at risk of acute hunger, malnutrition and medicine shortages.

<details><summary>References</summary>
<ul>
<li><a href="https://www.wfp.org/emergencies/sudan">Risk of Famine in Sudan | World Food Programme</a></li>
<li><a href="https://allafrica.com/stories/202610230024.html">Sudan Hunger Crisis Deepens As Aid Cuts Collide... - allAfrica.com</a></li>
<li><a href="https://indonesianpost.com/2026/02/15/un-report-21-million-sudanese-face-acute-hunger-wfp-funding-crunch/">More than 21 million people in Sudan at risk of hunger as WFP aid...</a></li>
<li><a href="https://allafrica.com/stories/202610230024.html">Sudan Hunger Crisis Deepens As Aid Cuts Collide... - allAfrica.com</a></li>
<li><a href="https://indonesianpost.com/2026/02/15/un-report-21-million-sudanese-face-acute-hunger-wfp-funding-crunch/">More than 21 million people in Sudan at risk of hunger as WFP aid...</a></li>

</ul>
</details>

**Tags**: `#Sudan`, `#Humanitarian crisis`, `#WFP`, `#Aid`, `#Hunger`

---

<a id="item-world-news-3"></a>
### [US envoys meet Zelensky in Dublin after talks with Putin in Moscow](https://www.bbc.co.uk/news/articles/cwrkgmymk55zo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

US envoys Jared Kushner and Steve Witkoff met with Russian President Vladimir Putin and then Ukraine’s President Volodymyr Zelensky, agreeing on a new round of trilateral talks amid ongoing war discussions.

rss · BBC World · Nov 12, 21:00

**Tags**: `#diplomacy`, `#Ukraine war`, `#US-Russia relations`, `#trilateral talks`, `#Zelensky`

---

<a id="item-world-news-4"></a>
### [Democrat Scott Colom makes history as Mississippi&\#x27;s first black senator since 19th Century](https://www.bbc.co.uk/news/articles/cw7vppyr80eeo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Scott Colom, a Democrat, won Mississippi&\#x27;s U.S. Senate seat, becoming the state&\#x27;s first black senator since the 1800s.

rss · BBC World · Nov 12, 12:56

**Tags**: `#US politics`, `#elections`, `#diversity`, `#Mississippi`, `#Senate`

---

<a id="item-world-news-5"></a>
### [Millions of Ebola dollars missing with staff unpaid while virus spreads, charity says](https://www.bbc.co.uk/news/articles/cx98757ymm6zo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

MSF warns that millions of Ebola relief funds are missing and frontline staff in the DRC are unpaid, jeopardizing the outbreak response.

rss · BBC World · Nov 12, 15:18

**Tags**: `#Ebola`, `#DRC`, `#MSF`, `#funding`, `#public health`

---

<a id="item-world-news-6"></a>
### [The rise and fall of Jensen Huang - how the tech superstar became mired in scandal](https://www.bbc.co.uk/news/articles/cmze750zg0jeo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Nvidia’s founder Jensen Huang resigns after a scandal, a development that could reshape the company and affect the global technology landscape.

rss · BBC World · Nov 12, 17:11

**Tags**: `#technology`, `#business`, `#scandal`, `#Nvidia`, `#Jensen Huang`

---

<a id="item-world-news-7"></a>
### [Jensen Huang has resigned, what&\#x27;s next for Nvidia?](https://www.bbc.co.uk/news/videos/cmdx1r99kp9wo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Jensen Huang steps down as Nvidia CEO, triggering an interim leadership change and a brief stock market dip.

rss · BBC World · Nov 12, 19:33

**Tags**: `#Nvidia`, `#CEO resignation`, `#tech industry`, `#stock market`, `#business`

---

<a id="item-world-news-8"></a>
### [China rules out hosting Cop33 climate summit in 2028](https://www.theguardian.com/environment/2026/nov/12/china-rules-out-hosting-cop33-climate-summit-in-2028) ⭐️ 8.0/10

China has declined to host the 2028 COP33 climate summit, opening the bid to other Asian nations and altering the dynamics of global climate diplomacy.

rss · The Guardian World · Nov 12, 22:00

**Tags**: `#Climate Change`, `#COP33`, `#China`, `#International Relations`

---