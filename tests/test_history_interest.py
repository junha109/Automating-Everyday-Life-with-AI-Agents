from datetime import date

import pytest

from trending import config, history, interest


@pytest.fixture(autouse=True)
def tmp_data(tmp_path, monkeypatch):
    """테스트가 실제 site/data를 건드리지 않도록 임시 폴더로 바꾼다."""
    data = tmp_path / "data"
    monkeypatch.setattr(config, "DATA_DIR", data)
    monkeypatch.setattr(config, "TRENDING_DIR", data / "trending")
    monkeypatch.setattr(config, "INTEREST_DIR", data / "interest")
    monkeypatch.setattr(config, "SNAPSHOT_DIR", data / "interest" / "snapshots")
    monkeypatch.setattr(config, "INDEX_FILE", data / "index.json")


def _repo(name, stars):
    return {"full_name": name, "stars": stars}


def test_first_day_is_baseline():
    d = date(2026, 10, 30)
    repos = {"a/x": _repo("a/x", 10)}
    interest.save_snapshot(d, repos)
    status, top, base = interest.rank_by_delta(d, repos)
    assert status == "baseline" and top == [] and base is None


def test_delta_ranking_and_skip_gap_day():
    d1, d3 = date(2026, 10, 30), date(2026, 11, 1)  # 10/31 수집이 빠진 상황
    interest.save_snapshot(d1, {"a/x": _repo("a/x", 10), "b/y": _repo("b/y", 100)})
    today = {"a/x": _repo("a/x", 30), "b/y": _repo("b/y", 105), "c/new": _repo("c/new", 999)}
    status, top, base = interest.rank_by_delta(d3, today)
    assert status == "ok" and base == "2026-10-30"
    assert [r["full_name"] for r in top] == ["a/x", "b/y"]   # c/new는 비교 불가라 제외
    assert top[0]["stars_delta"] == 20 and top[0]["rank"] == 1


def test_streak_counts_consecutive_days():
    for day in (date(2026, 10, 28), date(2026, 10, 29), date(2026, 10, 30)):
        history.save_day("trending", day, {"repos": [{"full_name": "a/x"}]})
    history.save_day("trending", date(2026, 10, 26), {"repos": [{"full_name": "b/y"}]})
    # 10/31 결과를 계산하는 시점: a/x는 3일 연속 + 오늘, b/y는 중간에 끊김, z/new는 처음
    recs = [{"full_name": "a/x"}, {"full_name": "b/y"}, {"full_name": "z/new"}]
    history.add_streaks("trending", date(2026, 10, 31), recs)
    a, b, z = recs
    assert a["streak"] == 4 and a["is_new"] is False
    assert b["streak"] == 1 and b["is_new"] is False   # 5일 전에 있었으므로 재등장
    assert z["streak"] == 1 and z["is_new"] is True


def test_category_counts_interest_excludes_irrelevant():
    repos = [
        {"ai": {"category": "이차전지", "relevant": True}},
        {"ai": {"category": "이차전지", "relevant": False}},   # 배터리 '앱' 같은 경우
    ]
    c = history.category_counts("interest", repos)
    assert c["이차전지"] == 1 and set(c) == set(config.INTEREST_CATEGORIES)
