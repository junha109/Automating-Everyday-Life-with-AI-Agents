"""매일 실행되는 메인 파이프라인.

사용 예:
  uv run python -m trending.pipeline                 # 실제 수집 + AI 처리
  uv run python -m trending.pipeline --mock          # AI 대신 테스트 모드
  uv run python -m trending.pipeline --offline --mock --date 2026-10-30   # 네트워크 없이 샘플 데이터로
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone

from . import config, history, interest
from .evidence import clean_readme, readable_excerpt, warnings_for
from .github_api import GitHubAPI, default_client
from .llm import Analyzer
from .scrape_trending import fetch_trending_html, parse_trending

KST = timezone(timedelta(hours=9))


def _record(repo: dict, readme: str, ai: dict) -> dict:
    return {
        **repo,
        "readme_excerpt": readable_excerpt(readme, config.README_EXCERPT_CHARS),
        "readme_chars": len(clean_readme(readme)),
        "ai": ai,
        "warnings": warnings_for(repo, readme, ai),
    }


def run_trending(day: date, gh: GitHubAPI, analyzer: Analyzer, html: str | None = None) -> None:
    html = html if html is not None else fetch_trending_html()
    repos = parse_trending(html)
    if not repos:
        raise RuntimeError("Trending 파싱 결과가 0개입니다. 페이지 구조가 바뀌었는지 확인하세요.")
    print(f"[trending] {len(repos)}개 수집")

    records = []
    for r in repos:
        detail = gh.repo(r["full_name"]) or {}
        r["topics"] = detail.get("topics", [])
        if not r["description"]:
            r["description"] = detail.get("description") or ""
        readme = gh.readme(r["full_name"])
        ai = analyzer.analyze("trending", r, readme)
        records.append(_record(r, readme, ai))
        print(f"  #{r['rank']:>2} {r['full_name']:<45} → {ai['category']}")

    history.add_streaks("trending", day, records)
    counts = history.category_counts("trending", records)
    history.save_day("trending", day, {
        "date": day.isoformat(), "tab": "trending", "status": "ok",
        "model": analyzer.model, "prompt_version": analyzer.prompt_version,
        "category_counts": counts, "repos": records,
    })
    history.update_index("trending", day, counts, "ok")


def run_interest(day: date, gh: GitHubAPI, analyzer: Analyzer) -> None:
    found = interest.collect(gh, day)
    interest.save_snapshot(day, found)
    status, top, base_day = interest.rank_by_delta(day, found)
    print(f"[interest] 후보 {len(found)}개, 상태={status}, 상위 {len(top)}개 처리")

    records = []
    for r in top:
        readme = gh.readme(r["full_name"])
        ai = analyzer.analyze("interest", r, readme)
        records.append(_record(r, readme, ai))
        mark = "O" if ai.get("relevant") else "X"
        print(f"  #{r['rank']:>2} +{r['stars_delta']:<4} [{mark}] {r['full_name']:<45} → {ai['category']}")

    history.add_streaks("interest", day, records)
    counts = history.category_counts("interest", records)
    history.save_day("interest", day, {
        "date": day.isoformat(), "tab": "interest", "status": status,
        "compared_with": base_day, "candidates": len(found),
        "model": analyzer.model, "prompt_version": analyzer.prompt_version,
        "category_counts": counts, "repos": records,
    })
    history.update_index("interest", day, counts, status)


def main() -> None:
    ap = argparse.ArgumentParser(description="GitHub Trending 한국어 대시보드 데이터 생성")
    ap.add_argument("--date", help="기준일 YYYY-MM-DD (기본: 오늘, 한국 시간)")
    ap.add_argument("--tab", choices=["trending", "interest", "all"], default="all")
    ap.add_argument("--mock", action="store_true", help="AI 호출 없이 테스트 모드 결과 사용")
    ap.add_argument("--offline", action="store_true", help="GitHub 대신 tests/fixtures 샘플 사용")
    args = ap.parse_args()

    day = date.fromisoformat(args.date) if args.date else datetime.now(KST).date()
    analyzer = Analyzer(mock=args.mock)
    print(f"기준일 {day} · AI {'테스트 모드' if analyzer.mock else analyzer.model}")

    html = None
    if args.offline:
        from .offline import FakeGitHub, sample_trending_html
        gh = FakeGitHub(day)
        html = sample_trending_html(day)
    else:
        gh = default_client()

    if args.tab in ("trending", "all"):
        run_trending(day, gh, analyzer, html)
    if args.tab in ("interest", "all"):
        run_interest(day, gh, analyzer)


if __name__ == "__main__":
    main()
