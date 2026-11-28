import json
from datetime import date

import pytest

from trending import backfill, config, history


@pytest.fixture(autouse=True)
def tmp_data(tmp_path, monkeypatch):
    data = tmp_path / "data"
    monkeypatch.setattr(config, "DATA_DIR", data)
    monkeypatch.setattr(config, "TRENDING_DIR", data / "trending")
    monkeypatch.setattr(config, "INTEREST_DIR", data / "interest")
    monkeypatch.setattr(config, "INDEX_FILE", data / "index.json")


FAIL = {"category": "기타", "summary_ko": "", "description_ko": "", "confidence": "low",
        "confidence_reason": "AI 처리 실패: Error code: 404", "llm_issues": []}


class FakeGH:
    def __init__(self):
        self.calls = 0

    def readme(self, name):
        self.calls += 1
        return f"# {name}\nreadme text " * 20


class FakeAnalyzer:
    mock = False
    model = "claude-haiku-4-5"
    prompt_version = "v2"

    def __init__(self, fail=()):
        self.calls, self.fail = 0, set(fail)

    def analyze(self, tab, repo, readme):
        self.calls += 1
        if repo["full_name"] in self.fail:
            return dict(FAIL)
        return {"category": "DevTools·CLI", "summary_ko": "요약", "description_ko": "번역",
                "confidence": "high", "confidence_reason": "", "llm_issues": []}


def _save(day, names, ok=()):
    repos = [{"rank": i + 1, "full_name": n, "description": "", "streak": 1, "is_new": False,
              "ai": dict(FAIL) if n not in ok else {"category": "Security", "summary_ko": "기존",
                                                   "confidence": "high", "confidence_reason": ""},
              "warnings": []} for i, n in enumerate(names)]
    history.save_day("trending", day, {"date": day.isoformat(), "tab": "trending", "status": "ok",
                                       "model": "x", "prompt_version": "v2",
                                       "category_counts": {}, "repos": repos})


def test_backfill_fills_failed_only_and_reuses_per_repo():
    d1, d2 = date(2026, 11, 18), date(2026, 11, 19)
    _save(d1, ["a/x", "b/y", "c/ok"], ok={"c/ok"})
    _save(d2, ["a/x", "b/y"])
    an, gh = FakeAnalyzer(), FakeGH()
    rc = backfill.main(["--from", "2026-11-18", "--to", "2026-11-19", "--tab", "trending"], gh, an)
    assert rc == 0
    assert an.calls == 2 and gh.calls == 2          # 레포마다 한 번씩만
    day1 = history.load_day("trending", d1)
    by = {r["full_name"]: r for r in day1["repos"]}
    assert by["a/x"]["ai"]["summary_ko"] == "요약" and "backfilled_at" in by["a/x"]["ai"]
    assert by["c/ok"]["ai"]["summary_ko"] == "기존"   # 성공한 기록은 건드리지 않음
    assert day1["category_counts"]["DevTools·CLI"] == 2 and day1["category_counts"]["Security"] == 1
    assert day1["repos"][0]["streak"] == 1             # 연속 등장 등 수집 정보 유지
    idx = json.loads(config.INDEX_FILE.read_text(encoding="utf-8"))
    assert idx["tabs"]["trending"]["counts"]["2026-11-19"]["DevTools·CLI"] == 2


def test_backfill_keeps_failures_for_retry():
    d = date(2026, 11, 20)
    _save(d, ["a/x", "b/y"])
    rc = backfill.main(["--from", "2026-11-20", "--to", "2026-11-20", "--tab", "trending"],
                       FakeGH(), FakeAnalyzer(fail={"b/y"}))
    assert rc == 1
    by = {r["full_name"]: r for r in history.load_day("trending", d)["repos"]}
    assert by["a/x"]["ai"]["summary_ko"] == "요약"
    assert backfill.is_failed(by["b/y"])
    # 다시 실행하면 남은 것만 시도
    an = FakeAnalyzer()
    assert backfill.main(["--from", "2026-11-20", "--to", "2026-11-20"], FakeGH(), an) == 0
    assert an.calls == 1


def test_per_day_sends_each_day():
    _save(date(2026, 11, 18), ["a/x"])
    _save(date(2026, 11, 19), ["a/x"])
    an = FakeAnalyzer()
    backfill.main(["--from", "2026-11-18", "--to", "2026-11-19", "--per-day"], FakeGH(), an)
    assert an.calls == 2
