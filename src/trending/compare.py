"""프롬프트 개선 전후 비교.

이미 저장한 실행 결과(JSON)의 레포들을 같은 README로 새 프롬프트에 다시 돌리고,
이전 결과와 나란히 비교한 마크다운 보고서를 만든다.
Trending은 시간이 지나면 바뀌므로, 같은 레포로 비교하려면 이 방식이 필요하다.

사용 예:
  uv run python -m trending.compare docs/real_runs/2026-10-29_trending_v1-prompt.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .evidence import warnings_for
from .github_api import default_client
from .llm import PROMPT_VERSION, Analyzer


def _cell(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ")


def build_report(old: dict, new: dict) -> str:
    ov, nv = old.get("prompt_version", "v1"), new["prompt_version"]
    o_by = {r["full_name"]: r for r in old["repos"]}
    lines = [
        f"# 프롬프트 {ov} → {nv} 비교 ({old['date']} Trending, 모델 {new['model']})",
        "",
        "## 요약",
        "",
        "| 항목 | " + ov + " | " + nv + " |",
        "|---|---|---|",
    ]
    oc = Counter(r["ai"]["confidence"] for r in old["repos"])
    nc = Counter(r["ai"]["confidence"] for r in new["repos"])
    lines.append(f"| confidence high/medium/low | {oc['high']}/{oc['medium']}/{oc['low']} "
                 f"| {nc['high']}/{nc['medium']}/{nc['low']} |")
    oi = sum(bool(r["ai"].get("llm_issues")) for r in old["repos"])
    ni = sum(bool(r["ai"].get("llm_issues")) for r in new["repos"])
    lines.append(f"| 출력 형식 보정 건수 | {oi} | {ni} |")
    changed = sum(o_by[r["full_name"]]["ai"]["category"] != r["ai"]["category"] for r in new["repos"])
    lines.append(f"| 카테고리가 바뀐 레포 | - | {changed}개 |")
    lines += ["", "### 분야별 개수", "", f"| 카테고리 | {ov} | {nv} |", "|---|---|---|"]
    for cat, n in new["category_counts"].items():
        lines.append(f"| {cat} | {old['category_counts'].get(cat, 0)} | {n} |")

    lines += ["", "## 레포별 비교", ""]
    for r in new["repos"]:
        o = o_by[r["full_name"]]
        oa, na = o["ai"], r["ai"]
        mark = " ⟵ 카테고리 변경" if oa["category"] != na["category"] else ""
        lines += [
            f"### #{r['rank']} {r['full_name']}{mark}",
            "",
            f"- 원문 설명: {r['description'] or '(없음)'}",
            "",
            f"| | {ov} | {nv} |",
            "|---|---|---|",
            f"| 카테고리 | {oa['category']} | {na['category']} |",
            f"| 분류 이유 | {_cell(oa.get('category_reason', '') or '-')} | {_cell(na.get('category_reason', ''))} |",
            f"| 설명 번역 | {_cell(oa['description_ko'])} | {_cell(na['description_ko'])} |",
            f"| confidence | {oa['confidence']} {_cell(oa.get('confidence_reason', ''))} "
            f"| {na['confidence']} {_cell(na.get('confidence_reason', ''))} |",
            f"| 형식 보정 | {_cell('; '.join(oa.get('llm_issues', [])) or '-')} "
            f"| {_cell('; '.join(na.get('llm_issues', [])) or '-')} |",
            f"| 요약 | {_cell(oa['summary_ko'])} | {_cell(na['summary_ko'])} |",
            "",
        ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="저장된 실행 결과를 새 프롬프트로 다시 돌려 비교")
    ap.add_argument("input", help="이전 실행 결과 JSON")
    ap.add_argument("--prompt-version", default=PROMPT_VERSION)
    args = ap.parse_args()

    src = Path(args.input)
    old = json.loads(src.read_text(encoding="utf-8"))
    analyzer = Analyzer(prompt_version=args.prompt_version)
    if analyzer.mock:
        raise SystemExit("LLM_API_KEY / LLM_MODEL이 설정되지 않았습니다 (.env 확인)")
    gh = default_client()

    tab = old.get("tab", "trending")
    records = []
    for o in old["repos"]:
        repo = {k: o[k] for k in ("full_name", "description", "language", "topics") if k in o}
        readme = gh.readme(o["full_name"])
        ai = analyzer.analyze(tab, repo, readme)
        rec = {**o, "ai": ai, "warnings": warnings_for(repo, readme, ai)}
        records.append(rec)
        flag = "변경" if ai["category"] != o["ai"]["category"] else "    "
        print(f"  #{o['rank']:>2} {o['full_name']:<40} {o['ai']['category']:<16} → {ai['category']:<16} {flag}")

    counts = Counter(r["ai"]["category"] for r in records)
    base = {**old["category_counts"]}
    new = {
        **{k: v for k, v in old.items() if k != "repos"},
        "prompt_version": analyzer.prompt_version,
        "model": analyzer.model,
        "category_counts": {k: counts.get(k, 0) for k in base},
        "repos": records,
    }
    stem = src.stem.replace("_v1-prompt", "")
    out_json = src.with_name(f"{stem}_{analyzer.prompt_version}-prompt.json")
    out_md = src.with_name(f"{stem}_compare_{old.get('prompt_version', 'v1')}_{analyzer.prompt_version}.md")
    out_json.write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding="utf-8")
    out_md.write_text(build_report(old, new), encoding="utf-8")
    print(f"\n저장: {out_json}\n비교 보고서: {out_md}")


if __name__ == "__main__":
    main()
