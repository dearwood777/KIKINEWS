---
layout: default
title: "Horizon Summary: 2026-11-11 (EN)"
date: 2026-11-11
lang: en
---

> From 70 items, 5 important content pieces were selected

---

**Technology News**
1. [Anthropic Reveals Multi‑Chip Strategy for Claude in IPO Video](#item-tech-news-1) ⭐️ 8.0/10
2. [Databricks launches Genie AI agent with multi‑step, ontology‑driven capabilities](#item-tech-news-2) ⭐️ 8.0/10
3. [New York&\#x27;s RAISE Act Requires Registration and Incident Reporting from Large AI Labs](#item-tech-news-3) ⭐️ 8.0/10
4. [DeepMind uses AI to formally verify key parts of Signal protocol](#item-tech-news-4) ⭐️ 8.0/10

**Financial News**
1. [Fed&\#x27;s Goolsbee calls inflation report &quot;borderline disturbing&quot;](#item-finance-news-1) ⭐️ 8.0/10

---

## Technology News

<a id="item-tech-news-1"></a>
### [Anthropic Reveals Multi‑Chip Strategy for Claude in IPO Video](https://simonwillison.net/2026/Nov/11/anthropic-ipo-roadshow/) ⭐️ 8.0/10

Anthropic’s IPO roadshow video confirms that the company trains and serves its Claude models on four major chip families—AWS Trainium, Google TPUs, NVIDIA GPUs, and AMD GPUs—by using a long‑standing multi‑chip strategy. The video explains that Anthropic’s internal Mythos system can port Claude to a new hardware platform \(e.g., AMD GPUs\) in just three days with virtually no human intervention, demonstrating a highly automated software stack. It also introduces the concept of &quot;compute multipliers,&quot; where discovered efficiencies multiply effective compute capacity, and suggests future self‑discovery of such multipliers by the model itself. This operational detail is new public information for AI engineers, cloud providers, and hardware vendors.

rss · Simon Willison · Nov 11, 15:11

**「Prerequisite: Multi‑chip compute strategy」** Anthropic’s multi‑chip approach builds on the industry practice of running large language models on different hardware families to maximize compute capacity and cost efficiency. The company first hinted at this strategy in a September post‑mortem that described bugs affecting only its TPU deployments, indicating early experimentation with heterogeneous hardware before expanding to AWS Trainium, NVIDIA and AMD GPUs as disclosed in the IPO roadshow video.

**「Impact」** AI teams that rely on a single hardware vendor may need to reconsider multi‑chip approaches to achieve similar flexibility and cost efficiency, and cloud providers could see increased demand for supporting diverse accelerator ecosystems as Anthropic’s model demonstrates viable cross‑chip deployment at scale.

**Tags**: `#AI`, `#Compute`, `#Hardware`, `#Cloud`

---

<a id="item-tech-news-2"></a>
### [Databricks launches Genie AI agent with multi‑step, ontology‑driven capabilities](https://techcrunch.com/2026/11/11/databricks-new-ai-agent-tells-ceo-ali-ghodsi-the-unvarnished-truth/) ⭐️ 8.0/10

Databricks unveiled an updated Genie AI agent that can execute multi‑step jobs by using an internal ontology to provide contextual understanding of the data customers store on the Databricks platform. The agent is positioned as an always‑on assistant for corporate leaders, allowing them to assign a wide range of tasks that it completes unsupervised, such as analyzing employee‑satisfaction surveys, summarizing sales pitches, and preparing interview briefings. Databricks also highlighted that usage costs can be managed through its Unity Gateway product, which lets organizations set limits and swap in cheaper open‑weight models.

rss · TechCrunch · Nov 11, 15:00

**「Background」** Genie is Databricks’ AI‑agent product that lets users issue natural‑language commands to run data‑engineering and analytics tasks on the Databricks platform. The new version adds an ontology—a structured knowledge graph of the customer’s stored data and metadata—so the agent can maintain context across multi‑step workflows. Databricks also bundles the agent with Unity Gateway, its enterprise AI gateway that lets organizations set usage limits and switch to lower‑cost open‑weight models to control spending on AI agents.

**「Impact」** Business leaders can now rely on Genie to surface unfiltered insights from internal data—such as low‑scoring survey areas or failed sales calls—without needing to solicit feedback directly, while the Unity Gateway controls help prevent runaway AI‑driven expenses.

<details><summary>References</summary>
<ul>
<li><a href="https://www.databricks.com/product/artificial-intelligence/unity-gateway">Unity Gateway: Databricks AI gateway for cost and security</a></li>

</ul>
</details>

**Tags**: `#Databricks`, `#AI agents`, `#Data engineering`, `#Enterprise AI`

---

<a id="item-tech-news-3"></a>
### [New York&\#x27;s RAISE Act Requires Registration and Incident Reporting from Large AI Labs](https://techcrunch.com/2026/11/10/openai-anthropic-face-new-oversight-as-new-yorks-ai-safety-law-takes-effect/) ⭐️ 8.0/10

New York has opened a registration portal for the RAISE Act, obligating large frontier AI developers—defined as companies with over $500 million in annual revenue such as OpenAI and Anthropic—to register by January 1, 2027. The law also mandates publishing safety frameworks on their websites, issuing public model‑transparency reports, and reporting critical safety incidents within 72 hours. Enforcement will be handled by the newly created Office of Digital Innovation, Governance, Integrity, and Trust \(DIGIT\), with penalties of up to $1 million for a first violation and $3 million for subsequent violations. The state simultaneously launched the New York Center for AI Responsibility and Research to evaluate AI safety independently.

rss · TechCrunch · Nov 10, 20:52

**「Prerequisite AI safety regulations in New York」** The RAISE Act builds on earlier New York AI safety legislation, such as the 2025 law that required AI chatbots to disclose they are non‑human and to monitor for suicidal ideation, and the 2026 chatbot‑for‑minors law that restricts deceptive or harmful interactions. Those prior statutes created the state’s enforcement framework and the Office of Digital Innovation, Governance, Integrity, and Trust \(DIGIT\), which now administers the new registration and reporting requirements for frontier AI developers.

**「Impact」** Affected companies must build compliance pipelines to publish frameworks, monitor incidents in real time, and submit reports within the tight 72‑hour window, or risk multi‑million‑dollar fines and enforcement actions.

<details><summary>References</summary>
<ul>
<li><a href="https://techcrunch.com/2026/11/10/openai-anthropic-face-new-oversight-as-new-yorks-ai-safety-law-takes-effect/">OpenAI, Anthropic face new oversight as New York’s AI safety ...</a></li>
<li><a href="https://casrai.org/guides/new-york-raise-act-explained">New York RAISE Act: What It Requires — CASRAI</a></li>

</ul>
</details>

**Tags**: `#AI regulation`, `#AI safety`, `#Industry policy`

---

<a id="item-tech-news-4"></a>
### [DeepMind uses AI to formally verify key parts of Signal protocol](https://arstechnica.com/ai/2026/11/signals-encryption-just-passed-an-ai-powered-mathematical-checkup/) ⭐️ 8.0/10

Google DeepMind researchers applied their new AI framework AlphaProof Code to formally verify several core cryptographic guarantees of the Signal protocol, completing the proof‑of‑concept in about four weeks. The AI‑assisted analysis proved the targeted properties, found no new vulnerabilities, and correctly identified known, already‑fixed flaws in older protocol versions. The verification covers only selected components of the protocol—not the entire Signal mobile app—and the team released the specification and proof for reuse by other formal‑verification efforts.

rss · Ars Technica · Nov 11, 14:08

**「Formal verification and AI assistance」** Formal verification uses mathematical proofs—often written in proof assistants such as Lean—to guarantee that software behaves as specified, a process that traditionally required extensive manual modeling of code and properties. Recent AI‑driven frameworks, like DeepMind’s AlphaProof Code, automate the translation of live code into Lean theorems using agentic AI, enabling much faster verification of larger codebases such as the Signal protocol. This capability builds on earlier manual efforts to verify cryptographic primitives but had not been applied at the scale of a widely deployed messaging protocol before.

**「Impact」** By releasing the verified specification and proof, DeepMind provides a concrete artifact that other cryptographers and security engineers can build on, potentially accelerating AI‑aided formal verification of similar communication protocols.

<details><summary>References</summary>
<ul>
<li><a href="https://explainx.ai/blog/google-deepmind-alphaproof-code-signal-protocol-formal-verification-2026">AlphaProof Code: Signal Protocol Verified in 4 Weeks ...</a></li>
<li><a href="https://deepmind.google/blog/introducing-alphaproof-code/">Formal Verification of Signal’s Protocol with Gemini</a></li>

</ul>
</details>

**Tags**: `#AI`, `#formal verification`, `#cryptography`, `#software security`, `#Signal`

---

## Financial News

<a id="item-finance-news-1"></a>
### [Fed&\#x27;s Goolsbee calls inflation report &quot;borderline disturbing&quot;](https://www.cnbc.com/2026/11/11/goolsbee-october-inflation-fed-rates-disturbing-distressing.html) ⭐️ 8.0/10

Chicago Fed President Austan Goolsbee said the October consumer price index rose 0.4% seasonally adjusted, calling the result &quot;borderline disturbing.&quot;

rss · CNBC Finance · Nov 11, 16:49

**「Background」** The Fed had lifted its policy rate to a 3.75‑4% range in September and held it steady in October as inflation remained above target.

**「Impact」** Fed funds futures now price a 15% chance of a half‑point rate hike in December and a 60% chance of rates reaching 4.25‑4.5% by January, affecting borrowing costs for households and businesses.

**Tags**: `#inflation`, `#Federal Reserve`, `#monetary policy`, `#CPI`

---