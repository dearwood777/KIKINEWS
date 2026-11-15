#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从当天这期日报里挑出“难点词汇”，生成 docs/vocab.html。

每张卡片包含：单词 + 音标 + 一键发音 + 词性 + 稀有度 + 中文释义 + 英文释义/例句
+ 这个词在当天新闻里的原文语境句（高亮）。

释义只用本地词库（ECDICT，英汉双解 CSV）查表，英文释义/例句来自免费公开词典接口
（dictionaryapi.dev，Wiktionary 数据，无需密钥、不产生任何模型 token）。
接口不通时自动降级，页面照常生成。

用法（在仓库根目录执行）：
    python scripts/build_vocab.py
词库位置：默认 data/ecdict.csv，可用环境变量 ECDICT_PATH 覆盖。
关闭联网补全：VOCAB_NO_NET=1
"""
from __future__ import annotations

import csv
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_latest import DOCS, POSTS, digest_display  # noqa: E402

FRONT_MATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.S)
LINK_MD = re.compile(r"\[([^\]]*)\]\([^)]*\)")
TOKEN = re.compile(r"[A-Za-z][A-Za-z'\-]{2,}")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

# 太常见的功能词，任何词表都不该收
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "have", "has", "had", "was", "were",
    "are", "been", "will", "would", "could", "should", "there", "their", "them", "they", "his",
    "her", "its", "our", "your", "who", "what", "when", "where", "which", "while", "about",
    "into", "over", "than", "then", "also", "such", "some", "more", "most", "much", "many",
    "very", "just", "only", "even", "still", "after", "before", "during", "between", "under",
    "because", "however", "therefore", "according", "said", "says", "say", "one", "two", "new",
    "now", "get", "got", "make", "made", "use", "used", "using", "may", "might", "must",
    "can", "not", "but", "you", "all", "any", "out", "off", "own", "same", "other", "these",
}

MAX_WORDS = 80
MAX_SENSE_WORDS = 6
# 词频排位在多少名以内算“C1 已认识”。两套词频任一进入该名次即视为已知。
COMMON_RANK = 8000
# 熟词生义只看排名 3500 之后的词：ceiling / rate 这类太基础的，即使在新闻里有专业义也不列。
NEWS_SENSE_MIN_RANK = 3500
ENRICH_CACHE = os.path.join("data", "vocab_enrich.json")

# C1/专八读者本来就该认识的日常词与科技常用词。词库词频排位对这类词偏宽松
# （demo 排到 12000 名之后），单靠 frq/bnc 会把它们放进来，这里显式兜底排除。
COMMON_WORDS = {
    "demo", "demos", "backup", "backups", "email", "emails", "million", "millions",
    "billion", "billions", "startup", "startups", "platform", "platforms", "update",
    "updates", "upgrade", "upgrades", "release", "released", "releases", "launch",
    "launched", "feature", "features", "server", "servers", "cloud", "clouds",
    "device", "devices", "network", "networks", "networked", "online", "offline",
    "software", "hardware", "chip", "chips", "data", "dataset", "datasets",
    "user", "users", "customer", "customers", "market", "markets", "company",
    "companies", "business", "businesses", "industry", "industries", "economy",
    "government", "governments", "official", "officials", "policy", "policies",
    "report", "reports", "reported", "statement", "statements", "announce",
    "announced", "confirm", "confirmed", "deny", "denied", "claim", "claimed",
    "warning", "warnings", "risk", "risks", "issue", "issues", "problem", "problems",
    "solution", "solutions", "system", "systems", "service", "services", "product",
    "products", "project", "projects", "process", "processes", "result", "results",
    "increase", "increased", "decrease", "decreased", "growth", "decline",
    "support", "supported", "supporting", "require", "required", "provide",
    "provided", "include", "included", "including", "allow", "allowed", "enable",
    "enabled", "ensure", "ensured", "improve", "improved", "reduce", "reduced",
    "protect", "protected", "prevent", "prevented", "cause", "caused", "affect",
    "affected", "impact", "impacted", "impacting", "leading", "leader", "leaders",
    "leadership", "major", "majors", "majority", "majorities", "minor", "minority",
    "notify", "notified", "notification", "notifications", "dashboard", "dashboards",
    "connectivity", "functionality", "natively", "canceling", "canceling", "cancelled",
    "canceled", "healthcare", "health", "outage", "outages", "cascade", "cascades",
    "glitch", "glitches", "sending", "sender", "receiver", "volume", "traffic",
    "content", "contents", "contented", "account", "accounts", "budget", "budgets",
    "quarter", "quarterly", "annual", "annually", "monthly", "weekly", "daily",
    "measure", "measures", "policy", "standard", "standards", "framework",
    "sector", "sectors", "global", "globally", "region", "regional", "national",
    "international", "domestic", "foreign", "economic", "political", "military",
    "security", "defense", "trade", "export", "exports", "exported", "import",
    "imports", "tariff", "tariffs", "sanction", "sanctions", "agreement",
    "agreements", "negotiate", "negotiated", "negotiation", "negotiations",
    "challenge", "challenges", "challenged", "challenger", "challengers",
    "response", "responses", "respond", "responded", "comment", "comments",
    "commenting", "statement", "briefing", "analysis", "analyst", "analysts",
    "estimate", "estimates", "forecast", "forecasts", "investor", "investors",
    "investment", "investments", "funding", "revenue", "revenues", "profit",
    "losses", "share", "shares", "stock", "stocks", "price", "prices", "cost",
    "costs", "demand", "supply", "manufacture", "manufacturer", "manufacturers",
    "production", "productivity", "capacity", "capacities", "efficiency",
    "infrastructure", "regulation", "regulations", "regulator", "regulators",
    "compliance", "legal", "illegal", "court", "courts", "lawsuit", "laws",
    "investigate", "investigation", "investigated", "allege", "alleged",
    "accused", "charge", "charges", "charged", "sentence", "sentenced",
    "election", "elections", "vote", "votes", "voters", "campaign", "campaigns",
    "minister", "ministers", "parliament", "senate", "congress", "president",
    "senator", "governor", "ambassador", "summit", "treaty", "alliance",
    "coalition", "protest", "protests", "conflict", "conflicts", "ceasefire",
    "troops", "forces", "weapons", "strike", "strikes", "attack", "attacks",
    "attacked", "bombing", "casualties", "refugee", "refugees", "humanitarian",
    "earthquake", "flood", "floods", "hurricane", "wildfire", "wildfires",
    "climate", "emission", "emissions", "carbon", "renewable", "energy",
    "electricity", "nuclear", "reactor", "satellite", "satellites", "orbit",
    "launch", "launches", "mission", "missions", "spacecraft", "astronaut",
    "algorithm", "algorithms", "model", "models", "training", "trained",
    "dataset", "compute", "computing", "processor", "processor", "memory",
    "storage", "bandwidth", "encryption", "privacy", "privacies", "secure",
    "security", "vulnerability", "vulnerabilities", "breach", "breaches",
    "malware", "ransomware", "phishing", "hacker", "hackers", "hacking",
    "patch", "patches", "bug", "bugs", "debug", "deploy", "deployed", "deployment",
    "migration", "migrate", "architecture", "architectures", "protocol",
    "protocols", "interface", "interfaces", "application", "applications",
    "browser", "browsers", "mobile", "desktop", "tablet", "console",
    "subscribe", "subscription", "subscriptions", "license", "licenses",
    "patent", "patents", "copyright", "trademark", "supplier", "suppliers",
    "logistics", "shipment", "shipments", "container", "containers", "freight",
    "airline", "airlines", "airport", "airports", "port", "ports", "railway",
    "vehicle", "vehicles", "automaker", "automakers", "factory", "factories",
    "plant", "plants", "mining", "agriculture", "harvest", "drought", "droughts",
    "pandemic", "vaccine", "vaccines", "virus", "viruses", "infection", "outbreak",
    "hospital", "hospitals", "patient", "patients", "doctor", "doctors",
    "treatment", "treatments", "diagnosis", "therapy", "symptom", "symptoms",
    # 现代日常/科技词，词频表对它们偏宽松，单独兜底排除
    "ecosystem", "ecosystems", "password", "passwords", "scanner", "scanners",
    "timeline", "timelines", "cookie", "cookies", "cooky", "crypto",
    "executable", "executables", "credentials", "thousand", "thousands",
    "hundred", "hundreds", "chopstick", "chopsticks", "abort", "aborted",
    "booster", "boosters", "negotiator", "negotiators", "legislator", "legislators",
    "centralize", "centralized", "governorship", "keyless", "unconfirmed",
    "unauthorized", "unauthorised", "confirm", "authorize", "authorized",
    "reload", "reset", "upload", "download", "install", "installer", "setup",
    "config", "configure", "configured", "click", "tap", "login", "logout",
    "inbox", "spam", "popup", "banner", "widget", "widgets",
    # 品牌名 / 缩写 / 一眼就懂的科技词
    "google", "app", "apps", "metadata", "reusable", "reuse", "sideline",
    "sidelines", "chopstick", "chopsticks", "twitter", "facebook", "tesla",
    "nvidia", "openai", "chatgpt", "iphone", "android", "windows", "linux",
    "github", "youtube", "tiktok", "spotify", "amazon",
}


def newest_post(lang: str = "en") -> str | None:
    if not os.path.isdir(POSTS):
        return None
    files = [f for f in os.listdir(POSTS) if f.endswith(f"-summary-{lang}.md")]
    if not files:
        return None
    files.sort()
    return os.path.join(POSTS, files[-1])


def read_prose(path: str) -> str:
    text = open(path, encoding="utf-8").read()
    text = FRONT_MATTER.sub("", text)
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s == "---":
            continue
        if s.startswith("title:") or s.startswith("layout:") or s.startswith("date:"):
            continue
        if re.match(r"^\*\*(?:标签|Tags|Tag)\*\*", s):
            continue
        if s.startswith("<details") or s.startswith("</details"):
            continue
        if s.startswith("### ") or s.startswith("**") and s.endswith("**"):
            continue
        if s.startswith("> "):
            s = s[2:]
        # 清掉正文里的标记残留：来源前缀、HTML 标签、Markdown 粗体、零宽字符
        s = re.sub(r"^\s*rss\s*·.*?·\s*[A-Za-z]{3,9}\s*\d{1,2},\s*\d{2}:\d{2}\s*", "", s)
        s = re.sub(r"<[^>]*>", "", s)
        s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
        s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
        s = s.replace("\u200b", "").replace("\xa0", " ").replace("\u2011", "-")
        s = LINK_MD.sub(r"\1", s)
        lines.append(s)
    return "\n".join(lines)


def candidates_from(text: str) -> set[str]:
    words = set()
    for m in TOKEN.finditer(text):
        w = m.group(0).strip("'-").lower()
        if len(w) < 4 or w in STOPWORDS or "-" in w:
            continue
        words.add(w)
        # 简单变形还原，让词库扫描能命中原形行
        for suf, cut in (("ing", 3), ("ied", 3), ("ies", 3), ("ed", 2), ("es", 2), ("s", 1)):
            if len(w) > cut + 3 and w.endswith(suf):
                words.add(w[:-cut])
    return words


def scan_dict(dict_path: str, wanted: set[str]):
    """流式扫一遍词库，返回 (原形词条, 变形→可能的原形列表, 原形→变形列表)。

    只保留**原形**词条用于出词表：countries/parties 这类变形行的音标、词频常常缺失，
    而且它们的出现频率应该按原形（country/party）来判断，否则会把极常见的词收进来。
    同一个变形可能对应多个原形（does → do / doe），先都记下，稍后按词频挑最可能的。
    """
    bases: dict[str, dict] = {}
    rev_multi: dict[str, list[str]] = {}
    forms_of: dict[str, list[str]] = {}
    if not os.path.exists(dict_path):
        return bases, rev_multi, forms_of
    with open(dict_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            word = (row.get("word") or "").strip().lower()
            if not word:
                continue
            forms = []
            base_of_row = ""
            for part in (row.get("exchange") or "").split("/"):
                if ":" not in part:
                    continue
                key, val = part.split(":", 1)
                val = val.strip().lower()
                # 0:xxx 表示“本行是 xxx 的变形”，即本行自己的原形
                if key.strip() == "0":
                    base_of_row = val
                elif val:
                    forms.append(val)
            if word not in wanted and not any(f in wanted for f in forms):
                continue
            bases[word] = {
                "word": word,
                "phonetic": (row.get("phonetic") or "").strip(),
                "translation": (row.get("translation") or "").strip(),
                "collins": (row.get("collins") or "0").strip(),
                "oxford": (row.get("oxford") or "0").strip(),
                "tag": (row.get("tag") or "").strip(),
                "pos": (row.get("pos") or "").strip(),
                "frq": int((row.get("frq") or "0").strip() or 0),
                "bnc": int((row.get("bnc") or "0").strip() or 0),
            }
            if base_of_row:
                rev_multi.setdefault(word, []).append(base_of_row)
            for fm in forms:
                rev_multi.setdefault(fm, []).append(word)
            if forms:
                forms_of.setdefault(word, []).extend(forms)
    return bases, rev_multi, forms_of


def phonetic_guesses(word: str) -> list[str]:
    """变形词缺音标时，猜几个可能的原形拼法（只对规则后缀，避免把 startup 猜成 start）。"""
    out = []
    for suf, cut in (("ing", 3), ("ied", 3), ("ies", 3), ("ed", 2), ("es", 2), ("s", 1)):
        if word.endswith(suf) and len(word) > cut + 3:
            stem = word[:-cut]
            out.append(stem)
            out.append(stem + "e")
            if stem and stem[-1] == stem[-2] if len(stem) > 1 else False:
                out.append(stem[:-1])
    return [w for w in out if w != word]


def is_hard(entry: dict) -> bool:
    if not entry["translation"]:
        return False
    if entry["word"] in COMMON_WORDS:
        return False
    trans = entry["translation"]
    for marker in ("[人名]", "[地名]", "[姓氏]", "[缩写]"):
        if trans.startswith(marker):
            return False
    tags = entry["tag"]
    if any(t in tags for t in ("zk", "gk", "cet4")):
        return False
    # 六级词按“新闻里常见的书面语”标准保留：真正生僻的留，词频靠前的（C1 早就认识的）仍排除
    if "cet6" in tags and is_common(entry):
        return False
    if (entry.get("oxford") or "0").strip() == "1":
        return False
    try:
        if int(entry["collins"] or 0) >= 2:
            return False
    except ValueError:
        pass
    frq = entry["frq"]
    bnc = entry.get("bnc", 0)
    # 两套词频（当代语料 frq / 英式语料 bnc）任一显示为常用词，就说明它不该进超纲词表。
    # does → do、millions → million 这类常见词，靠这一步排除。
    if frq >= 9000 or bnc >= 9000:
        return True
    if frq > 0 or bnc > 0:
        return False
    # 两套词频都查不到：短词多是缩写或变形残渣，不收
    if len(entry["word"]) < 6:
        return False
    return True


def is_common(entry: dict) -> bool:
    """C1/专八读者基本认识：有牛津标注、Collins 星级够、或两套词频都靠前。"""
    if not entry:
        return False
    if entry["word"] in COMMON_WORDS:
        return True
    if (entry.get("oxford") or "0").strip() == "1":
        return True
    try:
        if int(entry.get("collins") or 0) >= 2:
            return True
    except ValueError:
        pass
    for key in ("frq", "bnc"):
        v = entry.get(key, 0)
        if 0 < v <= COMMON_RANK:
            return True
    return False


DERIV_PREFIXES = ("un", "in", "im", "non", "dis", "mis", "re", "pre", "over",
                  "under", "anti", "co", "sub", "de", "multi", "semi", "post",
                  "inter", "intra", "hyper", "ultra", "auto", "micro", "macro")
DERIV_SUFFIXES = ("ization", "isation", "ation", "ition", "ship", "ness", "ment",
                  "able", "ible", "less", "like", "ward", "wise", "ally", "ity",
                  "ive", "ous", "ful", "ize", "ise", "ing", "ers", "er", "or",
                  "al", "ic", "ly", "ed", "es", "s")


def roots_of(word: str) -> list[str]:
    """拆出可能的构词根：unconfirmed → confirm，negotiator → negotiate，censorship → censor。"""
    out = []
    for p in DERIV_PREFIXES:
        if word.startswith(p) and len(word) - len(p) >= 3:
            out.append(word[len(p):])
    for s in DERIV_SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 3:
            stem = word[:-len(s)]
            out.append(stem)
            out.append(stem + "e")   # negotiat → negotiate
            out.append(stem + "y")   # privat → privacy
            if stem.endswith("i"):
                out.append(stem[:-1] + "y")  # happi → happy
    return [w for w in dict.fromkeys(out) if w and w != word]


def derived_from_known(word: str, bases: dict[str, dict]) -> bool:
    """判断是不是“本来认识的词的简单派生”（最多拆两层）。"""
    for r in roots_of(word):
        if is_common(bases.get(r)):
            return True
        for r2 in roots_of(r):
            if is_common(bases.get(r2)):
                return True
    return False


# ---------- 熟词生义 ----------
# 词频表只能筛“简不简单”，筛不出“新闻里它换了意思”。
# ECDICT 自带的领域标注不可靠（idea 都被标成 [医]“观念”），靠它自动判断会灌进噪声，
# 所以这一层用一张人工维护的新闻义词表：命中就出卡、并在卡片上标“新闻义”。
# 运行时纯查表，零 token；新词直接往 data/news_senses.json 里加即可。

NEWS_SENSE_FILE = os.path.join("data", "news_senses.json")


def load_news_senses() -> dict:
    for p in (NEWS_SENSE_FILE, os.path.join(os.path.dirname(__file__), "..", "data", "news_senses.json")):
        try:
            with open(os.path.normpath(p), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            continue
    return {}


def raw_sentence(word: str, sents: list[str], variants: list[str] | None = None) -> str:
    """跟 context_for 同样的匹配规则，但返回未加工的句子原文（供语义判断用）。"""
    alts = {word}
    for v in variants or []:
        if v and len(v) >= 3:
            alts.add(v)
    exact = re.compile(r"\b(?:" + "|".join(re.escape(a) for a in sorted(alts, key=len, reverse=True))
                       + r")[a-z]{0,3}\b", re.I)
    stem = word[:max(6, len(word) // 2)]
    loose = re.compile(r"\b" + re.escape(stem) + r"[a-z]{0,8}\b", re.I)
    for pat in (exact, loose):
        for s in sents:
            if pat.search(s):
                return s
    return ""


# ---------- 联网补全（免费公开词典，无需密钥，不产生模型 token） ----------

def load_cache() -> dict:
    if os.path.exists(ENRICH_CACHE):
        try:
            with open(ENRICH_CACHE, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}
    return {}


def save_cache(cache: dict) -> None:
    try:
        os.makedirs(os.path.dirname(ENRICH_CACHE) or ".", exist_ok=True)
        with open(ENRICH_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=0)
    except OSError:
        pass


def fetch_enrich(word: str, timeout: int = 8) -> dict:
    """取英文释义、例句、词性、发音音频地址；失败返回空 dict。"""
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + urllib.parse.quote(word)
    req = urllib.request.Request(url, headers={"User-Agent": "kikinews-vocab/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return {}
    if not isinstance(data, list) or not data:
        return {}
    first = data[0]
    out = {}
    if first.get("phonetic"):
        out["phonetic"] = first["phonetic"].strip()
    for ph in first.get("phonetics") or []:
        if ph.get("audio"):
            out["audio"] = ph["audio"]
        if ph.get("text") and "phonetic" not in out:
            out["phonetic"] = ph["text"].strip()
    meanings = first.get("meanings") or []
    for m in meanings:
        pos = (m.get("partOfSpeech") or "").strip()
        for d in m.get("definitions") or []:
            if d.get("definition"):
                out.setdefault("en", d["definition"].strip())
                out.setdefault("pos", pos)
            if d.get("example") and "example" not in out:
                out["example"] = d["example"].strip()
        if out.get("en"):
            break
    return out


def enrich_words(words: list[str], use_net: bool) -> dict:
    cache = load_cache()
    todo = [w for w in words if w not in cache]
    if use_net:
        for w in todo:
            cache[w] = fetch_enrich(w)
        if todo:
            save_cache(cache)
    return {w: cache.get(w) or {} for w in words}


# ---------- 语境句 ----------

def sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text)
    out = []
    for s in SENT_SPLIT.split(flat):
        s = s.strip()
        # 正文里的小标题（「Impact」「Prerequisite Context」）不是句子，去掉
        s = re.sub(r"^[「『\"']?[^」』\"']{0,30}[」』\"']\s*", "", s) if re.match(r"^[「『]", s) else s
        s = s.strip()
        if len(s) < 25:
            continue
        # 标题行常带评分/标签残留，不适合当语境句
        if "⭐" in s or re.search(r"\b\d+\.\d/10\b", s):
            continue
        out.append(s)
    return out


def tts_url(word: str) -> str:
    """有道的公开发音接口（https，直接返回 mp3，无需密钥），比 WebView 自带 TTS 可靠。"""
    return "https://dict.youdao.com/dictvoice?audio=" + urllib.parse.quote(word) + "&amp;type=2"


def context_for(word: str, sents: list[str], variants: list[str] | None = None) -> str:
    """从原文里摘出该词所在的句子并高亮。

    词表里给的是**原形**，原文里往往是变形（retaliation / retaliations / underpinned），
    所以把词库里该词族的变形一起纳入匹配；实在找不到再退一步用词干前缀匹配，
    避免出现“有卡片却没语境”或缺高亮的情况。
    """
    alts = {word}
    for v in variants or []:
        if v and len(v) >= 3:
            alts.add(v)
    exact = re.compile(r"\b(?:" + "|".join(re.escape(a) for a in sorted(alts, key=len, reverse=True))
                       + r")[a-z]{0,3}\b", re.I)
    stem = word[:max(6, len(word) // 2)]
    loose = re.compile(r"\b" + re.escape(stem) + r"[a-z]{0,8}\b", re.I)
    for pat in (exact, loose):
        for s in sents:
            m = pat.search(s)
            if not m:
                continue
            # 以命中词为中心裁剪，保证高亮的那一段不会被截断吃掉
            start = max(0, m.start() - 110)
            end = min(len(s), start + 300)
            if end - start < 300:
                start = max(0, end - 300)
            piece = ("…" if start else "") + s[start:end] + ("…" if end < len(s) else "")
            # 先转义（词是纯 ASCII，转义不会改动字母），再在转义结果上标红
            piece = html.escape(html.unescape(piece), quote=False)
            piece = pat.sub(lambda mm: "<b>" + mm.group(0) + "</b>", piece, count=1)
            return piece
    return ""


# ---------- 渲染 ----------

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<title>{title}</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>
:root{{
  --bg:#0e1320;--card:#171d2c;--fg:#e8ecf6;--muted:#8b93a7;--line:#2a3245;
  --accent:#4ea1ff;--chip:#232c3f;--shadow:0 10px 30px rgba(0,0,0,.35);
}}
*{{box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
body{{margin:0;background:var(--bg);color:var(--fg);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:16px;line-height:1.6;overflow-x:hidden}}
.wrap{{max-width:720px;margin:0 auto;padding:0 16px 60px}}
.bar{{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:10px;
  padding:12px 0;background:linear-gradient(180deg,var(--bg) 78%,transparent)}}
.back{{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:999px;
  background:var(--card);border:1px solid var(--line);color:var(--fg);text-decoration:none;font-size:14px}}
.count{{color:var(--muted);font-size:12.5px}}
.card{{position:relative;background:var(--card);border:1px solid var(--line);border-radius:16px;
  padding:13px 16px 14px;box-shadow:var(--shadow);margin:0 0 10px;overflow:hidden}}
.card::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--accent);opacity:.55}}
.hdr{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.w{{font-size:19px;font-weight:700;letter-spacing:.2px}}
.ph{{color:var(--muted);font-size:13px;font-weight:400}}
.meta{{display:flex;align-items:center;gap:8px;margin-top:3px;flex-wrap:wrap}}
.pos{{font-size:11.5px;color:var(--fg);background:var(--chip);border-radius:6px;padding:2px 7px}}
.stars{{font-size:11.5px;color:#ffc861;letter-spacing:1px}}
.say{{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;
  border-radius:999px;border:1px solid var(--line);background:var(--chip);color:var(--fg);
  font-size:14px;cursor:pointer;padding:0}}
.say:active{{transform:scale(.94)}}
.say.on{{border-color:var(--accent);color:var(--accent)}}
.t{{margin-top:7px;font-size:14.5px;color:#cfd6e6;white-space:pre-wrap}}
.en{{margin-top:5px;font-size:13.5px;color:#a9b4cc;font-style:italic}}
.ex{{margin-top:4px;font-size:13px;color:var(--muted)}}
.sense{{margin-top:7px;padding:7px 10px;border-radius:8px;background:rgba(255,200,97,.09);
  border:1px solid rgba(255,200,97,.25);font-size:13.5px;color:#ffd68a}}
.sense .lb{{color:#c9a45f;font-size:11px;margin-right:6px;letter-spacing:.4px}}
.ctx{{margin-top:9px;padding:9px 11px;border-left:2px solid #3b4a6b;background:rgba(78,161,255,.07);
  border-radius:0 10px 10px 0;font-size:13.5px;color:#c3cddf}}
.ctx b{{color:#7fb8ff;font-weight:700}}
.ctx .lb{{display:block;font-size:11px;color:var(--muted);margin-bottom:3px;letter-spacing:.4px}}
.intro{{color:var(--muted);font-size:12.5px;margin:6px 0 14px}}
footer{{margin-top:26px;text-align:center;color:var(--muted);font-size:12px;line-height:1.9}}
</style>
<div class="wrap">
  <div class="bar">
    <a class="back" href="latest.html">‹ 返回今日速递</a>
    <span class="count">{count} 个词 · {day}</span>
  </div>
  <div class="intro">今日超纲词汇（已排除四六级等低于 C1 的高频词）。</div>
  {cards}
  <footer>KIKI · 难点词汇 · 释义取自开源词库 ECDICT 与公开词典接口</footer>
</div>
<script>
(function(){{
  var doc = document;
  function tts(word){{
    try {{
      if (!window.speechSynthesis) return;
      var u = new SpeechSynthesisUtterance(word);
      u.lang = 'en-US'; u.rate = 0.92;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
    }} catch (e) {{}}
  }}
  function speak(word, src){{
    if (!src) {{ tts(word); return; }}
    try {{
      var a = new Audio(src);
      a.onerror = function(){{ tts(word); }};
      var p = a.play();
      if (p && p.catch) {{ p.catch(function(){{ tts(word); }}); }}
    }} catch (e) {{ tts(word); }}
  }}
  doc.addEventListener('click', function(ev){{
    var btn = ev.target.closest ? ev.target.closest('.say') : null;
    if (!btn) return;
    var self = this;
    btn.classList.add('on');
    setTimeout(function(){{ btn.classList.remove('on'); }}, 600);
    speak(btn.getAttribute('data-w'), btn.getAttribute('data-a'));
  }}, false);
}})();
</script>
</html>
"""

CARD = """<div class="card">
    <div class="hdr"><span class="w">{word}</span><button class="say" data-w="{word}" data-a="{audio}">🔊</button>{ph}</div>
    <div class="meta">{pos}{stars}</div>
    <div class="t">{trans}</div>{sense}{en}{ex}{ctx}
  </div>"""

POS_MAP = [
    ("n.", "n."), ("vt.", "v."), ("vi.", "v."), ("v.", "v."),
    ("a.", "adj."), ("adj.", "adj."), ("ad.", "adv."), ("adv.", "adv."),
    ("prep.", "prep."), ("conj.", "conj."), ("pron.", "pron."),
]


def stars_for(frq: int) -> str:
    if frq == 0:
        return "★★★★★"
    if frq >= 16000:
        return "★★★★"
    if frq >= 12000:
        return "★★★"
    return "★★"


def short(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + "…"


def pos_of(entry: dict, enrich: dict) -> str:
    raw = (enrich.get("pos") or "").strip()
    if raw:
        short = {"noun": "n.", "verb": "v.", "adjective": "adj.", "adverb": "adv.",
                 "preposition": "prep.", "conjunction": "conj.", "pronoun": "pron."}.get(raw, raw)
        return f'<span class="pos">{html.escape(short)}</span>'
    first = entry["translation"].strip().split()[0] if entry["translation"].strip() else ""
    for src, short in POS_MAP:
        if first == src:
            return f'<span class="pos">{short}</span>'
    return ""


def main() -> None:
    dict_path = os.environ.get("ECDICT_PATH") or os.path.join("data", "ecdict.csv")
    post = newest_post("en")
    if not post:
        print("[skip] no english post found")
        return
    day = os.path.basename(post).split("-summary")[0]
    # 与日报页完全一致：按这次抓取的 UTC 时间换算北京时间，重建不会改日期
    display_day, _ = digest_display(DOCS)
    text = read_prose(post)
    wanted = candidates_from(text)
    # 把可能的构词根也一起查进来，才能判断 unconfirmed 是不是由认识的 confirm 派生而来
    wanted |= {r for t in list(wanted) for r in roots_of(t)}
    bases, rev_multi, forms_of = scan_dict(dict_path, wanted)
    if not bases:
        print(f"[skip] dictionary not found or nothing matched: {dict_path}")
        return

    def resolve(token: str) -> str:
        """变形 → 最可能的原形：取词频最靠前（最常用）的那个原形。"""
        cands = rev_multi.get(token)
        if not cands:
            return token

        def score(b: str):
            e = bases.get(b)
            if not e:
                return (10**9, 10**9, len(b))
            return (e["frq"] or 10**9, e["bnc"] or 10**9, len(b))

        return min(cands, key=score)

    freq = Counter()
    lower_forms = Counter()
    for m in TOKEN.finditer(text):
        raw = m.group(0).strip("'-")
        freq[raw.lower()] += 1
        if raw[:1].islower():
            lower_forms[raw.lower()] += 1

    # 先归到原形再判断：countries 计入 country、held 计入 hold，
    # 频率和难度都按原形算，避免把极常见的词收进来，也避免拿没有音标的变形行出词。
    sents = sentences(text)
    news_senses = load_news_senses()
    picked = []
    seen_words = set()
    common_sense = []      # 熟词生义候选，单独排序、单独限额
    for token in sorted(lower_forms):
        base = resolve(token)
        e = bases.get(base)
        if not e or e["word"] in seen_words:
            continue
        # 简单派生词不收：unconfirmed / negotiator / redesign 这类，
        # 只要去掉前后缀后能落到一个“本来就会”的词，就不算生词。
        if derived_from_known(e["word"], bases):
            continue
        count = sum(c for f, c in lower_forms.items() if resolve(f) == base)
        if is_hard(e):
            seen_words.add(e["word"])
            picked.append((e["frq"], -count, e, None))
            continue
        # 第二层：熟词生义。词本身不算生僻，但在这条新闻里是另一个意思——
        # 这正是“看得懂每个词、却读不懂这句话”的来源，值得单独列出。
        note = news_senses.get(e["word"])
        if note:
            seen_words.add(e["word"])
            common_sense.append((e["frq"], -count, e, (e["word"], note)))

    picked.sort(key=lambda x: (x[0] if x[0] > 0 else 10**9, x[1]))
    picked = picked[:MAX_WORDS]
    common_sense.sort(key=lambda x: (x[0] if x[0] > 0 else 10**9, x[1]))
    sense_picked = common_sense[:MAX_SENSE_WORDS]

    # 音标兜底：变形词（millions / canceling / prototyping）本行往往没音标，
    # 回到原形词条去取，取到就补上。
    all_picked = picked + sense_picked
    need_ph = {e["word"] for _, _, e, _ in all_picked if not e["phonetic"]}
    if need_ph:
        guesses = {w: phonetic_guesses(w) for w in need_ph}
        extra = scan_dict(dict_path, {g for gs in guesses.values() for g in gs})[0]
        for _, _, e, _ in all_picked:
            if e["phonetic"]:
                continue
            for g in guesses.get(e["word"], []):
                cand = extra.get(g)
                if cand and cand["phonetic"]:
                    e["phonetic"] = cand["phonetic"]
                    break

    words = [e["word"] for _, _, e, _ in all_picked]
    use_net = os.environ.get("VOCAB_NO_NET") != "1"
    enriched = enrich_words(words, use_net) if words else {}

    cards = []
    dropped = []
    for _, _, e, sense in all_picked:
        w = e["word"]
        en = enriched.get(w) or {}
        audio = tts_url(w)
        # 词库里部分词条（尤其是派生词、专业词）没有音标，用公开词典接口的音标补上
        ph_text = e["phonetic"] or (en.get("phonetic") or "")
        if not ph_text:
            # 连音标都查不到的词不出卡：列出来却不会读，对读者没意义
            dropped.append(w)
            continue
        ph = f'<span class="ph">/{html.escape(ph_text, quote=False)}/</span>'
        # 词库释义用字面量 "\n" 分行，且常带 [网络]/[计] 之类的专业标记
        raw_lines = e["translation"].replace("\\n", "\n").split("\n")
        lines = [ln.strip() for ln in raw_lines if ln.strip()]
        keep = [ln for ln in lines if not ln.startswith("[网络]")][:3] or lines[:3]
        trans = html.escape("\n".join(keep), quote=False)
        sense_bit = (f'<div class="sense"><span class="lb">新闻义</span>'
                     f'{html.escape(sense[1], quote=False)}</div>' if sense else "")
        en_bit = (f'<div class="en">{html.escape(short(en["en"], 150), quote=False)}</div>'
                  if en.get("en") else "")
        ex_bit = (f'<div class="ex">e.g. {html.escape(short(en["example"], 150), quote=False)}</div>'
                  if en.get("example") else "")
        ctx = context_for(w, sents, forms_of.get(w))
        ctx_bit = f'<div class="ctx"><span class="lb">原文语境</span>{ctx}</div>' if ctx else ""
        cards.append(CARD.format(
            word=html.escape(w, quote=False), audio=audio, ph=ph,
            pos=pos_of(e, en), stars=f'<span class="stars">{stars_for(e["frq"])}</span>',
            trans=trans, sense=sense_bit, en=en_bit, ex=ex_bit, ctx=ctx_bit,
        ))

    page = PAGE.format(
        title=f"难点词汇 {display_day}",
        day=display_day,
        count=len(cards),
        cards="\n  ".join(cards) or '<div class="card">这一期没有挑出超纲词。</div>',
    )
    out = os.path.join(DOCS, "vocab.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[ok] vocab.html: {len(cards)} words from {os.path.basename(post)} "
          f"(enrich: {sum(1 for w in words if enriched.get(w))})")
    if dropped:
        print(f"[info] 无音标已跳过: {', '.join(dropped)}")


if __name__ == "__main__":
    main()
