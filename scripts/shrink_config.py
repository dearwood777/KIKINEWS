#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""备用 provider 重跑前把 data/config.json 的量压到最小，避免打爆小额度。

Gemini 免费层只有 20 次请求/天，所以这里只留：HackerNews 少量高分条目 + 一个 RSS 源。
"""
import json
import os

PATH = os.path.join("data", "config.json")


def main() -> None:
    with open(PATH, encoding="utf-8") as f:
        cfg = json.load(f)

    cfg.setdefault("digest", {})["max_items"] = 5

    src = cfg.get("sources", {})

    hn = src.get("hackernews", {})
    if hn:
        hn["enabled"] = True
        hn["fetch_top_stories"] = 12
        hn["min_score"] = 250

    rd = src.get("reddit", {})
    if rd:
        rd["enabled"] = False

    gh = src.get("github", [])
    if isinstance(gh, list):
        for g in gh:
            g["enabled"] = False

    rss = src.get("rss", [])
    if isinstance(rss, list):
        keep = {"CNBC Finance", "TechCrunch"}
        for r in rss:
            r["enabled"] = r.get("name") in keep

    ai = cfg.get("ai", {})
    ai["analysis_concurrency"] = 2
    ai["enrichment_concurrency"] = 1

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    print("shrunk config: max_items=5, hn=12/250, rss=", [r["name"] for r in rss if r.get("enabled")])
    print("provider:", ai.get("provider"), "model:", ai.get("model"))


if __name__ == "__main__":
    main()
