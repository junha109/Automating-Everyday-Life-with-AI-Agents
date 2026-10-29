"""GitHub REST API 호출 (레포 상세, README, 검색)."""
from __future__ import annotations

import time

import requests

from . import config

API = "https://api.github.com"


class GitHubAPI:
    def __init__(self, token: str = ""):
        self.s = requests.Session()
        self.s.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "github-trending-ko/0.1",
        })
        if token:
            self.s.headers["Authorization"] = f"Bearer {token}"

    def _get(self, path: str, **kw) -> requests.Response:
        for attempt in range(3):
            r = self.s.get(f"{API}{path}", timeout=30, **kw)
            # 검색 API는 분당 요청 제한이 있어서 403/429면 잠시 기다렸다 재시도
            if r.status_code in (403, 429) and "rate limit" in r.text.lower():
                reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
                time.sleep(min(max(reset - time.time(), 5), 90))
                continue
            return r
        return r

    def repo(self, full_name: str) -> dict | None:
        r = self._get(f"/repos/{full_name}")
        return r.json() if r.ok else None

    def readme(self, full_name: str) -> str:
        """README 원문(raw). 없으면 빈 문자열."""
        r = self._get(
            f"/repos/{full_name}/readme",
            headers={"Accept": "application/vnd.github.raw+json"},
        )
        return r.text if r.ok else ""

    def search(self, query: str, per_page: int = 100, sort: str = "stars") -> list[dict]:
        # sort=stars: 날마다 비슷한 레포가 잡혀야 스타 증가량을 비교할 수 있음
        # (updated 순은 매일 결과가 크게 바뀌어서 전날과 비교할 수 없는 레포가 많아짐)
        r = self._get(
            "/search/repositories",
            params={"q": query, "sort": sort, "order": "desc", "per_page": per_page},
        )
        if not r.ok:
            print(f"[warn] search failed ({r.status_code}): {query}")
            return []
        time.sleep(2.5)  # 인증 시 분당 30회 제한 → 여유 있게
        return r.json().get("items", [])


def default_client() -> GitHubAPI:
    return GitHubAPI(config.GITHUB_TOKEN)
