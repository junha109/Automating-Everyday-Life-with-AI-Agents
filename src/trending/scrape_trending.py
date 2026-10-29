"""github.com/trending 페이지 수집.

Trending은 공식 API가 없어서 HTML을 직접 파싱한다.
페이지 구조가 바뀌면 여기만 고치면 되도록 파싱 로직을 한곳에 모았다.
"""
from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

TRENDING_URL = "https://github.com/trending"
_NUM = re.compile(r"[\d,]+")
_STARS_TODAY = re.compile(r"([\d,]+)\s+stars?\s+today", re.I)


def _to_int(text: str | None) -> int | None:
    if not text:
        return None
    m = _NUM.search(text)
    return int(m.group().replace(",", "")) if m else None


def fetch_trending_html(since: str = "daily", timeout: int = 30) -> str:
    resp = requests.get(
        TRENDING_URL,
        params={"since": since},
        headers={"User-Agent": "github-trending-ko/0.1", "Accept-Language": "en"},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.text


def parse_trending(html: str) -> list[dict]:
    """Trending HTML → 레포 목록 (페이지 순서 = 순위)."""
    soup = BeautifulSoup(html, "html.parser")
    repos = []
    for rank, row in enumerate(soup.select("article.Box-row"), start=1):
        link = row.select_one("h2 a[href]")
        if not link:
            continue
        full_name = link["href"].strip("/")
        if full_name.count("/") != 1:
            continue

        desc_el = row.select_one("p")
        lang_el = row.select_one('[itemprop="programmingLanguage"]')
        stars_el = row.select_one('a[href$="/stargazers"]')
        forks_el = row.select_one('a[href$="/forks"]')
        today_match = _STARS_TODAY.search(row.get_text(" ", strip=True))

        repos.append({
            "rank": rank,
            "full_name": full_name,
            "url": f"https://github.com/{full_name}",
            "description": desc_el.get_text(" ", strip=True) if desc_el else "",
            "language": lang_el.get_text(strip=True) if lang_el else None,
            "stars": _to_int(stars_el.get_text() if stars_el else None),
            "forks": _to_int(forks_el.get_text() if forks_el else None),
            "stars_today": _to_int(today_match.group(1)) if today_match else None,
        })
    return repos
