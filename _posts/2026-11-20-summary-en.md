---
layout: default
title: "Horizon Summary: 2026-11-20 (EN)"
date: 2026-11-20
lang: en
---

> From 71 items, 16 important content pieces were selected

---

**Technology News**
1. [Behind Jensen Huang’s exit, questions about a management style reportedly built on fear](#item-tech-news-1) ⭐️ 9.0/10
2. [Inkling 2 Mini](#item-tech-news-2) ⭐️ 8.0/10
3. [Language Models Rewrite Their Own Weights via Reasoning](#item-tech-news-3) ⭐️ 8.0/10
4. [A transcription firm used by police, prosecutors, and tech giants exposed customer data online](#item-tech-news-4) ⭐️ 8.0/10
5. [CVE‑2026‑99312: KVM flaw lets VMs read AMD host memory](#item-tech-news-5) ⭐️ 8.0/10
6. [Experts warn: Nearly everyone in AI is susceptible to a honey-trap scheme right now](#item-tech-news-6) ⭐️ 7.0/10

**World News**
1. [ICJ Declares Myanmar Genocide; US Cautious, EU Praises](#item-world-news-1) ⭐️ 9.0/10
2. [UK to explore even closer ties with EU after agreeing deal, says Burnham](#item-world-news-2) ⭐️ 8.0/10
3. [Russian missile hits Poland as Ukraine&\#x27;s allies hold military exercise, says Tusk](#item-world-news-3) ⭐️ 8.0/10
4. [Russia Strikes Kyiv Bridges After Ukraine Damages Crimean Bridge](#item-world-news-4) ⭐️ 8.0/10
5. [UK‑EU post‑Brexit trade deal covers food, emissions, youth scheme](#item-world-news-5) ⭐️ 8.0/10
6. [Russian missile strikes hit Kyiv bridges, killing nine](#item-world-news-6) ⭐️ 8.0/10
7. [Nasdaq Loses 2026 Gains Amid AI Sell‑Off After Anthropic IPO](#item-world-news-7) ⭐️ 8.0/10
8. [Spain frees wealthy US-sought activist on bail as Irish police raid Dublin home](#item-world-news-8) ⭐️ 8.0/10
9. [EU wants ‘closest possible relationship’ with UK after agreeing Brexit reset deal – live](#item-world-news-9) ⭐️ 8.0/10
10. [Burnham seals trade and youth mobility deals in biggest step towards EU since Brexit](#item-world-news-10) ⭐️ 8.0/10

---

## Technology News

<a id="item-tech-news-1"></a>
### [Behind Jensen Huang’s exit, questions about a management style reportedly built on fear](https://techcrunch.com/2026/11/20/behind-jensen-huangs-exit-questions-about-a-management-style-reportedly-built-on-fear/) ⭐️ 9.0/10

Nvidia CEO Jensen Huang’s departure is highlighted, indicating a significant leadership change in a leading AI hardware company.

rss · TechCrunch · Nov 20, 13:25

**Tags**: `#Nvidia`, `#CEO`, `#AI hardware`, `#management`, `#industry`

---

<a id="item-tech-news-2"></a>
### [Inkling 2 Mini](https://thinkingmachines.ai/news/inkling-2-mini/) ⭐️ 8.0/10

Inkling 2 Mini is a new open‑weight, looped transformer model that offers competitive performance with large models while enabling efficient local deployment and multi‑agent reasoning.

hackernews · jasondavies · Nov 20, 20:12 · [Discussion](https://news.ycombinator.com/item?id=50581260)

**Tags**: `#AI models`, `#local deployment`, `#open source`, `#looped transformer`, `#MoE`

---

<a id="item-tech-news-3"></a>
### [Language Models Rewrite Their Own Weights via Reasoning](https://arxiv.org/abs/2611.21885) ⭐️ 8.0/10

A preprint on arXiv proposes that a language model can rewrite its own weights by reasoning about potential edits, a gradient‑free, no‑training self‑improvement method. The model generates candidate weight changes, tests them on practice problems, and only accepts those that improve performance, thereby iteratively refining its parameters. This approach is presented as a new weight‑space programming paradigm that could reshape how models are trained, though it remains unverified and is currently only a theoretical proposal.

hackernews · lwhsiao · Nov 20, 16:29 · [Discussion](https://news.ycombinator.com/item?id=50577265)

**「Weight‑space programming background」** Weight‑space programming treats a neural network’s weights as a program that can be read and edited by a language model; MIT researchers demonstrated this with GPT‑6 Astra, which could read, repair, and rewrite other models’ weights.

<details><summary>References</summary>
<ul>
<li><a href="https://rikiyat.github.io/blog/weight-space-programming/">Sparks of Weight - Space Programming : LLMs can natively read...</a></li>
<li><a href="https://itecs.ai/insights/weight-space-programming-explained">Weight - Space Programming : How LLMs Edit Model ... | ITECS AI</a></li>
<li><a href="https://jendume.com/en/news/gpt-6-astra-reprograms-other-ai-models-directly-through-their-weights/">GPT-6 Astra reprograms other AI models directly through their weights</a></li>

</ul>
</details>

**Tags**: `#self‑modifying models`, `#weight‑space programming`, `#AI self‑improvement`, `#language models`, `#no‑gradient training`

---

<a id="item-tech-news-4"></a>
### [A transcription firm used by police, prosecutors, and tech giants exposed customer data online](https://techcrunch.com/2026/11/20/a-transcription-firm-used-by-police-prosecutors-and-tech-giants-exposed-customer-data-online/) ⭐️ 8.0/10

A major security lapse at a transcription firm exposed sensitive police, government, and corporate data, underscoring urgent concerns about data privacy and secure handling in the tech ecosystem.

rss · TechCrunch · Nov 20, 15:46

**Tags**: `#security`, `#data-privacy`, `#law-enforcement`, `#AI-training`, `#tech-industry`

---

<a id="item-tech-news-5"></a>
### [CVE‑2026‑99312: KVM flaw lets VMs read AMD host memory](https://thehackernews.com/2026/11/new-linux-kvm-flaw-cve-2026-99312-lets.html) ⭐️ 8.0/10

A critical KVM vulnerability \(CVE‑2026‑99312\) allows virtual machines on AMD hosts with nested virtualization to read approximately 127 GB of host memory. The upstream kernel fix was released with stable kernel 7.3.5 on November 18, but Debian, Ubuntu, and other distributions have not yet incorporated the patch, so affected users must disable nested virtualization until the update is applied.

telegram · zaihuapd · Nov 20, 14:23

**「Background」** The flaw is specific to AMD processors running Linux with KVM and nested virtualization enabled, a configuration commonly used in cloud and AI workloads.

**「Impact」** Affected users must either wait for distribution kernel updates or temporarily disable nested virtualization to prevent host memory leakage.

**Tags**: `#security`, `#virtualization`, `#kernel`, `#AMD`, `#CVE`

---

<a id="item-tech-news-6"></a>
### [Experts warn: Nearly everyone in AI is susceptible to a honey-trap scheme right now](https://techcrunch.com/2026/11/20/experts-warn-nearly-everyone-in-ai-is-susceptible-to-a-honey-trap-scheme-right-now/) ⭐️ 7.0/10

TechCrunch warns that many AI professionals are vulnerable to honey‑trap schemes, highlighting a new security risk.

rss · TechCrunch · Nov 20, 20:58

**Tags**: `#security`, `#AI`, `#counterintelligence`, `#honey trap`, `#software engineering`

---

## World News

<a id="item-world-news-1"></a>
### [ICJ Declares Myanmar Genocide; US Cautious, EU Praises](https://www.theguardian.com/law/2026/nov/20/us-eu-reaction-myanmar-rohingya-genocide-icj-ruling-trump-international-law) ⭐️ 9.0/10

On Thursday, the International Court of Justice ruled that Myanmar committed genocide against the Rohingya minority. The United States responded cautiously to the decision, while the European Union praised the court’s role as a landmark judgment. The ruling is the first time a state has been found responsible for genocide by the world’s highest court.

rss · The Guardian World · Nov 20, 11:57

**「ICJ and Myanmar’s Rohingya Conflict」** The International Court of Justice \(ICJ\), the United Nations’ principal judicial organ, was established in 1945 to adjudicate disputes between states. Myanmar has faced accusations of genocide against the Rohingya Muslim minority since 2017, prompting international legal and humanitarian responses.

**「Impact」** The judgment may establish a legal precedent for future genocide claims, including a pending case against Israel.

**Tags**: `#ICJ`, `#Myanmar`, `#Rohingya`, `#genocide`, `#international law`

---

<a id="item-world-news-2"></a>
### [UK to explore even closer ties with EU after agreeing deal, says Burnham](https://www.bbc.co.uk/news/articles/c6jreyqgw4e9o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

UK Prime Minister announces that, following a new trade deal covering food exports, emissions trading and a youth scheme, the UK will seek even closer ties with the EU, potentially boosting the economy by up to £17 bn a year.

rss · BBC World · Nov 20, 17:49

**Tags**: `#UK`, `#EU`, `#Brexit`, `#trade deal`, `#economy`

---

<a id="item-world-news-3"></a>
### [Russian missile hits Poland as Ukraine&\#x27;s allies hold military exercise, says Tusk](https://www.bbc.co.uk/news/articles/cqx2x9dklxnro?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

A Russian missile breached Polish airspace amid Western military drills, prompting Poland to label it a provocation and raising concerns over regional security.

rss · BBC World · Nov 20, 16:54

**Tags**: `#Russia`, `#Poland`, `#military exercise`, `#missile`, `#international security`

---

<a id="item-world-news-4"></a>
### [Russia Strikes Kyiv Bridges After Ukraine Damages Crimean Bridge](https://www.bbc.co.uk/news/articles/c6x29gn4pdn9o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Russia launched a ballistic missile attack on Kyiv’s bridges and railway stations overnight, killing at least nine people, days after Ukraine damaged the Crimean Bridge. Russian President Vladimir Putin threatened retaliation for the earlier strike.

rss · BBC World · Nov 20, 13:01

**「Context of the Crimean Bridge Attack」** The Kerch Bridge, the sole road link between mainland Russia and the occupied Crimean peninsula, was heavily damaged by a Ukrainian strike on 17 November 2026, disrupting a critical supply route. In response, Russian President Vladimir Putin vowed retaliation, raising tensions ahead of the latest missile attack on Kyiv.

**「Impact」** The strike disrupted key transportation links in Kyiv, potentially hampering civilian movement and logistics.

<details><summary>References</summary>
<ul>
<li><a href="https://www.nytimes.com/2026/11/18/world/europe/russia-kerch-strait-crimean-bridge.html">Putin Vows to Retaliate After Crimea Bridge Attacks - The New York...</a></li>
<li><a href="https://www.dw.com/en/what-the-crimean-bridge-attack-means-for-russia/a-79985991">What the Crimean bridge attack means for Russia</a></li>

</ul>
</details>

**Tags**: `#Russia-Ukraine war`, `#Kyiv infrastructure`, `#Crimean Bridge`, `#missile attack`, `#regional conflict`

---

<a id="item-world-news-5"></a>
### [UK‑EU post‑Brexit trade deal covers food, emissions, youth scheme](https://www.bbc.co.uk/news/videos/c90k6gl3lyxeo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

On Friday, the UK and EU finalized a post‑Brexit trade agreement covering British food exports, emissions trading and a youth experience scheme. Prime Minister Andy Burnham called it a &quot;good day&quot; for Britain and Europe, while EU Council President António Costa said the EU remains open to the closest possible relationship. Conservative leader Kemi Badenoch and Reform Party leader Nigel Farage have criticized the deal, calling it unfair and a betrayal of the British people.

rss · BBC World · Nov 20, 21:43

**「Background of the UK‑EU post‑Brexit deal」** After the UK left the EU in 2020, the two sides had separate trade and environmental arrangements, with the UK’s emissions trading system diverging from the EU’s and no free‑trade provision for food exports. The new agreement, announced in November 2026, extends cooperation to include free trade in food, a linked emissions trading system, and a youth mobility scheme.

**「Impact」** The agreement will allow British food exporters to access EU markets more smoothly and enable UK participation in the EU emissions trading system.

<details><summary>References</summary>
<ul>
<li><a href="https://www.ft.com/content/be7924c4-8e29-4630-82f3-f94001765d37?syn-25a6b1a6=1">Andy Burnham’s EU deal in brief</a></li>
<li><a href="https://www.lbc.co.uk/article/britain-burnham-uk-eu-deal-win-win-tuition-fees-5HjdnLX_2/">&#x27;A good day for Britain&#x27;: Burnham hails UK - EU deal a &#x27;win-win&amp;apo...</a></li>
<li><a href="https://sputnikglobe.com/20261120/uk-eu-reach-new-post-brexit-trade-migration-deal---joint-statement-1125124641.html">UK , EU Reach New Post - Brexit Trade , Migration Deal - Joint Statement</a></li>

</ul>
</details>

**Tags**: `#UK`, `#EU`, `#Brexit`, `#trade deal`, `#post-Brexit relations`

---

<a id="item-world-news-6"></a>
### [Russian missile strikes hit Kyiv bridges, killing nine](https://www.bbc.co.uk/news/videos/c65y19wy3xl8o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Russian missiles struck bridges and railway stations in Kyiv overnight, killing at least nine people. President Zelensky called it one of the war’s most massive strikes. Russian President Putin had threatened retaliation for the earlier Crimean Bridge attack.

rss · BBC World · Nov 20, 15:14

**「Background」** The strikes followed a recent Russian attack that damaged the Crimean Bridge, a key link between Russia and occupied Crimea, prompting heightened tensions in the ongoing Ukraine war.

**「Impact」** The missile attack damaged key crossings in Kyiv, disrupting transport routes and causing significant infrastructure damage.

**Tags**: `#Russia-Ukraine war`, `#military attack`, `#missile strike`, `#infrastructure damage`, `#civilian casualties`

---

<a id="item-world-news-7"></a>
### [Nasdaq Loses 2026 Gains Amid AI Sell‑Off After Anthropic IPO](https://www.theguardian.com/business/2026/nov/20/global-stock-markets-slump-anthropic-ipo-ai-sell-off) ⭐️ 8.0/10

On 20 November 2026 the Nasdaq Composite erased all its 2026 gains, falling 5% from its 1 January value after Anthropic’s shares dropped 9% on their second trading day. The Dow and S&amp;P 500 also closed in correction territory, and the tech‑heavy index lost about $4 trillion in market value this week.

rss · The Guardian World · Nov 20, 21:38

**「Background」** Anthropic, the AI firm behind the Claude chatbot, had its record‑breaking IPO on 19 November 2026, the largest in history, but the shares slid sharply on the second day, triggering a broader sell‑off in AI‑linked stocks.

**「Impact」** The market decline erased roughly $4 trillion in market value for the Nasdaq, signalling a sharp correction in tech stocks and raising concerns about the sustainability of AI‑driven valuations.

**Tags**: `#stock market`, `#AI`, `#Anthropic`, `#Nasdaq`, `#market downturn`

---

<a id="item-world-news-8"></a>
### [Spain frees wealthy US-sought activist on bail as Irish police raid Dublin home](https://www.theguardian.com/world/2026/nov/20/james-fergie-chambers-bail-spain) ⭐️ 8.0/10

Spain released US activist James “Fergie” Chambers on bail while Irish police raided his Dublin home amid US extradition efforts tied to alleged Hamas support and money‑laundering charges.

rss · The Guardian World · Nov 20, 18:34

**Tags**: `#extradition`, `#US`, `#Spain`, `#Ireland`, `#Hamas`

---

<a id="item-world-news-9"></a>
### [EU wants ‘closest possible relationship’ with UK after agreeing Brexit reset deal – live](https://www.theguardian.com/world/live/2026/nov/20/uk-eu-european-union-brexit-deal-andy-burnham-latest-news-updates) ⭐️ 8.0/10

UK and EU agree a Brexit reset deal that deepens economic and political ties, potentially adding £17 bn a year to the UK economy.

rss · The Guardian World · Nov 20, 17:59

**Tags**: `#Brexit`, `#UK-EU relations`, `#trade agreement`, `#economic impact`, `#politics`

---

<a id="item-world-news-10"></a>
### [Burnham seals trade and youth mobility deals in biggest step towards EU since Brexit](https://www.theguardian.com/politics/2026/nov/20/burnham-trade-youth-mobility-deals-biggest-step-towards-eu-since-brexit) ⭐️ 8.0/10

UK and EU seal trade and youth mobility deals at a Brussels summit, marking the biggest step toward deeper ties since Brexit.

rss · The Guardian World · Nov 20, 17:57

**Tags**: `#UK-EU relations`, `#trade agreements`, `#youth mobility`

---