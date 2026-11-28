"""같은 레포를 여러 날 처리한 AI 결과가 얼마나 같은지 집계한다 (AI 호출 없음).

temperature 설정별로 나눠 집계하므로, 설정을 바꾼 전후를 한 번에 비교할 수 있다.
- 원문 설명이 날마다 같았던 레포만 센다 (원문이 바뀌면 번역이 달라지는 게 정상)
- backfill로 다시 채운 결과는 그날 실행한 결과가 아니므로 뺀다

사용 예:
  uv run python -m trending.consistency
  uv run python -m trending.consistency --from 2026-11-29
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

from . import config

TABS = ("trending", "interest")


def _label(t) -> str:
    return "기본값(미지정)" if t is None else f"temperature {t:g}"


def collect(tab: str, start: str = "", end: str = "") -> dict:
    """{설정: {레포: [(날짜, 레코드), ...]}}"""
    base = config.TRENDING_DIR if tab == "trending" else config.INTEREST_DIR
    out: dict = defaultdict(lambda: defaultdict(list))
    for p in sorted(base.glob("*.json")):
        day = p.stem
        if (start and day < start) or (end and day > end):
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        temp = data.get("temperature")
        for r in data.get("repos", []):
            ai = r.get("ai") or {}
            if "backfilled_at" in ai or str(ai.get("confidence_reason", "")).startswith("AI 처리 실패"):
                continue
            out[temp][r["full_name"]].append((day, r))
    return out


def summarize(tab: str, groups: dict) -> list[dict]:
    rows = []
    for temp, repos in groups.items():
        n = cat_same = desc_same = rel_same = 0
        examples = []
        for name, items in repos.items():
            if len(items) < 2 or len({r.get("description", "") for _, r in items}) != 1:
                continue
            n += 1
            cats = {r["ai"].get("category") for _, r in items}
            descs = {r["ai"].get("description_ko", "") for _, r in items}
            cat_same += len(cats) == 1
            desc_same += len(descs) == 1
            if tab == "interest":
                rel_same += len({bool(r["ai"].get("relevant")) for _, r in items}) == 1
            if len(descs) > 1:
                examples.append((len(descs), len(items), name))
        rows.append({
            "tab": tab, "setting": _label(temp), "repos": n, "category_same": cat_same,
            "translation_same": desc_same, "relevance_same": rel_same if tab == "interest" else None,
            "most_varied": sorted(examples, reverse=True)[:3],
        })
    return rows


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="날짜별 AI 결과 일관성 집계 (temperature 설정별)")
    ap.add_argument("--from", dest="start", default="")
    ap.add_argument("--to", dest="end", default="")
    args = ap.parse_args(argv)

    print("| 탭 | 설정 | 2일 이상·원문 같은 레포 | 분류 매일 같음 | 번역 매일 같음 | 관련성 매일 같음 |")
    print("|---|---|---|---|---|---|")
    notes = []
    for tab in TABS:
        for s in summarize(tab, collect(tab, args.start, args.end)):
            n = s["repos"] or 1
            rel = "-" if s["relevance_same"] is None else f"{s['relevance_same']} ({s['relevance_same'] / n:.0%})"
            print(f"| {tab} | {s['setting']} | {s['repos']} | {s['category_same']} ({s['category_same'] / n:.0%}) "
                  f"| {s['translation_same']} ({s['translation_same'] / n:.0%}) | {rel} |")
            for k, days, name in s["most_varied"]:
                notes.append(f"- {tab} · {s['setting']} · {name}: {days}일 중 번역 {k}가지")
    if notes:
        print("\n번역이 가장 많이 달라진 레포")
        print("\n".join(notes))


if __name__ == "__main__":
    main()
