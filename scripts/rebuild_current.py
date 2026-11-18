"""以「线上最新一期」为准重建两页，避免用本地过期正文覆盖线上。

背景：本地 docs/_posts 常常比线上落后若干天（流水线只在 Actions 里跑）。
手工重建前如果不先从 gh-pages 拉最新正文，就会把旧一期发布上线——2026-11-18 已经出过一次。

用法（在仓库根目录执行）：
    $env:KIKI_PAT='<GitHub 令牌>'
    python scripts\\rebuild_current.py            # 只重建，不推送
    python scripts\\rebuild_current.py --push     # 重建 + 推到 gh-pages 根与 main/docs

令牌只从环境变量读，不写进本文件（仓库是公开的）。
"""
import base64
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

OWNER, NAME = "dearwood777", "KIKINEWS"
GH_PAGES = "gh-pages"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
API = f"https://api.github.com/repos/{OWNER}/{NAME}"


def headers():
    token = os.environ.get("KIKI_PAT", "").strip()
    if not token:
        sys.exit("缺少环境变量 KIKI_PAT（GitHub 令牌），已中止，不会动任何文件。")
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
            "User-Agent": "kiki-rebuild"}


def api_get(path, hdrs, ref=GH_PAGES):
    url = f"{API}/contents/{urllib.parse.quote(path)}?ref={ref}"
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def api_blob(path, hdrs, ref=GH_PAGES):
    meta = api_get(path, hdrs, ref)
    req = urllib.request.Request(meta["url"], headers=hdrs)
    with urllib.request.urlopen(req, timeout=90) as r:
        return base64.b64decode(json.load(r)["content"])


def digest_commit(hdrs, day):
    """找到把这一期正文提交到 gh-pages 的那次 digest 提交，用它取当期的其他文件。

    gh-pages 根目录的 candidates.json 可能被后续手工推送覆盖成旧一期的版本，
    只有那次提交里的才是这一期真正对应的数据。
    """
    path = urllib.parse.quote(f"_posts/{day}-summary-en.md")
    url = f"{API}/commits?path={path}&sha={GH_PAGES}&per_page=1"
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=45) as r:
        commits = json.load(r)
    return commits[0]["sha"] if commits else GH_PAGES


def newest_post(hdrs):
    posts = api_get("_posts", hdrs)
    dates = sorted({p["name"][:10] for p in posts if p["name"].endswith("-summary-en.md")})
    if not dates:
        sys.exit("线上 _posts 里没有找到任何一期正文，已中止。")
    return dates[-1]


def main():
    hdrs = headers()
    day = newest_post(hdrs)
    ref = digest_commit(hdrs, day)
    print(f"[info] 线上最新一期：{day}（digest 提交 {ref[:7]}）")

    for name in (f"{day}-summary-en.md", f"{day}-summary-zh.md"):
        dst = os.path.join(DOCS, "_posts", name)
        with open(dst, "wb") as f:
            f.write(api_blob(f"_posts/{name}", hdrs))
        print(f"[get] {name}")

    with open(os.path.join(DOCS, "candidates.json"), "wb") as f:
        f.write(api_blob("candidates.json", hdrs, ref))
    print("[get] candidates.json（取自本期 digest 提交）")

    # latest.json 里是 guard 判断“该不该出下一期”的生成时间，重建会把它改成当前时间，
    # 从而把下一次出刊推迟 12 小时，所以先留底、构建后还原。
    live_latest = api_blob("latest.json", hdrs, ref)
    expect_date = json.loads(live_latest.decode("utf-8")).get("date", "")
    keep = os.path.join(DOCS, "latest.json.from_live")
    with open(keep, "wb") as f:
        f.write(live_latest)

    env = dict(os.environ, VOCAB_NO_NET="1", VOCAB_AI=os.environ.get("VOCAB_AI", "0"))
    if not env.get("ECDICT_PATH"):
        env["ECDICT_PATH"] = os.path.join(ROOT, "data", "ecdict.csv")
    for script in ("build_vocab.py", "build_latest.py"):   # 顺序不能反，否则主页入口会丢
        print(f"[run] {script}")
        subprocess.run([sys.executable, os.path.join("scripts", script)], cwd=ROOT,
                       env=env, check=True, encoding="utf-8")

    with open(os.path.join(DOCS, "latest.json"), "wb") as f:
        f.write(live_latest)
    os.remove(keep)
    print("[ok] latest.json 已还原为线上那一期的生成时间")

    page = open(os.path.join(DOCS, "latest.html"), encoding="utf-8").read()
    cards = page.count('class="card"')
    if expect_date:
        assert f'<div class="day">{expect_date}' in page, \
            f"页面日期与本期 latest.json 的 date（{expect_date}）不一致，构建异常"
        print(f"[check] 页面日期 = {expect_date}，与本期 latest.json 一致")
    assert cards >= 10, f"卡片数异常（{cards}），可能读错了正文"
    print(f"[check] 卡片 {cards} 条，正文用的是 {day} 这一期")


    if "--push" in sys.argv:
        msg = f"pages: rebuild from remote posts ({day})"
        for name in ("latest.html", "latest-en.html", "vocab.html", "widget.json", "latest.json"):
            content = base64.b64encode(open(os.path.join(DOCS, name), "rb").read()).decode()
            for branch, dst in ((GH_PAGES, name), ("main", f"docs/{name}")):
                url = f"{API}/contents/{urllib.parse.quote(dst)}"
                try:
                    sha = json.load(urllib.request.urlopen(
                        urllib.request.Request(f"{url}?ref={branch}", headers=hdrs), timeout=30))["sha"]
                except Exception:
                    sha = None
                payload = {"message": msg, "content": content, "branch": branch}
                if sha:
                    payload["sha"] = sha
                req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=dict(
                    hdrs, **{"Content-Type": "application/json"}), method="PUT")
                try:
                    with urllib.request.urlopen(req, timeout=150) as r:
                        print(f"[push] {branch}:{dst} -> {json.load(r)['commit']['sha'][:7]}")
                except Exception as exc:
                    print(f"[push-fail] {branch}:{dst} {exc}")
    else:
        print("[done] 未推送。确认页面无误后加 --push 再跑一次。")


if __name__ == "__main__":
    main()
