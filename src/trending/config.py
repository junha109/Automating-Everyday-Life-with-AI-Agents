"""설정값 모음: 카테고리, 관심 분야 검색어, 경로, LLM 환경변수."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")  # 내 PC에서 실행할 때 .env의 키를 읽음 (Actions에서는 Secrets 사용)
SITE_DIR = ROOT / "site"
DATA_DIR = SITE_DIR / "data"          # 웹페이지가 그대로 읽는 JSON 위치
TRENDING_DIR = DATA_DIR / "trending"
INTEREST_DIR = DATA_DIR / "interest"
SNAPSHOT_DIR = INTEREST_DIR / "snapshots"  # 관심 분야 레포의 날짜별 스타 수
INDEX_FILE = DATA_DIR / "index.json"

# 탭 1: 전체 Trending 분류용 고정 카테고리
GENERAL_CATEGORIES = [
    "LLM·에이전트",
    "AI/ML (그 외)",
    "Web·Frontend",
    "DevTools·CLI",
    "Infra·Cloud·DevOps",
    "Data·DB",
    "Security",
    "Mobile·Desktop 앱",
    "학습자료",
    "기타",
]

# 탭 2: 관심 분야 분류용 고정 카테고리
INTEREST_CATEGORIES = [
    "재료 시뮬레이션",
    "재료 데이터·ML",
    "이차전지",
    "분석기기·데이터 처리",
    "과학계산 일반",
    "기타",
]

# 탭 2: GitHub Search API 검색어. 일부러 넓게 잡아서 관련 없는 레포도 섞이게 한다
# (예: "battery"로 들어오는 안드로이드 배터리 앱) → AI가 걸러내는지 검증 대상
INTEREST_QUERIES = [
    "topic:materials-science",
    "topic:computational-materials-science",
    "topic:materials-informatics",
    "topic:dft",
    "topic:density-functional-theory",
    "topic:molecular-dynamics",
    "topic:pymatgen",
    "topic:battery",
    "topic:lithium-ion",
    "topic:battery-management-system",
    "topic:electrochemistry",
    "topic:xrd",
    "topic:x-ray-diffraction",
    "topic:spectroscopy",
    "battery in:name,description",
]
INTEREST_RECENT_DAYS = 30      # 최근 N일 안에 push된 레포만 검색
INTEREST_MIN_STARS = 3         # 스타가 이보다 적은 레포는 추적하지 않음 (0스타 레포가 절반이라 노이즈)
INTEREST_TOP_N = 25            # 하루에 AI로 처리할 상위 레포 수 (관련 없는 레포가 섞여도 충분히 남도록)
WATCHLIST_REFRESH_CAP = 300    # 검색에 안 잡힌 기존 레포를 다시 조회할 최대 개수 (스타 많은 순)

README_MAX_CHARS = 6000        # LLM에 보낼 README 최대 길이
README_EXCERPT_CHARS = 1000      # 웹페이지 "원문 보기"에 저장할 README 앞부분 길이 (정리된 평문 기준)

# LLM (OpenAI 호환 API). 실제 값은 .env 또는 GitHub Secrets에만 둔다.
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")
LLM_DELAY_SEC = float(os.getenv("LLM_DELAY_SEC", "1.5"))  # 요청 간 간격 (분당 요청 제한 대비)
# 일부 추론형 모델(gpt-5 계열 등)은 temperature 지정을 거부하므로 기본은 보내지 않음
LLM_TEMPERATURE = os.getenv("LLM_TEMPERATURE", "")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
