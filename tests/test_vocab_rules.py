"""难点词汇判定规则的回归测试。

不依赖词库文件：用假的词条字典喂给判定函数，专测这几条容易踩的规则。
"""
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_vocab.py"
spec = importlib.util.spec_from_file_location("kiki_build_vocab", SCRIPT)
bv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bv)


def entry(word, frq=0, bnc=0, collins="0", oxford="0", tag="", translation="n. 测试"):
    return {
        "word": word,
        "phonetic": "test",
        "translation": translation,
        "collins": str(collins),
        "oxford": str(oxford),
        "tag": tag,
        "pos": "n",
        "frq": frq,
        "bnc": bnc,
    }


@pytest.fixture(autouse=True)
def _cefr(monkeypatch):
    """默认关掉 CEFR 与 Zipf 两路外部数据，让每条测试只测自己要测的那条规则。"""
    monkeypatch.setattr(bv, "CEFR", {})
    monkeypatch.setattr(bv, "_zipf", lambda word: 0.0)


# ---------- 变形回推 ----------

def test_inflection_candidates_plural():
    assert bv.inflection_candidates("dozens")[0] == "dozen"
    assert bv.inflection_candidates("reparations")[0] == "reparation"


def test_inflection_candidates_ed_ing():
    assert set(bv.inflection_candidates("convened")) & {"convene"}
    assert set(bv.inflection_candidates("running")) & {"run", "runn", "runne"}


def test_inflection_candidates_short_word_untouched():
    assert bv.inflection_candidates("gas") == []


def test_resolve_falls_back_to_inflected_base():
    bases = {"dozen": entry("dozen", frq=1194)}
    assert bv.resolve_form("dozens", {}, bases) == "dozen"


def test_resolve_prefers_dictionary_link():
    bases = {"do": entry("do", frq=10), "doe": entry("doe", frq=5000)}
    rev = {"does": ["do", "doe"]}
    assert bv.resolve_form("does", rev, bases) == "do"


def test_resolve_keeps_token_when_nothing_found():
    assert bv.resolve_form("zzzzs", {}, {}) == "zzzzs"


# ---------- 已知证据 ----------

def test_b1_word_counts_as_known(monkeypatch):
    monkeypatch.setattr(bv, "CEFR", {"organ": "B1"})
    assert bv.known_evidence(entry("organ", frq=3101, collins=2, oxford=1)) == 10


def test_rare_c1_word_is_treated_as_unknown(monkeypatch):
    monkeypatch.setattr(bv, "CEFR", {"persecution": "C1"})
    assert bv.known_evidence(entry("persecution", frq=8852)) == 0


def test_common_c1_word_counts_as_known(monkeypatch):
    monkeypatch.setattr(bv, "CEFR", {"verdict": "C1"})
    assert bv.known_evidence(entry("verdict", frq=4163, collins=2)) == 2


def test_rare_unlisted_word_has_no_evidence():
    assert bv.known_evidence(entry("reparation", frq=13025, collins=1)) == 0


def test_missing_entry_is_unknown_to_reader():
    assert bv.known_evidence(None) == 99


# ---------- 常用词频段：词库没给 CEFR 也不能算超纲 ----------
# 11-21 期线上 38 张卡里，tech / reportedly / trillion / landmark / precedent /
# paradigm / deepen 这一批都是“词库排 4500–8000 名、又没 CEFR 等级”，
# 早前按零证据进超纲层，读者其实都认识。

def test_midfrequency_word_counts_as_familiar():
    assert bv.known_evidence(entry("tech", frq=4973)) == 2


def test_familiar_band_upper_edge():
    assert bv.known_evidence(entry("bail", frq=6736, collins=2)) == 2


def test_collins_one_star_beyond_familiar_band_is_unknown():
    # 5700 名之后、Collins 只给 1 星：没有别的证据，仍然按超纲处理（erase 这类
    # 边界词留着，宁可多一张也不漏掉真生词）。
    assert bv.known_evidence(entry("erase", frq=5776, collins=1)) == 0
    assert bv.known_evidence(entry("drizzle", frq=6200, collins=1)) == 0


def test_collins_weak_evidence_stops_at_common_rank():
    assert bv.known_evidence(entry("obsidian", frq=8500, collins=2)) == 0


# ---------- Zipf 词频（wordfreq）作为额外证据 ----------

def test_zipf_strong_marks_known(monkeypatch):
    monkeypatch.setattr(bv, "_zipf", lambda w: 4.69)   # tech
    assert bv.known_evidence(entry("tech", frq=4973)) == 3


def test_zipf_familiar_marks_known_weakly(monkeypatch):
    monkeypatch.setattr(bv, "_zipf", lambda w: 3.9)    # genocide / trillion 一档
    assert bv.known_evidence(entry("trillion", frq=5167)) == 2


def test_zipf_low_leaves_rare_word_unknown(monkeypatch):
    monkeypatch.setattr(bv, "_zipf", lambda w: 2.47)   # adjudicate
    assert bv.known_evidence(entry("adjudicate", frq=18877)) == 0


def test_zipf_marks_unranked_compound_known(monkeypatch):
    # 词库查不到排名的透明复合词（record-breaking），Zipf 是唯一信号
    monkeypatch.setattr(bv, "_zipf", lambda w: 4.61)
    assert bv.known_evidence(entry("record-breaking", frq=0)) == 3


# ---------- 派生词排除 ----------

def test_derived_rejects_when_root_not_in_dictionary():
    # 词库里没有 repar 这个词条时，reparation 不能被当成“repar 的派生”吞掉
    assert bv.derived_from_known("reparation", {}) is False


def test_derived_accepts_when_root_is_well_known():
    bases = {"care": entry("care", frq=1200, collins=4, oxford=1)}
    assert bv.derived_from_known("careless", bases) is True


# ---------- 卡片复核：模型投票的边界 ----------

def _card(word, rank, *, sense="", gloss="n. 测试"):
    return {"word": word, "rank": rank, "gloss": gloss, "sense": sense, "ctx": "ctx ..."}


def test_audit_drops_only_grey_band_words(monkeypatch):
    calls = []

    def fake_llm(prompt):
        calls.append(prompt)
        return '{"drop": ["trillion", "adjudicate"], "drop_sense": []}', {}, "fake"

    monkeypatch.setattr(bv, "_llm_call", fake_llm)
    monkeypatch.setenv("GROQ_API_KEY", "x")
    monkeypatch.setattr(bv, "save_verdicts", lambda v: None)

    verdicts = bv.audit_cards(
        [_card("trillion", 5167), _card("adjudicate", 18877)], verdicts={}
    )
    assert verdicts["trillion"] == "drop"      # 灰区，采纳
    assert verdicts["adjudicate"] == "keep"    # 9000 名以后的真难词，不接受删卡
    assert len(calls) == 1


def test_audit_ignores_sense_flag_on_plain_cards(monkeypatch):
    monkeypatch.setattr(bv, "_llm_call",
                        lambda p: ('{"drop": [], "drop_sense": ["susceptible"]}', {}, "fake"))
    monkeypatch.setenv("GROQ_API_KEY", "x")
    verdicts = bv.audit_cards([_card("susceptible", 6934)], verdicts={})
    assert verdicts["susceptible"] == "keep"


def test_audit_respects_cached_verdicts(monkeypatch):
    calls = []

    def fake_llm(prompt):
        calls.append(prompt)
        return '{"drop": [], "drop_sense": []}', {}, "fake"

    monkeypatch.setattr(bv, "_llm_call", fake_llm)
    monkeypatch.setenv("GROQ_API_KEY", "x")
    verdicts = bv.audit_cards(
        [_card("deepen", 6730)], verdicts={"deepen": "drop"}
    )
    assert verdicts["deepen"] == "drop"
    assert calls == []  # 缓存命中就不再花一次模型调用


def test_audit_keeps_everything_when_model_output_is_broken(monkeypatch):
    monkeypatch.setattr(bv, "_llm_call", lambda p: ("抱歉，我无法判断。", {}, "fake"))
    monkeypatch.setenv("GROQ_API_KEY", "x")
    verdicts = bv.audit_cards([_card("landmark", 4715)], verdicts={})
    assert verdicts.get("landmark") in (None, "keep")


def test_audit_noop_without_api_key(monkeypatch):
    for key in ("GROQ_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(bv, "_llm_call", lambda p: (_ for _ in ()).throw(AssertionError))
    assert bv.audit_cards([_card("tech", 4973)], verdicts={}) == {}
