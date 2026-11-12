"""只采集、不调用任何 AI：把当次抓到的候选标题和原文链接写进 docs/candidates.json。

页面上「展开全部候选」按钮读的就是这个文件，所以这条流程零 token 消耗。
用法：
    python scripts/collect_candidates_only.py [配置文件]
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models import Config  # noqa: E402
from src.scrapers.gdelt import GDELTScraper  # noqa: E402
from src.scrapers.github import GitHubScraper  # noqa: E402
from src.scrapers.google_news import GoogleNewsScraper  # noqa: E402
from src.scrapers.hackernews import HackerNewsScraper  # noqa: E402
from src.scrapers.rss import RSSScraper  # noqa: E402
from src.scrapers.telegram import TelegramScraper  # noqa: E402
from src.extractors import ExtractorRegistry  # noqa: E402


async def main() -> None:
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "configs/config.actions.groq.json"
    config = Config.model_validate(json.loads(Path(cfg_path).read_text(encoding="utf-8")))
    since = datetime.now(timezone.utc) - timedelta(hours=config.collection.time_window_hours)

    items = []
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        jobs = []
        if config.sources.hackernews and config.sources.hackernews.enabled:
            jobs.append(HackerNewsScraper(config.sources.hackernews, client).fetch(since))
        if config.sources.rss:
            jobs.append(
                RSSScraper(config.sources.rss, client, ExtractorRegistry(config.extractors)).fetch(since)
            )
        if getattr(config.sources, "google_news", None):
            jobs.append(GoogleNewsScraper(config.sources.google_news, client).fetch(since))
        if getattr(config.sources, "gdelt", None):
            jobs.append(GDELTScraper(config.sources.gdelt, client).fetch(since))
        if getattr(config.sources, "telegram", None):
            jobs.append(TelegramScraper(config.sources.telegram, client).fetch(since))
        if getattr(config.sources, "github", None):
            jobs.append(GitHubScraper(config.sources.github, client).fetch(since))

        results = await asyncio.gather(*jobs, return_exceptions=True)

    for res in results:
        if isinstance(res, Exception):
            print(f"[warn] source failed: {type(res).__name__}: {res}")
            continue
        items.extend(res.items)
        if res.failures:
            print(f"[warn] partial: {list(res.failures)[:2]}")

    seen_urls: set[str] = set()
    rows = []
    for item in items:
        url = str(getattr(item, "url", "") or "")
        title = (getattr(item, "title", "") or "").strip()
        if not title or url in seen_urls:
            continue
        seen_urls.add(url)
        rows.append(
            {
                "title": title,
                "url": url,
                "score": None,
                "profile": getattr(item.source_type, "value", ""),
            }
        )

    docs = Path("docs")
    docs.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(rows),
        "items": rows,
    }
    (docs / "candidates.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"[ok] {len(rows)} candidates -> docs/candidates.json")


if __name__ == "__main__":
    asyncio.run(main())
