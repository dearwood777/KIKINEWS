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
    monkeypatch.setattr(bv, "CEFR", {})


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


# ---------- 派生词排除 ----------

def test_derived_rejects_when_root_not_in_dictionary():
    # 词库里没有 repar 这个词条时，reparation 不能被当成“repar 的派生”吞掉
    assert bv.derived_from_known("reparation", {}) is False


def test_derived_accepts_when_root_is_well_known():
    bases = {"care": entry("care", frq=1200, collins=4, oxford=1)}
    assert bv.derived_from_known("careless", bases) is True
