# -*- coding: utf-8 -*-
"""发布 APK：把编译好的 release 包放到 docs/app/，并生成 version.json。

App 里的 UpdateChecker 只认这个清单：
    https://<owner>.github.io/KIKINEWS/app/version.json
字段：versionCode（比较用，必须单调递增）、versionName（展示用）、apk（下载地址）、
sha256（下载完整性校验）、notes（一两句更新说明）。

用法：python scripts/publish_apk.py [apk 路径] [--notes "说明"]
默认 apk 路径：android/app/build/outputs/apk/release/app-release.apk
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys

DOCS_APP = os.path.join("docs", "app")
GRADLE = os.path.join("android", "app", "build.gradle.kts")
DEFAULT_APK = os.path.join("android", "app", "build", "outputs", "apk", "release", "app-release.apk")
BASE_URL = "https://dearwood777.github.io/KIKINEWS/app/"


def read_version() -> tuple[int, str]:
    """从 build.gradle.kts 读出 versionCode（纯算术式）与 versionName。"""
    text = open(GRADLE, encoding="utf-8").read()
    expr = re.search(r"versionCode\s*=\s*([0-9\s+*]+)", text)
    name = re.search(r'versionName\s*=\s*"([^"]+)"', text)
    if not expr or not name:
        raise SystemExit("build.gradle.kts 里找不到 versionCode / versionName")
    # 版本号写法是 "1 * 100000 + 6 * 10000 + 7" 这种纯算术式：按 + 切段，段内相乘
    total = 0
    for part in expr.group(1).split("+"):
        product = 1
        for factor in part.split("*"):
            product *= int(factor.strip())
        total += product
    return total, name.group(1)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    notes = ""
    if "--notes" in sys.argv:
        notes = sys.argv[sys.argv.index("--notes") + 1]
    apk = args[0] if args else DEFAULT_APK
    if not os.path.exists(apk):
        raise SystemExit(f"APK 不存在：{apk}")

    code, name = read_version()
    os.makedirs(DOCS_APP, exist_ok=True)
    target_name = f"kikinews-{name}.apk"
    target = os.path.join(DOCS_APP, target_name)
    shutil.copyfile(apk, target)

    digest = sha256(target)
    manifest = {
        "versionCode": code,
        "versionName": name,
        "apk": BASE_URL + target_name,
        "sha256": digest,
        "size": os.path.getsize(target),
        "notes": notes or f"KIKINEWS {name}",
        "minSdk": 24,
    }
    with open(os.path.join(DOCS_APP, "version.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    # 老包留一份在本机根目录，方便直接发给别人
    shutil.copyfile(target, os.path.join("..", f"KIKINEWS-日报-v{name}.apk"))
    print(json.dumps(manifest, ensure_ascii=False, indent=1))
    print(f"[ok] {target}  {manifest['size'] / 1024:.0f} KB")


if __name__ == "__main__":
    main()
