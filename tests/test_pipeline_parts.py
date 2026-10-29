from datetime import date

from trending import config
from trending.evidence import readme_language_hint, warnings_for
from trending.llm import _extract_json, _normalize
from trending.offline import sample_trending_html
from trending.scrape_trending import parse_trending


def test_parse_trending_fields():
    repos = parse_trending(sample_trending_html(date(2026, 10, 30)))
    assert repos, "파싱 결과가 비어 있음"
    r = repos[0]
    assert r["rank"] == 1
    assert r["full_name"].count("/") == 1
    assert isinstance(r["stars"], int) and r["stars"] > 0
    assert isinstance(r["stars_today"], int)
    # 설명이 없는 레포도 깨지지 않고 빈 문자열
    assert all(isinstance(x["description"], str) for x in repos)


def test_parse_ignores_non_repo_rows():
    html = '<article class="Box-row"><h2><a href="/sponsors">x</a></h2></article>'
    assert parse_trending(html) == []


def test_extract_json_with_code_fence():
    assert _extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert _extract_json('결과입니다: {"a": 2} 끝') == {"a": 2}


def test_normalize_fixes_unknown_category():
    out = _normalize("trending", {"category": "Gaming", "confidence": "sure"})
    assert out["category"] == "기타"
    assert out["confidence"] == "low"
    assert len(out["llm_issues"]) == 2


def test_normalize_interest_keeps_relevance():
    out = _normalize("interest", {"category": "이차전지", "confidence": "high", "relevant": True})
    assert out["category"] in config.INTEREST_CATEGORIES
    assert out["relevant"] is True and out["llm_issues"] == []


def test_language_hint():
    assert readme_language_hint("这是一个用于检索增强生成的工具包" * 5) == "중국어"
    assert readme_language_hint("This is an English readme " * 5) is None
    assert readme_language_hint("한국어로 쓴 설명입니다 " * 5) is None


def test_warnings():
    w = warnings_for({"description": ""}, "", {"confidence": "low", "confidence_reason": "근거 부족"})
    assert "README 없음" in w and "레포 설명 없음" in w
    assert any(x.startswith("AI 확신 낮음") for x in w)


def test_prompt_versions():
    from trending.llm import SYSTEM_PROMPT, _user_prompt
    repo = {"full_name": "a/b", "description": "x", "topics": []}
    v2 = _user_prompt("trending", repo, "readme")
    v1 = _user_prompt("trending", repo, "readme", "v1")
    assert "[카테고리 정의]" in v2 and "category_reason" in v2
    assert "[카테고리 정의]" not in v1
    assert "自学" in SYSTEM_PROMPT  # 번역 규칙 포함


def test_compare_report():
    from trending.compare import build_report
    ai = lambda c, conf: {"category": c, "confidence": conf, "summary_ko": "s", "description_ko": "d", "llm_issues": []}
    old = {"date": "2026-10-29", "category_counts": {"A": 1, "B": 0},
           "repos": [{"full_name": "a/b", "rank": 1, "description": "x", "ai": ai("A", "high")}]}
    new = {**old, "prompt_version": "v2", "model": "m", "category_counts": {"A": 0, "B": 1},
           "repos": [{"full_name": "a/b", "rank": 1, "description": "x", "ai": ai("B", "medium")}]}
    md = build_report(old, new)
    assert "카테고리 변경" in md and "| 카테고리가 바뀐 레포 | - | 1개 |" in md


def test_readable_excerpt():
    from trending.evidence import readable_excerpt
    md = """# π RuView

<p align="center"><img src="x.png"></p>

[ ](docs/user-guide.md)

      Start here
      Hardware

## **See through walls with WiFi** ##

**Turn ordinary WiFi into a spatial intelligence / sensing system.** Detect people, measure breathing,
and monitor rooms — through walls, with **[Home Assistant](docs/ha.md)** support.

```bash
pip install ruview
```

| a | b |
|---|---|
- Works with the four major smart-home ecosystems out of the box
"""
    out = readable_excerpt(md)
    assert "Start here" not in out and "<" not in out and "](" not in out and "pip install" not in out
    assert "# See through walls with WiFi" in out
    assert "Turn ordinary WiFi into a spatial intelligence / sensing system. Detect people" in out
    assert "with Home Assistant support." in out
    assert "• Works with the four major" in out
    assert len(readable_excerpt("word " * 500, 100)) <= 101
