"""날짜별 결과 저장, 연속 등장(streak) 계산, index.json 갱신.

연속 등장·신규 진입은 AI 없이 코드로만 계산한다 (AI 결과와 대비되는 '확정적' 정보).
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from . import config


def _day_file(tab: str, day: date) -> Path:
    base = config.TRENDING_DIR if tab == "trending" else config.INTEREST_DIR
    return base / f"{day.isoformat()}.json"


def load_day(tab: str, day: date) -> dict | None:
    p = _day_file(tab, day)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _names(tab: str, day: date) -> set[str] | None:
    d = load_day(tab, day)
    if d is None:
        return None
    return {r["full_name"] for r in d.get("repos", [])}


def add_streaks(tab: str, day: date, repos: list[dict]) -> None:
    """각 레포에 streak(오늘 포함 연속 등장 일수)과 is_new(이전 기록에 없던 레포)를 붙인다."""
    cache: dict[date, set[str] | None] = {}

    def names(d: date):
        if d not in cache:
            cache[d] = _names(tab, d)
        return cache[d]

    for r in repos:
        n, streak, d = r["full_name"], 1, day - timedelta(days=1)
        while (s := names(d)) is not None and n in s:
            streak += 1
            d -= timedelta(days=1)
        r["streak"] = streak
        # 신규 진입: 최근 30일 기록 어디에도 없던 레포
        r["is_new"] = not any(
            (s := names(day - timedelta(days=k))) is not None and n in s for k in range(1, 31)
        )


def category_counts(tab: str, repos: list[dict]) -> dict[str, int]:
    cats = config.GENERAL_CATEGORIES if tab == "trending" else config.INTEREST_CATEGORIES
    pool = repos if tab == "trending" else [r for r in repos if r["ai"].get("relevant")]
    c = Counter(r["ai"]["category"] for r in pool)
    return {k: c.get(k, 0) for k in cats}


def save_day(tab: str, day: date, payload: dict) -> Path:
    p = _day_file(tab, day)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def update_index(tab: str, day: date, counts: dict[str, int], status: str) -> None:
    """웹페이지가 처음 읽는 파일: 날짜 목록 + 날짜별 분야 개수(추이 차트용)."""
    idx = {"tabs": {}}
    if config.INDEX_FILE.exists():
        idx = json.loads(config.INDEX_FILE.read_text(encoding="utf-8"))
    idx.setdefault("tabs", {})
    idx["categories"] = {
        "trending": config.GENERAL_CATEGORIES,
        "interest": config.INTEREST_CATEGORIES,
    }
    t = idx["tabs"].setdefault(tab, {"dates": [], "counts": {}, "status": {}})
    key = day.isoformat()
    if key not in t["dates"]:
        t["dates"].append(key)
        t["dates"].sort()
    t["counts"][key] = counts
    t["status"][key] = status
    config.INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.INDEX_FILE.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
