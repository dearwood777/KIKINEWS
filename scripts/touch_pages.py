# -*- coding: utf-8 -*-
"""Pages 构建兜底：往 gh-pages 的 _config.yml 追加一行注释，触发一次重建。

GitHub Pages 的 legacy Jekyll 构建偶尔会 errored（内容本身没问题），而
github.token 没有 Pages 构建权限（POST /pages/builds 返回 403），改一个
受版本控制的文件是唯一能稳触发重建的办法。
用法：GH_TOKEN=... python scripts/touch_pages.py
"""
from __future__ import annotations

import base64
import datetime
import json
import os
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY") or "dearwood777/KIKINEWS"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
PATH = "_config.yml"


def api(method: str, path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/{path}",
        data=json.dumps(body).encode() if body else None,
        method=method,
    )
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    if body:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read())


def main() -> None:
    if not TOKEN:
        print("[skip] 没有 token，无法触发 Pages 重建")
        return
    info = api("GET", f"contents/{PATH}?ref=gh-pages")
    raw = base64.b64decode(info["content"]).decode("utf-8")
    stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    text = raw.rstrip("\n") + f"\n# rebuild-trigger {stamp}\n"
    api("PUT", f"contents/{PATH}", {
        "message": "chore(pages): re-trigger build after errored run",
        "content": base64.b64encode(text.encode()).decode(),
        "branch": "gh-pages",
        "sha": info["sha"],
    })
    print("[ok] 已在 gh-pages/_config.yml 追加触发注释")


if __name__ == "__main__":
    main()
