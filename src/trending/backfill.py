"""AI 처리가 실패한 날의 레포만 골라 AI 판단을 다시 채운다 (수집은 다시 하지 않음).

Trending은 지난 날짜를 다시 볼 수 없지만, 그날 어떤 레포가 몇 위였는지는 이미 저장돼 있다.
그 목록 그대로 README를 다시 받아 AI 분류·요약·번역만 새로 한다.

주의 (보고서에 밝힐 점)
- README는 '오늘' 받은 것이다. 그날 이후 README가 바뀌었다면 그날 결과와 다를 수 있다.
- 기본값은 같은 레포를 탭마다 한 번만 AI에 보내고 여러 날에 같은 결과를 넣는다 (요청 수 절약).
  날마다 따로 보내려면 --per-day.
- 다시 채운 레포에는 ai.backfilled_at이 붙는다. 날짜별 일관성 분석에서는 이 레포들을 빼야 한다
  (실제 그날 실행한 결과가 아니므로).

사용 예:
  uv run python -m trending.backfill --dry-run                 # 대상만 확인
  uv run python -m trending.backfill --from 2026-11-18 --to 2026-11-27
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone

from . import config, history
from .evidence import warnings_for
from .github_api import default_client
from .llm import Analyzer

KST = timezone(timedelta(hours=9))
TABS = ("trending", "interest")


def is_failed(r: dict) -> bool:
    ai = r.get("ai") or {}
    return str(ai.get("confidence_reason", "")).startswith("AI 처리 실패")


def find_targets(start: date, end: date, tabs=TABS) -> list[tuple[str, date, dict]]:
    """(탭, 날짜, 그날 JSON) 중 AI 실패 레포가 하나라도 있는 것."""
    out = []
    d = start
    while d <= end:
        for tab in tabs:
            data = history.load_day(tab, d)
            if data and any(is_failed(r) for r in data.get("repos", [])):
                out.append((tab, d, data))
        d += timedelta(days=1)
    return out


def _repo_fields(r: dict) -> dict:
    # AI 프롬프트에 들어가는 값만 (AI 결과·배지 등 이전 처리 결과는 넣지 않음)
    return {k: v for k, v in r.items() if k not in ("ai", "warnings", "readme_excerpt", "readme_chars")}


def main(argv: list[str] | None = None, gh=None, analyzer: Analyzer | None = None) -> int:
    ap = argparse.ArgumentParser(description="AI 처리가 실패한 날짜의 AI 결과 다시 채우기")
    ap.add_argument("--from", dest="start", default="2026-10-29", help="시작일 YYYY-MM-DD")
    ap.add_argument("--to", dest="end", help="종료일 YYYY-MM-DD (기본: 오늘)")
    ap.add_argument("--tab", choices=["trending", "interest", "all"], default="all")
    ap.add_argument("--per-day", action="store_true", help="같은 레포도 날마다 따로 AI에 보냄")
    ap.add_argument("--dry-run", action="store_true", help="대상만 출력하고 저장하지 않음")
    args = ap.parse_args(argv)

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end) if args.end else datetime.now(KST).date()
    tabs = TABS if args.tab == "all" else (args.tab,)
    targets = find_targets(start, end, tabs)

    total = sum(sum(is_failed(r) for r in data["repos"]) for _, _, data in targets)
    unique = {(tab, r["full_name"]) for tab, _, data in targets for r in data["repos"] if is_failed(r)}
    print(f"대상: {len(targets)}개 파일, 실패 레코드 {total}건, 고유 레포 {len(unique)}개")
    for tab, d, data in targets:
        n = sum(is_failed(r) for r in data["repos"])
        print(f"  {tab:<9} {d}  {n}/{len(data['repos'])}")
    if args.dry_run or not targets:
        print(f"AI 요청 예상: {total if args.per_day else len(unique)}회")
        return 0

    analyzer = analyzer or Analyzer()
    if analyzer.mock:
        raise SystemExit("LLM_API_KEY / LLM_MODEL이 설정되지 않았습니다 (.env 또는 Secrets 확인)")
    gh = gh or default_client()
    stamp = datetime.now(KST).isoformat(timespec="seconds")
    readmes: dict[str, str] = {}
    cache: dict[tuple[str, str], dict] = {}
    fixed = failed = 0

    for tab, d, data in targets:
        print(f"[{tab} {d}]")
        for r in data["repos"]:
            if not is_failed(r):
                continue
            name = r["full_name"]
            if name not in readmes:
                readmes[name] = gh.readme(name)
            readme = readmes[name]
            repo = _repo_fields(r)
            key = (tab, name)
            ai = None if args.per_day else cache.get(key)
            if ai is None:
                ai = analyzer.analyze(tab, repo, readme)
            if is_failed({"ai": ai}):
                failed += 1
                print(f"  실패  {name}: {ai['confidence_reason'][:120]}")
                continue  # 실패한 건 그대로 두고 다음 실행 때 다시 시도
            cache[key] = ai
            r["ai"] = {**ai, "backfilled_at": stamp, "temperature": config.temperature()}
            r["warnings"] = warnings_for(repo, readme, ai)
            fixed += 1
            print(f"  채움  {name:<45} → {ai['category']}")

        counts = history.category_counts(tab, data["repos"])
        data["category_counts"] = counts
        data["model"] = analyzer.model
        data["prompt_version"] = analyzer.prompt_version
        data["backfilled_at"] = stamp
        history.save_day(tab, d, data)
        history.update_index(tab, d, counts, data.get("status", "ok"))

    print(f"\n완료: 채움 {fixed}건, 실패 {failed}건")
    if failed:
        print("실패한 건은 그대로 남겨 두었습니다. 같은 명령을 다시 실행하면 그것만 다시 시도합니다.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
