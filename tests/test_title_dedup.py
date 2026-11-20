"""Tests for the deterministic title deduplication layer."""

import asyncio
import json
from datetime import datetime, timezone
from types import SimpleNamespace

from rich.console import Console
import pytest

import src.orchestrator as orchestrator_module
from src.models import (
    ClassificationResult,
    ContentAnalysis,
    ContentItem,
    ProcessingResult,
    SourceType,
)
from src.orchestrator import HorizonOrchestrator
from src.processing.title_dedup import (
    cluster_duplicate_titles,
    normalize_title,
    title_tokens,
)


def make_item(item_id, score, title, *, content=None, source_type=SourceType.RSS):
    return ContentItem(
        id=item_id,
        source_type=source_type,
        title=title,
        url=f"https://example.com/{item_id}",
        content=content,
        published_at=datetime.now(timezone.utc),
        profile="world-news",
        processing=ProcessingResult(
            classification=ClassificationResult(profile="world-news", method="source_override"),
            analysis=ContentAnalysis(score=score, reason="test", summary=item_id),
        ),
    )


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def complete(self, **kwargs):
        self.calls.append(kwargs)
        return json.dumps(self.response)


def build_orchestrator(monkeypatch, client):
    monkeypatch.setattr(orchestrator_module, "create_ai_client", lambda config: client)
    orchestrator = HorizonOrchestrator.__new__(HorizonOrchestrator)
    orchestrator.config = SimpleNamespace(ai=None)
    orchestrator.console = Console(record=True)
    return orchestrator


def run_topic_dedup(monkeypatch, client, items):
    orchestrator = build_orchestrator(monkeypatch, client)
    return asyncio.run(orchestrator.merge_topic_duplicates(items, log=False))


ROHINGYA = [
    "Myanmar committed genocide against Rohingya minority, world's top court rules",
    "Myanmar committed genocide against Rohingya minority, top UN court rules",
    "Top UN court finds Myanmar committed genocide against Muslim Rohingya - Reuters",
    "World court finds Myanmar committed genocide against the Rohingya - Courthouse News",
]


def test_normalize_title_strips_outlet_suffix_and_punctuation():
    assert normalize_title("Top UN court finds Myanmar guilty - Reuters") == (
        "top un court finds myanmar guilty"
    )
    assert normalize_title("最高法院裁定缅甸实施种族灭绝 · BBC") == "最高法院裁定缅甸实施种族灭绝 bbc"


def test_title_tokens_keeps_rare_words_and_drops_stopwords():
    tokens = title_tokens("Myanmar committed genocide against the Rohingya - Reuters")

    assert {"myanmar", "committed", "genocide", "rohingya"} <= tokens
    assert "against" not in tokens and "the" not in tokens


def test_cluster_duplicate_titles_collapses_one_event_four_wordings():
    groups = cluster_duplicate_titles(ROHINGYA)

    assert groups == [[0, 1, 2, 3]]


def test_cluster_duplicate_titles_keeps_distinct_stories_separate():
    titles = [
        "Anthropic hits $2T in Nasdaq debut",
        "Fiona the hippo dies after swallowing a hat at Cincinnati Zoo",
        "UK government forced to admit it issued Apple a secret encryption order",
    ]

    assert cluster_duplicate_titles(titles) == []


def test_short_generic_titles_are_not_merged_by_guard():
    # Both reduce to a single token ("title"), below the MIN_TOKENS guard.
    assert cluster_duplicate_titles(["title 0", "title 1"]) == []


def test_merges_literal_duplicates_even_when_ai_reports_nothing(monkeypatch):
    items = [
        make_item("a", 9.0, ROHINGYA[0], content="body a"),
        make_item("b", 8.0, ROHINGYA[2], content="body b"),
    ]
    result = run_topic_dedup(monkeypatch, FakeClient({"duplicates": []}), items)

    assert [item.id for item in result] == ["a"]
    assert "body b" in result[0].content


def test_title_merge_survives_a_generic_ai_failure(monkeypatch):
    class BrokenClient:
        async def complete(self, **kwargs):
            raise RuntimeError("model overloaded")

    items = [
        make_item("a", 9.0, ROHINGYA[0]),
        make_item("b", 8.0, ROHINGYA[1]),
        make_item("c", 7.0, "Fiona the hippo dies after swallowing a hat at Cincinnati Zoo"),
    ]
    result = run_topic_dedup(monkeypatch, BrokenClient(), items)

    assert [item.id for item in result] == ["a", "c"]


def test_ai_dedup_runs_on_the_surviving_items_with_its_own_budget(monkeypatch):
    client = FakeClient({"duplicates": []})
    items = [
        make_item("a", 9.0, ROHINGYA[0]),
        make_item("b", 8.0, ROHINGYA[1]),
        make_item("c", 7.5, "Fiona the hippo dies after swallowing a hat at Cincinnati Zoo"),
    ]
    run_topic_dedup(monkeypatch, client, items)

    call = client.calls[0]
    assert call["max_tokens"] >= 1024
    # Two survivors only: the AI never sees the row that was already merged away.
    assert "[2]" not in call["user"]


def test_chinese_titles_of_the_same_event_are_merged(monkeypatch):
    items = [
        make_item("a", 9.0, "最高法院裁定缅甸对罗兴亚族实施种族灭绝"),
        make_item("b", 8.0, "最高法院认定缅甸对罗兴亚族实施种族灭绝"),
        make_item("c", 7.0, "黄仁勋表示愿回任 Nvidia CEO"),
    ]
    result = run_topic_dedup(monkeypatch, FakeClient({"duplicates": []}), items)

    assert [item.id for item in result] == ["a", "c"]
