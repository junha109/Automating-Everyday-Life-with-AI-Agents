# GitHub Trending 한국어 대시보드

**사이트: https://github-trending-ko.pages.dev**

매일 아침 GitHub Trending을 수집해 분야별로 분류하고, 한국어로 요약·번역해 웹페이지로 보여줍니다.
관심 분야(재료공학·이차전지·분석기기) 레포는 스타 증가량으로 별도 Trending을 계산합니다.

## 구조

```
src/trending/
  scrape_trending.py  # 탭1: github.com/trending HTML 파싱 (공식 API 없음)
  github_api.py       # GitHub REST API: 레포 상세, README, 검색
  interest.py         # 탭2: 관심 분야 검색 → 스타 스냅샷 → 전날 대비 증가량 순위
  llm.py              # AI: 분류·요약·번역·관련성 판정 (OpenAI 호환 API)
  evidence.py         # '근거 부족' 경고 배지 규칙
  history.py          # 날짜별 JSON 저장, 연속 등장 계산, index.json
  pipeline.py         # 전체 실행 진입점
  offline.py          # 네트워크 없이 개발하기 위한 샘플 데이터
site/                 # 웹페이지 (Cloudflare Pages 배포 대상)
  data/               # 파이프라인이 매일 쓰는 JSON
.github/workflows/daily.yml  # 매일 08:43 KST 자동 실행
docs/
  진행기록.md               # 과제 요구사항, 결정 사항, 구현 현황, 다음 할 일
  offline_sample_output/    # 샘플 데이터로 돌린 실행 결과·테스트 로그 (실제 데이터 아님)
```

## 내 PC에서 실행

```bash
uv sync
cp .env.example .env      # .env에 LLM_API_KEY, LLM_MODEL 입력
uv run pytest             # 단위 테스트
uv run python -m trending.pipeline --offline --mock   # 네트워크·AI 없이 시험 실행
uv run python -m trending.pipeline                    # 실제 실행
```

## 웹페이지 미리보기 (내 PC)

`site/index.html`을 더블클릭하면 브라우저 보안 때문에 데이터를 못 읽어요. 아래처럼 간이 서버로 여세요.

```bash
uv run python -m http.server -d site 8000
```

브라우저에서 http://localhost:8000 접속. 끝낼 때는 PowerShell에서 Ctrl+C.

## 자동 실행 설정 (GitHub)

1. 이 폴더를 GitHub 저장소로 올리기
2. Settings → Secrets and variables → Actions
   - **Secrets**: `LLM_API_KEY`, `LLM_BASE_URL`
   - **Variables**: `LLM_MODEL`
3. Actions 탭 → `daily-collect` → Run workflow로 한 번 수동 실행해서 확인

## 배포 (Cloudflare Pages)

Cloudflare 대시보드 **Workers & Pages → Create application → Pages → Connect to Git**에서 이 저장소를 연결.
Framework preset `None`, Build command 비움, Build output directory `site`.
매일 데이터 커밋이 올라오면 자동으로 다시 배포됩니다.
