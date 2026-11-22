# 从 docs/fonts/kiki-head-700.woff2（报头专用字体子集）导出字形轮廓，
# 生成 scripts/head_glyphs.json，供 web_polish.py 注入到页面做"小人行走骨架"。
# 只依赖 fontTools；字体是 Noto Sans SC 子集（OFL 授权），可自由分发。
import json, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen

ROOT = r"D:\AI\KIKINEWS\repo"
FONT = os.path.join(ROOT, "docs", "fonts", "kiki-head-700.woff2")
OUT = os.path.join(ROOT, "scripts", "head_glyphs.json")
TEXT = "科技 · 财经 · 国际速递"

f = TTFont(FONT)
gs = f.getGlyphSet()
cmap = f.getBestCmap()
upm = f["head"].unitsPerEm
os2 = f["OS/2"]
hhea = f["hhea"]
print("upm", upm, "hhea asc/desc", hhea.ascent, hhea.descent,
      "typo", os2.sTypoAscender, os2.sTypoDescender, "win", os2.usWinAscent, os2.usWinDescent)

data = {"upm": upm, "ascent": hhea.ascent, "descent": hhea.descent, "d": {}, "adv": {}}
for ch in set(TEXT):
    gn = cmap.get(ord(ch))
    if not gn:
        print("MISSING", repr(ch)); continue
    pen = SVGPathPen(gs)
    gs[gn].draw(pen)
    d = pen.getCommands().replace('"', "'")
    data["d"][ch] = d
    data["adv"][ch] = f["hmtx"][gn][0]

open(OUT, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
print("wrote", OUT, os.path.getsize(OUT), "bytes; glyphs", len(data["d"]))
print("dot path:", data["d"].get("·", "")[:120])
