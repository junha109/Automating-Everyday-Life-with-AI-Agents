"""탭 2: 관심 분야 Trending.

GitHub에는 분야별 Trending이 없으므로 직접 만든다.
1) Search API로 관심 분야 레포를 매일 수집
2) 그날의 스타 수를 스냅샷으로 저장
3) 전날 스냅샷과 비교한 스타 증가량으로 순위 계산
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from . import config
from .github_api import GitHubAPI


def _snapshot_path(day: date) -> Path:
    return config.SNAPSHOT_DIR / f"{day.isoformat()}.json"


def load_snapshot(day: date) -> dict | None:
    p = _snapshot_path(day)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def latest_snapshot_before(day: date, max_lookback: int = 7) -> tuple[date, dict] | None:
    """가장 최근 이전 스냅샷 (수집이 하루 빠져도 비교 가능하도록 최대 7일 전까지)."""
    for back in range(1, max_lookback + 1):
        d = day - timedelta(days=back)
        snap = load_snapshot(d)
        if snap is not None:
            return d, snap
    return None


def _slim(item: dict) -> dict:
    return {
        "full_name": item["full_name"],
        "url": item["html_url"],
        "description": item.get("description") or "",
        "language": item.get("language"),
        "stars": item.get("stargazers_count", 0),
        "forks": item.get("forks_count", 0),
        "topics": item.get("topics", []),
        "pushed_at": item.get("pushed_at"),
    }


def collect(gh: GitHubAPI, day: date) -> dict[str, dict]:
    """검색어별로 레포를 모으고, 이전에 본 레포(watchlist)도 다시 조회한다."""
    since = (day - timedelta(days=config.INTEREST_RECENT_DAYS)).isoformat()
    found: dict[str, dict] = {}
    for q in config.INTEREST_QUERIES:
        for item in gh.search(f"{q} pushed:>={since} stars:>={config.INTEREST_MIN_STARS}"):
            rec = _slim(item)
            rec.setdefault("matched_queries", [])
            found.setdefault(rec["full_name"], rec)["matched_queries"].append(q)

    # 이전 스냅샷에는 있었지만 오늘 검색에 안 잡힌 레포 → 증가량 계산을 위해 직접 조회
    # 조회 횟수에 상한이 있으므로 스타가 많은(= 의미 있는 증가가 나올 가능성이 큰) 레포부터
    prev = latest_snapshot_before(day)
    if prev:
        missing = [n for n, s in prev[1]["repos"].items()
                   if n not in found and s >= config.INTEREST_MIN_STARS]
        missing.sort(key=lambda n: -prev[1]["repos"][n])
        for name in missing[: config.WATCHLIST_REFRESH_CAP]:
            item = gh.repo(name)
            if item:
                rec = _slim(item)
                rec["matched_queries"] = ["(watchlist)"]
                found[name] = rec
    return found


def save_snapshot(day: date, repos: dict[str, dict]) -> None:
    config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    snap = {"date": day.isoformat(), "repos": {n: r["stars"] for n, r in repos.items()}}
    _snapshot_path(day).write_text(json.dumps(snap, ensure_ascii=False), encoding="utf-8")


def rank_by_delta(day: date, repos: dict[str, dict]) -> tuple[str, list[dict], str | None]:
    """전날 대비 스타 증가량 순위.

    반환: (status, 상위 레포 목록, 비교 기준일)
    status = "ok" | "baseline"(비교할 이전 데이터 없음)
    """
    prev = latest_snapshot_before(day)
    if prev is None:
        return "baseline", [], None
    prev_day, prev_snap = prev
    ranked = []
    for name, rec in repos.items():
        before = prev_snap["repos"].get(name)
        if before is None:
            continue  # 오늘 처음 본 레포는 증가량을 알 수 없음
        delta = rec["stars"] - before
        if delta > 0:
            ranked.append({**rec, "stars_delta": delta})
    ranked.sort(key=lambda r: (-r["stars_delta"], -r["stars"]))
    top = ranked[: config.INTEREST_TOP_N]
    for i, r in enumerate(top, start=1):
        r["rank"] = i
    return "ok", top, prev_day.isoformat()
