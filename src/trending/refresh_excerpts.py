"""이미 저장한 JSON의 '원문 보기'용 README 앞부분만 다시 만든다 (AI 호출 없음).

README 정리 방식을 바꾼 뒤, 예전에 수집한 데이터에도 적용하기 위한 일회성 도구.

사용 예:
  uv run python -m trending.refresh_excerpts
"""
from __future__ import annotations

import json

from . import config
from .evidence import clean_readme, readable_excerpt
from .github_api import default_client


def main() -> None:
    gh = default_client()
    readmes: dict[str, str] = {}
    files = sorted(config.TRENDING_DIR.glob("*.json")) + sorted(config.INTEREST_DIR.glob("*.json"))
    files += sorted((config.ROOT / "docs" / "real_runs").glob("*.json"))
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        repos = data.get("repos", [])
        if not repos:
            continue
        for r in repos:
            name = r["full_name"]
            if name not in readmes:
                readmes[name] = gh.readme(name)
            readme = readmes[name]
            r["readme_excerpt"] = readable_excerpt(readme, config.README_EXCERPT_CHARS)
            r["readme_chars"] = len(clean_readme(readme))
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"갱신: {path.relative_to(config.ROOT)} ({len(repos)}개)")


if __name__ == "__main__":
    main()
