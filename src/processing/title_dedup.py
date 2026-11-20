"""Deterministic near-duplicate detection for news titles.

Why this exists: the AI topic-dedup stage is a single LLM call whose JSON can be
truncated (the Groq/Gemini configs cap ``max_tokens`` well below what a full
duplicate list needs). When that happens the stage silently returns every item
unchanged, and the digest ships several wordings of one story. This module is a
token-free safety net: it merges titles that are clearly the same story after
normalisation, so an AI failure can no longer produce visible duplicates.

Matching rules:
- Titles are normalised first: NFKC, HTML stripped, outlet suffix ("- Reuters",
  "| BBC News") removed, lower-cased, quotes unified, punctuation collapsed,
  possessive "'s" dropped.
- The token set mixes latin word tokens (len >= 3, stop words dropped) and CJK
  character bigrams, so Chinese titles are comparable without a segmenter.
- Two plain (non-IDF) metrics are combined, both stable regardless of batch size:
  * overlap coefficient = |A and B| / min(|A|, |B|), threshold 0.72 — catches a
    re-worded headline that reuses most of the shorter title's content;
  * Jaccard = |A and B| / |A or B|, threshold 0.20 — rejects pairs that only
    share a couple of words while each title carries a lot of other material.
- Two guards keep it conservative: both titles need >= 3 tokens, and they must
  share >= 2 tokens. Short generic titles never collapse into each other.

Known limit: two titles that differ only in one product/version token (e.g.
"iOS 27 beta" vs "macOS 27 beta") still look like one story here. That check
belongs to the semantic AI stage, which runs after this pass on the survivors.
"""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from typing import Iterable, List, Sequence, Set

# Weighted down because every news title uses them.
_EN_STOPWORDS = {
    "a", "an", "the", "of", "to", "in", "on", "at", "for", "from", "with", "by",
    "as", "is", "are", "was", "were", "be", "been", "being", "and", "or", "not",
    "but", "if", "then", "than", "that", "this", "these", "those", "it", "its",
    "their", "his", "her", "they", "them", "we", "you", "your", "our",
    "new", "says", "say", "said", "after", "before", "over", "under", "into",
    "out", "up", "down", "about", "more", "most", "less", "many", "much",
    "amid", "could", "would", "should", "will", "can", "may", "might",
    "has", "have", "had", "do", "does", "did", "who", "what", "when", "where",
    "why", "how", "top", "world", "court", "courts", "rule", "rules", "ruled",
    "ruling", "find", "finds", "found", "case", "cases", "news", "report",
    "reports", "today", "now", "first",
    "against", "among", "between", "during", "since", "until", "while", "via",
    "per", "plus", "across", "behind", "beyond", "within", "without", "despite",
    "toward", "towards", "upon", "off", "onto", "also", "just", "only", "very",
    "still", "again", "already", "around", "near", "back", "both",
}

_OUTLET_SUFFIX = re.compile(r"^(.*?)\s*[\-\u2013\u2014|]\s*([A-Za-z0-9 &.'\u2019\-]{2,30})$")
_LATIN_TOKEN = re.compile(r"[a-z0-9']+")
_CJK_RUN = re.compile(r"[\u4e00-\u9fff]+")
_TAG = re.compile(r"<[^>]+>")

OVERLAP_THRESHOLD = 0.72
JACCARD_THRESHOLD = 0.20
MIN_TOKENS = 3
MIN_SHARED_TOKENS = 2


def strip_outlet_suffix(title: str) -> str:
    """Drop a trailing "- Reuters" / "| BBC News" style outlet attribution."""
    text = title.strip()
    match = _OUTLET_SUFFIX.match(text)
    if not match:
        return text
    tail = match.group(2)
    # Only treat it as an outlet when it looks like one: a few ascii words,
    # no sentence punctuation, and not the whole title.
    if len(tail.split()) > 4 or re.search(r"[\u4e00-\u9fff，。！？]", tail):
        return text
    head = match.group(1).strip()
    return head or text


def normalize_title(title: str) -> str:
    """Normalise a title into a comparable, punctuation-free form."""
    text = unicodedata.normalize("NFKC", strip_outlet_suffix(title or ""))
    text = _TAG.sub("", text).lower()
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", "'").replace("\u201d", "'")
    text = re.sub(r"[^0-9a-z\u4e00-\u9fff']+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def title_tokens(title: str) -> Set[str]:
    """Return the similarity token set for one title."""
    normalized = normalize_title(title)
    tokens: Set[str] = set()
    for word in _LATIN_TOKEN.findall(normalized):
        word = word.strip("'")
        if word.endswith("'s"):
            word = word[:-2]
        if len(word) >= 3 and word not in _EN_STOPWORDS:
            tokens.add(word)
    for run in _CJK_RUN.findall(normalized.replace(" ", "")):
        if len(run) > 1:
            tokens.update(run[i : i + 2] for i in range(len(run) - 1))
    return tokens


def overlap_coefficient(left: Set[str], right: Set[str]) -> float:
    """|A and B| / min(|A|, |B|): how much of the shorter title is reused."""
    shared = left & right
    if not shared:
        return 0.0
    smaller = min(len(left), len(right))
    return len(shared) / smaller if smaller else 0.0


def jaccard_similarity(left: Set[str], right: Set[str]) -> float:
    """|A and B| / |A or B|."""
    shared = left & right
    if not shared:
        return 0.0
    return len(shared) / len(left | right)


def titles_are_duplicates(
    left: Set[str],
    right: Set[str],
    *,
    overlap_threshold: float = OVERLAP_THRESHOLD,
    jaccard_threshold: float = JACCARD_THRESHOLD,
) -> bool:
    """Whether two token sets describe the same story under the tuned rules."""
    if len(left) < MIN_TOKENS or len(right) < MIN_TOKENS:
        return False
    if len(left & right) < MIN_SHARED_TOKENS:
        return False
    return (
        overlap_coefficient(left, right) >= overlap_threshold
        and jaccard_similarity(left, right) >= jaccard_threshold
    )


def cluster_duplicate_titles(
    titles: Sequence[str],
    *,
    overlap_threshold: float = OVERLAP_THRESHOLD,
    jaccard_threshold: float = JACCARD_THRESHOLD,
) -> List[List[int]]:
    """Return index groups whose titles describe the same story.

    Groups are only returned when they hold 2+ titles. Ordering inside a group
    follows the input order so callers can pick a primary deterministically.
    """
    if len(titles) < 2:
        return []

    token_sets = [title_tokens(title) for title in titles]
    parent = list(range(len(titles)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for i in range(len(titles)):
        if len(token_sets[i]) < MIN_TOKENS:
            continue
        for j in range(i + 1, len(titles)):
            if titles_are_duplicates(
                token_sets[i],
                token_sets[j],
                overlap_threshold=overlap_threshold,
                jaccard_threshold=jaccard_threshold,
            ):
                parent[find(j)] = find(i)

    groups: dict[int, List[int]] = defaultdict(list)
    for index in range(len(titles)):
        groups[find(index)].append(index)
    return [members for members in groups.values() if len(members) > 1]


def duplicate_title_groups(items: Iterable[object], *, title_attr: str = "title") -> List[List[int]]:
    """Convenience wrapper that reads titles off objects."""
    return cluster_duplicate_titles([getattr(item, title_attr, "") or "" for item in items])
