---
layout: default
title: "Horizon Summary: 2026-11-24 (EN)"
date: 2026-11-24
lang: en
---

> From 76 items, 16 important content pieces were selected

---

**Technology News**
1. [vCenter 再曝 9.8 分免鉴权漏洞，几天前刚被零日利用](#item-tech-news-1) ⭐️ 10.0/10
2. [Amazon Acquires Decart to Narrow Silicon Gap with Nvidia](#item-tech-news-2) ⭐️ 9.0/10
3. [Check Point HFS PRNG flaw enables forged admin session cookies](#item-tech-news-3) ⭐️ 8.0/10
4. [Even the best AI agents struggle with everyday life](#item-tech-news-4) ⭐️ 8.0/10
5. [UK warns AI-driven cyberattacks are exposing years of weak security](#item-tech-news-5) ⭐️ 8.0/10
6. [Uber and Nuro start driverless testing of Lucid robotaxis](#item-tech-news-6) ⭐️ 8.0/10
7. [Why a Crusoe investor is betting on solar and batteries to power future AI data centers](#item-tech-news-7) ⭐️ 8.0/10
8. [FCC to impose reciprocal restrictions on foreign satellite operators](#item-tech-news-8) ⭐️ 7.0/10

**World News**
1. [Democrat Victoria Broderick unseats eight-term Republican incumbent in Tennessee to win election](#item-world-news-1) ⭐️ 9.0/10
2. [Huawei found guilty of stealing trade secrets but acquitted of racketeering](#item-world-news-2) ⭐️ 8.0/10
3. [Mali Conflict Claims 349 Russian Soldiers Over Three Years](#item-world-news-3) ⭐️ 8.0/10
4. [EU to impose cap on Chinese hybrid EV imports next month](#item-world-news-4) ⭐️ 8.0/10
5. [Schumer Accuses Nvidia CEO of Export Violations](#item-world-news-5) ⭐️ 8.0/10
6. [Sarkozy, Bruni to Stand Trial Over Gaddafi‑Linked Campaign Finance](#item-world-news-6) ⭐️ 7.0/10
7. [Israeli air strike kills Hamas internal security chief in Gaza](#item-world-news-7) ⭐️ 7.0/10

**Financial News**
1. [Fed President Signals Possible Future Rate Hikes to Reach 2% Inflation Target](#item-finance-news-1) ⭐️ 8.0/10

---

## Technology News

<a id="item-tech-news-1"></a>
### [vCenter 再曝 9.8 分免鉴权漏洞，几天前刚被零日利用](https://thehackernews.com/2026/11/vmware-vcenter-hit-by-another-critical.html) ⭐️ 10.0/10

A 9.8‑rated zero‑day authentication bypass in VMware vCenter has been publicly disclosed and exploited, posing a major security risk for virtualization environments.

telegram · zaihuapd · Nov 24, 14:50

**Tags**: `#security`, `#vulnerability`, `#VMware`, `#zero-day`

---

<a id="item-tech-news-2"></a>
### [Amazon Acquires Decart to Narrow Silicon Gap with Nvidia](https://techcrunch.com/2026/11/24/amazons-decart-acquisition-is-a-bet-on-using-software-to-narrow-the-gap-with-nvidia-in-the-ai-chip-race/) ⭐️ 9.0/10

Amazon announced a $7.5 billion acquisition of Decart, a startup that optimizes AI models for non‑Nvidia chips, marking a strategic effort to reduce dependence on Nvidia’s hardware. Decart had previously raised $300 million in a $4 billion‑valued round that included Nvidia as an investor, and Anthropic had also shown interest. The deal is a planned investment; the technology is not yet deployed in Amazon’s services but signals a shift toward broader silicon compatibility.

rss · TechCrunch · Nov 24, 15:51

**「Decart’s AI‑model‑optimization focus」** Decart is an Israeli AI startup that builds real‑time world‑model infrastructure, concentrating on optimizing generative AI to run with low latency on non‑Nvidia hardware. Its technology enables models to operate faster and at lower cost, which is why Amazon is interested in acquiring it to strengthen its AI infrastructure.

**「Impact」** Amazon’s acquisition enables AWS customers to run AI workloads on a wider range of GPUs, potentially lowering inference costs and giving developers an alternative to Nvidia hardware.

<details><summary>References</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Decart">Decart - Wikipedia</a></li>
<li><a href="https://decart.ai/">Decart - The Live AI Lab the World Runs On</a></li>

</ul>
</details>

**Tags**: `#AI hardware`, `#software optimization`, `#Amazon`, `#Nvidia`, `#Decart`

---

<a id="item-tech-news-3"></a>
### [Check Point HFS PRNG flaw enables forged admin session cookies](https://www.greynoise.io/blog/check-point-security-management-servers-intrusion-campaign) ⭐️ 8.0/10

A new intrusion campaign targets Check Point Security Management Servers by exploiting a flaw in the HFS server’s use of JavaScript’s Math.random\(\) to generate session‑cookie signatures. Attackers repeatedly log in to the HFS loginSrp1 endpoint, capture the resulting signed cookies, reconstruct the V8 PRNG state, recover the internal signing key, and forge a valid admin‑session cookie. The campaign appears to use CVE‑2026‑16232 as an initial vector, though the exact method of first access is not fully confirmed. The vulnerability allows attackers to gain full administrative control of affected Check Point servers that are reachable from the internet.

hackernews · louiereederson · Nov 24, 16:32 · [Discussion](https://news.ycombinator.com/item?id=50630594)

**「Prior authentication bypass vulnerability」** Check Point’s SmartConsole had a documented authentication bypass flaw \(CVE‑2026‑16232\) that allowed attackers to obtain full administrative privileges by exploiting the login process.

**「Impact」** Organizations running Check Point Security Management Servers exposed to the internet risk unauthorized administrative access; they should apply the CVE‑2026‑16232 patch, restrict remote HFS access, and monitor for forged session cookies.

**「Community Discussion」** Commentary by PyWoody provides a detailed technical walk‑through of how the PRNG flaw is exploited to forge admin session cookies.

<details><summary>References</summary>
<ul>
<li><a href="https://nvd.nist.gov/vuln/detail/cve-2026-16232">NVD-CVE-2026-16232</a></li>
<li><a href="https://support.checkpoint.com/results/sk/sk185169">sk185169 - CVE-2026-16232 - Authentication bypass with ...</a></li>
<li><a href="https://www.sentinelone.com/vulnerability-database/cve-2026-16232/">CVE-2026-16232: Check Point SmartConsole Auth Bypass</a></li>

</ul>
</details>

**Tags**: `#security`, `#vulnerability`, `#software engineering`, `#cybersecurity`, `#systems`

---

<a id="item-tech-news-4"></a>
### [Even the best AI agents struggle with everyday life](https://techcrunch.com/2026/11/24/even-the-best-ai-agents-struggle-with-everyday-life/) ⭐️ 8.0/10

ShellBench reveals that even advanced AI agents struggle with everyday tasks, underscoring safety and reliability challenges for personal assistants.

rss · TechCrunch · Nov 24, 21:33

**Tags**: `#AI`, `#personal assistants`, `#benchmarks`, `#safety`, `#research`

---

<a id="item-tech-news-5"></a>
### [UK warns AI-driven cyberattacks are exposing years of weak security](https://techcrunch.com/2026/11/24/uk-warns-ai-driven-cyberattacks-are-exposing-years-of-weak-security/) ⭐️ 8.0/10

UK’s cybersecurity unit warns of a surge in AI‑driven attacks exploiting weak defenses, underscoring a growing threat to software and system security.

rss · TechCrunch · Nov 24, 18:02

**Tags**: `#cybersecurity`, `#AI`, `#cyberattacks`, `#NCSC`, `#UK`

---

<a id="item-tech-news-6"></a>
### [Uber and Nuro start driverless testing of Lucid robotaxis](https://techcrunch.com/2026/11/24/uber-and-nuro-begin-driverless-testing-of-lucid-robotaxis-ahead-of-2027-launch/) ⭐️ 8.0/10

Uber and Nuro have begun driverless testing of Lucid Gravity SUVs on public streets in the San Francisco Bay Area, after receiving a permit to remove the safety driver. The test marks a key step toward a commercial robotaxi service slated for Q1 2027, and the companies plan to offer driverless rides to employees shortly. The move follows Uber’s 2025 investment of $300 million in Lucid and its earlier announcement of a premium robotaxi plan using Nuro‑developed autonomous technology.

rss · TechCrunch · Nov 24, 16:40

**「Prior partnership and permit」** In 2025 Uber announced a $300 million investment in Lucid and a partnership with Nuro to equip Lucid Gravity SUVs with autonomous technology for a planned robotaxi service, and in 2026 the California DMV granted a permit allowing the vehicles to be tested without a safety driver.

**「Impact」** The driverless testing removes the safety driver, allowing Uber and Nuro to validate autonomous operation in real traffic and prepare for employee rides, bringing the companies closer to a commercial launch.

<details><summary>References</summary>
<ul>
<li><a href="https://lucidmotors.com/stories/lucid-nuro-uber-partner">Lucid , Nuro &amp; Uber Launch Robotaxis | Lucid Motors</a></li>
<li><a href="https://electrek.co/guides/nuro/">Nuro | Electrek</a></li>
<li><a href="https://techcrunch.com/2025/07/17/uber-makes-multi-million-dollar-investment-in-lucid-nuro-to-build-robotaxi-service/">Uber makes multimillion-dollar investment in Lucid and Nuro to build...</a></li>

</ul>
</details>

**Tags**: `#autonomous vehicles`, `#driverless cars`, `#robotaxi`, `#Uber`, `#Nuro`

---

<a id="item-tech-news-7"></a>
### [Why a Crusoe investor is betting on solar and batteries to power future AI data centers](https://techcrunch.com/2026/11/24/why-a-crusoe-investor-is-betting-on-solar-and-batteries-to-power-future-ai-data-centers/) ⭐️ 8.0/10

A Crusoe investor is backing solar and battery solutions to meet the growing power demands of AI data centers, reflecting a notable shift toward renewable energy in AI infrastructure.

rss · TechCrunch · Nov 24, 16:10

**Tags**: `#AI infrastructure`, `#renewable energy`, `#data centers`, `#investment`, `#technology`

---

<a id="item-tech-news-8"></a>
### [FCC to impose reciprocal restrictions on foreign satellite operators](https://www.theregister.com/networks/2026/11/24/fcc-proposes-tit-for-tat-restrictions-on-foreign-satellite-operators/5311889) ⭐️ 7.0/10

The FCC will vote in December to launch a reciprocal restriction program that would impose equal limits on domestic operators whenever foreign satellite operators restrict U.S. suppliers. The proposal is aimed at countering the EU’s 2 GHz spectrum plan that would bar SpaceX and Amazon LEO from using the band. The measure would apply to any foreign operator that limits U.S. companies, potentially affecting SpaceX, Amazon LEO, and other U.S. satellite operators.

telegram · zaihuapd · Nov 24, 15:12

**「Background」** The EU’s 2 GHz spectrum plan requires that two‑thirds of the band be reserved for domestic operators, excluding SpaceX and Amazon LEO, prompting the U.S. to consider a tit‑for‑tat response.

**「Impact」** If enacted, U.S. satellite operators such as SpaceX and Amazon LEO could face restrictions on their U.S. supply chains or market access if foreign operators impose similar limits, potentially limiting their ability to procure equipment or sell services in those markets.

**Tags**: `#regulation`, `#satellite`, `#FCC`, `#EU`, `#spectrum`

---

## World News

<a id="item-world-news-1"></a>
### [Democrat Victoria Broderick unseats eight-term Republican incumbent in Tennessee to win election](https://www.theguardian.com/us-news/2026/nov/24/democrat-victoria-broderick-election-win-tennesee-midterms) ⭐️ 9.0/10

Democrat Victoria Broderick defeats long‑time Republican incumbent Scott DesJarlais in Tennessee’s 4th district, boosting the Democratic majority in the U.S. House.

rss · The Guardian World · Nov 24, 20:20

**Tags**: `#US politics`, `#midterm elections`, `#House of Representatives`, `#Tennessee`, `#political upset`

---

<a id="item-world-news-2"></a>
### [Huawei found guilty of stealing trade secrets but acquitted of racketeering](https://www.bbc.co.uk/news/articles/cmy49ngydqzpo?at_medium=RSS&amp;at_campaign=rss) ⭐️ 8.0/10

Huawei was convicted of trade‑secret theft and bank fraud, but cleared of racketeering in a landmark U.S. trial.

rss · BBC World · Nov 24, 21:32

**Tags**: `#Huawei`, `#US trial`, `#trade secrets`, `#China-US relations`, `#technology`

---

<a id="item-world-news-3"></a>
### [Mali Conflict Claims 349 Russian Soldiers Over Three Years](https://www.theguardian.com/world/2026/nov/24/russian-fighters-killed-in-mali-africa-leaked-data) ⭐️ 8.0/10

A leaked report released on 24 November 2026 lists 349 Russian military deaths in Mali over a three‑year period, confirming a significant loss of personnel in the country’s ongoing conflict. The data were obtained from records held by Russia’s Africa Corps and were made public by The Guardian. No additional casualties have been reported beyond the 349 figure, and the report does not attribute the deaths to any specific incident beyond the overall tally.

rss · The Guardian World · Nov 24, 16:00

**「Russia’s Africa Corps in Mali」** Russia’s Africa Corps has operated in Mali since 2021, with troops based in northern Togo and equipment shipped through Lomé, and has been involved in combat against insurgent forces in the north. Mali has also paid Russia approximately $10 million a month for Wagner’s assistance in the conflict.

**「Impact」** The high casualty count may prompt Moscow to reassess its military engagement in Africa, potentially leading to a shift in Russian foreign policy toward the continent and affecting the stability of Mali’s junta government.

<details><summary>References</summary>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Africa_Corps_%28Russia%29">Africa Corps ( Russia ) - Wikipedia</a></li>
<li><a href="https://www.yahoo.com/news/articles/russias-africa-corps-fights-mali-052131039.html">As Russia &#x27;s Africa Corps fights in Mali , witnesses describe atrocities...</a></li>

</ul>
</details>

**Tags**: `#Russia`, `#Mali`, `#military casualties`, `#foreign policy`, `#African conflict`

---

<a id="item-world-news-4"></a>
### [EU to impose cap on Chinese hybrid EV imports next month](https://www.theguardian.com/business/2026/nov/24/eu-cap-chinese-hybrid-ev-imports-tariff-uk) ⭐️ 8.0/10

The EU will impose quotas on Chinese hybrid electric vehicles next month, also affecting hybrids from Japan, Turkey, South Korea and the UK.

rss · The Guardian World · Nov 24, 10:59

**Tags**: `#EU trade policy`, `#electric vehicles`, `#China`, `#automotive industry`, `#global trade`

---

<a id="item-world-news-5"></a>
### [Schumer Accuses Nvidia CEO of Export Violations](https://www.theguardian.com/technology/2026/nov/24/nvidia-jensen-huang-congress) ⭐️ 8.0/10

Senate Minority Leader Chuck Schumer accused Nvidia CEO Jensen Huang of shipping advanced chips to China, alleging a violation of U.S. export control laws. Schumer compared the alleged shipments to selling rocket engines to the Soviets during the space race. The claim is an allegation; no official investigation has yet been announced.

rss · The Guardian World · Nov 24, 20:05

**「Nvidia’s export‑control context」** Nvidia has recently set up an export‑control panel after the U.S. government barred sales of its highest‑tier chips to China, and the Trump administration tightened restrictions on indirect transfers of advanced chips to the country.

<details><summary>References</summary>
<ul>
<li><a href="https://www.cbsnews.com/news/nvidia-export-control-committee-china-chips/">Nvidia forms export control panel amid concerns over China sales</a></li>
<li><a href="https://apnews.com/article/nvidia-export-controls-chips-china-remote-access-60f868d3bb430b85a8657b27d421096e">Trump administration moves to restrict China from indirect ...</a></li>

</ul>
</details>

**Tags**: `#US politics`, `#technology`, `#export controls`, `#China`, `#Nvidia`

---

<a id="item-world-news-6"></a>
### [Sarkozy, Bruni to Stand Trial Over Gaddafi‑Linked Campaign Finance](https://www.bbc.co.uk/news/articles/c65y17pwv1z7o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 7.0/10

Nicolas Sarkozy and his wife Carla Bruni‑Sarkozy will stand trial in Paris next year on charges related to alleged campaign‑finance violations involving money from former Libyan dictator Muammar Gaddafi. The case stems from Sarkozy’s 2025 conviction for conspiring to fund his 2012 presidential campaign with Gaddafi funds, and the pair are accused of retracting testimony from a key witness. Both deny wrongdoing. The trial is scheduled for 2027, following Sarkozy’s 5‑year sentence in September 2025.

rss · BBC World · Nov 24, 16:49

**「Background on Sarkozy&\#x27;s 2007 campaign finance case」** Nicolas Sarkozy served as France’s president from 2007 to 2012 and was later convicted of conspiring to fund his 2007 election campaign with money from former Libyan dictator Muammar Gaddafi. He received a five‑year prison sentence in September 2023, becoming the first former French president to be jailed, though he served only 20 days. The case centers on allegations that he covered up the Gaddafi‑linked funding and that a key witness was coerced to retract incriminating testimony.

**「Impact」** The case establishes a legal precedent for holding former presidents accountable for campaign‑finance violations.

<details><summary>References</summary>
<ul>
<li><a href="https://www.elysee.fr/en/nicolas-sarkozy">Nicolas Sarkozy | Élysée</a></li>
<li><a href="https://williambowles.info/2018/03/30/frances-bling-bling-sarkozy-haunted-by-ghost-of-gaddafi-by-finian-cunningham/">France’s Bling-Bling Sarkozy Haunted by Ghost of Gaddafi By Finian...</a></li>

</ul>
</details>

**Tags**: `#politics`, `#France`, `#legal`, `#former president`, `#campaign finance`

---

<a id="item-world-news-7"></a>
### [Israeli air strike kills Hamas internal security chief in Gaza](https://www.bbc.co.uk/news/articles/c6rrg7ggq190o?at_medium=RSS&amp;at_campaign=rss) ⭐️ 7.0/10

Israeli air strike killed Hamas internal security chief Naeem Abu Nahel in Gaza, marking a high‑level blow to Hamas leadership.

rss · BBC World · Nov 24, 15:35

**Tags**: `#Israel-Hamas conflict`, `#Gaza`, `#military strike`, `#Hamas leadership`, `#regional security`

---

## Financial News

<a id="item-finance-news-1"></a>
### [Fed President Signals Possible Future Rate Hikes to Reach 2% Inflation Target](https://www.cnbc.com/2026/11/23/john-williams-fed-inflation-rate-hikes.html) ⭐️ 8.0/10

Fed President John Williams said higher interest rates may be needed over time to bring inflation to the Fed&\#x27;s 2% target by 2027.

rss · CNBC Finance · Nov 24, 13:33

**「Background」** Williams reiterated earlier comments that inflation should reach 2% in 2027, with further tightening likely as the economy grows.

**Tags**: `#Fed`, `#interest rates`, `#inflation`, `#monetary policy`

---