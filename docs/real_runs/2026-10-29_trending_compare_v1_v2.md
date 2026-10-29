# 프롬프트 v1 → v2 비교 (2026-10-29 Trending, 모델 anthropic/claude-haiku-4.5)

## 요약

| 항목 | v1 | v2 |
|---|---|---|
| confidence high/medium/low | 14/0/0 | 12/2/0 |
| 출력 형식 보정 건수 | 1 | 0 |
| 카테고리가 바뀐 레포 | - | 5개 |

### 분야별 개수

| 카테고리 | v1 | v2 |
|---|---|---|
| LLM·에이전트 | 4 | 9 |
| AI/ML (그 외) | 0 | 0 |
| Web·Frontend | 1 | 1 |
| DevTools·CLI | 6 | 1 |
| Infra·Cloud·DevOps | 0 | 0 |
| Data·DB | 0 | 0 |
| Security | 1 | 1 |
| Mobile·Desktop 앱 | 0 | 0 |
| 학습자료 | 1 | 1 |
| 기타 | 1 | 1 |

## 레포별 비교

### #1 JetBrains/thinkrail ⟵ 카테고리 변경

- 원문 설명: Vibe code with pi in a lightweight, real IDE that customises itself around the way you work — The Vibe You Need

| | v1 | v2 |
|---|---|---|
| 카테고리 | DevTools·CLI | LLM·에이전트 |
| 분류 이유 | - | pi 코딩 에이전트를 중심으로 한 IDE이며, 에이전트의 기능과 워크플로우 확장이 핵심 목적이기 때문. (DevTools·CLI도 고려했지만, 에이전트 기능이 제품의 본질) |
| 설명 번역 | 경량의 실제 IDE에서 Pi 코드를 작성하며, 당신의 작업 방식에 맞춰 자동으로 커스터마이징되는 Vibe 개발 경험 | pi를 가볍고 실제 IDE에 담아 당신의 작업 방식에 맞게 커스터마이징하는 에이전트 기반 개발 환경 |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | ThinkRail은 JetBrains의 에이전틱 IDE로, Pi 코딩 에이전트를 중심으로 경량의 실제 IDE 환경을 제공합니다. 프로젝트 스펙을 통해 에이전트가 학습하고, 독립된 워크스페이스에서 병렬 작업을 수행하며 자동으로 개선되는 개발 도구입니다. | ThinkRail은 JetBrains가 만든 에이전트 중심 IDE로, pi 코딩 에이전트를 풍부한 인터페이스로 감싸고 고립된 워크스페이스, 명세 문서 기반 프로젝트 지식, 재사용 가능한 스킬을 제공합니다. 에이전트가 사용자의 작업 방식을 학습해 자신의 능력을 개선하며, 확장 프로그램 지원을 통해 필요한 도구를 직접 만들 수 있습니다. |

### #2 elayadesign/ai-design-skills ⟵ 카테고리 변경

- 원문 설명: (없음)

| | v1 | v2 |
|---|---|---|
| 카테고리 | DevTools·CLI | LLM·에이전트 |
| 분류 이유 | - | Claude Code, Cursor, Codex, Windsurf 등 AI 코딩 도구용 설계 스킬 모음으로, 코딩 에이전트의 기능을 확장하는 것이 핵심 목적이다. |
| 설명 번역 |  |  |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | Claude Code, Cursor, Codex, Windsurf 등 AI 코딩 도구를 위한 마크다운 기반 디자인 스킬 모음입니다. 랜딩페이지 디자인부터 시작해 각 스킬을 필요에 따라 설치하고 사용할 수 있으며, 디자인 시스템(폰트, 색상, 간격, 모션)을 쉽게 커스터마이징할 수 있습니다. | AI 코딩 도구(Claude Code, Cursor, Codex, Windsurf 등)에 설치하는 설계 스킬 모음입니다. 각 스킬은 마크다운 규칙 파일 형태로 제공되며, 현재 랜딩 페이지 설계를 지원합니다. 사용자가 필요한 스킬을 선택해 설치하고 AI에게 자연어로 요청하면 스킬에 정의된 설계 가이드에 따라 작업을 진행합니다. |

### #3 obra/superpowers

- 원문 설명: An agentic skills framework & software development methodology that works.

| | v1 | v2 |
|---|---|---|
| 카테고리 | LLM·에이전트 | LLM·에이전트 |
| 분류 이유 | - | 코딩 에이전트(Claude Code, Cursor, Devin 등)용 플러그인/스킬 모음으로, AI 에이전트가 소프트웨어 개발 작업을 수행하도록 하는 것이 핵심 목적이다. |
| 설명 번역 | 코딩 에이전트를 위한 에이전트 스킬 프레임워크 및 소프트웨어 개발 방법론 | 코딩 에이전트를 위한 에이전트 스킬 프레임워크 및 소프트웨어 개발 방법론 |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | Superpowers는 코딩 에이전트를 위한 완전한 소프트웨어 개발 방법론으로, 재사용 가능한 스킬들을 조합하여 에이전트가 체계적으로 소프트웨어를 개발하도록 지원합니다. Claude Code, Cursor, Devin 등 다양한 AI 코딩 플랫폼에 플러그인으로 설치할 수 있으며, 요구사항 분석부터 구현 계획 수립, 서브에이전트 기반 개발까지의 전체 과정을 자동화합니다. | Superpowers는 코딩 에이전트를 위한 완전한 소프트웨어 개발 방법론으로, 구성 가능한 스킬과 지시사항을 통해 에이전트가 자동으로 사양 도출, 설계 검증, 구현 계획 수립, 서브에이전트 기반 개발을 수행하도록 한다. Claude Code, Cursor, Devin CLI, GitHub Copilot CLI 등 다양한 코딩 에이전트 플랫폼에서 플러그인 형태로 설치할 수 있다. |

### #4 HKUDS/DeepTutor

- 원문 설명: DeepTutor: Lifelong Personalized Tutoring. https://deeptutor.info/ .

| | v1 | v2 |
|---|---|---|
| 카테고리 | LLM·에이전트 | LLM·에이전트 |
| 분류 이유 | - | AI 에이전트 기반의 다중 에이전트 시스템, RAG, 대화형 학습 등이 핵심이며, 개인화된 튜터링을 제공하는 에이전트 앱이 주요 목적이다. |
| 설명 번역 | DeepTutor: 평생 개인맞춤형 튜터링 | DeepTutor: 생애 전반 개인화 튜터링 |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | DeepTutor는 AI 에이전트 기반의 개인맞춤형 평생 튜터링 시스템입니다. 다중 에이전트 아키텍처, RAG 기술, 대화형 학습을 통해 사용자에게 지속적인 학습 지원을 제공하며, CLI 도구와 웹 인터페이스를 모두 지원합니다. | DeepTutor는 생애 전반에 걸쳐 개인화된 튜터링을 제공하는 AI 에이전트 기반 학습 플랫폼입니다. 다중 에이전트 시스템, RAG, 심화 조사(Deep Research) 기능을 결합하여 대화형 학습 경험을 제공하며, CLI 도구와 웹 인터페이스를 통해 접근할 수 있습니다. |

### #5 macro-inc/macro

- 원문 설명: Macro is a unified workspace for teams: email, chat, docs, tasks, agents, calls, and CRM — @-linked together with shared AI memory.

| | v1 | v2 |
|---|---|---|
| 카테고리 | Web·Frontend | Web·Frontend |
| 분류 이유 | - | AI 에이전트 기능이 포함되어 있지만, 레포의 핵심 목적은 팀을 위한 올인원 웹 기반 업무 공간(이메일, 채팅, 문서, 작업, CRM 통합)이며, 에이전트는 이 플랫폼의 여러 기능 중 하나다. |
| 설명 번역 | Macro는 팀을 위한 통합 워크스페이스입니다: 이메일, 채팅, 문서, 작업, 에이전트, 통화, CRM — @링크로 연결되고 공유 AI 메모리를 갖춘 플랫폼입니다. | 팀을 위한 통합 업무 공간: 이메일, 채팅, 문서, 작업, 에이전트, 통화, CRM — @링크와 공유 AI 기억으로 모두 연결된다. |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | Macro는 이메일, 채팅, 문서, 작업, AI 에이전트, 통화, CRM을 하나의 통합 워크스페이스로 제공하는 팀 협업 플랫폼입니다. Rust와 SolidJS로 구축되었으며, 모든 요소가 @링크로 연결되고 공유 AI 메모리를 통해 작동합니다. | Slack, Notion, Linear, HubSpot 같은 도구들을 하나로 통합한 팀 업무 플랫폼이다. 이메일, 메시지, 문서, 작업, CRM, 녹화 통화, 에이전트를 공유 AI 기억과 양방향 그래프로 연결해 모든 정보가 @링크되고 검색 가능하게 한다. |

### #6 Nutlope/hallmark ⟵ 카테고리 변경

- 원문 설명: Anti-AI-slop design skill for Claude Code, Cursor, and Codex.

| | v1 | v2 |
|---|---|---|
| 카테고리 | DevTools·CLI | LLM·에이전트 |
| 분류 이유 | - | Claude Code, Cursor, Codex 등 AI 코딩 에이전트를 위한 디자인 스킬이 핵심 목적이며, 이는 LLM 기반 도구의 기능 확장이므로 LLM·에이전트 카테고리에 해당한다. |
| 설명 번역 | Claude Code, Cursor, Codex를 위한 AI 생성물 같지 않은 디자인 스킬 | Claude Code, Cursor, Codex를 위한 AI 생성 디자인을 거부하는 디자인 스킬 |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | Hallmark은 Claude Code, Cursor, Codex 등 AI 코드 어시스턴트를 위한 디자인 스킬로, AI가 생성한 것처럼 보이지 않는 자연스러운 웹페이지를 만드는 것을 목표로 합니다. 50가지 테마와 자동 검증 시스템을 통해 대비도, 포커스, 모션 감소 등 접근성 기준을 지키면서도 기계적으로 느껴지는 디자인 패턴들을 제거합니다. | Hallmark는 Claude Code, Cursor, Codex 같은 AI 코딩 에이전트가 사용할 수 있는 디자인 스킬로, AI가 생성한 것 같은 어색한 디자인을 피하고 실질적으로 작동하는 웹페이지를 만들도록 돕습니다. 50개의 테마를 제공하며, 대비·포커스·접근성부터 AI 특유의 패턴 제거까지 엄격한 기준으로 디자인을 검수합니다. |

### #7 pbakaus/impeccable ⟵ 카테고리 변경

- 원문 설명: The design vocabulary for your coding agent. Steer with polish and bolder, review with critique and audit, catch AI slop before it ships.

| | v1 | v2 |
|---|---|---|
| 카테고리 | DevTools·CLI | LLM·에이전트 |
| 분류 이유 | - | Claude Code, Cursor, Codex, GitHub Copilot 등 코딩 에이전트용 설계 스킬·명령어 모음이 핵심 기능이므로 LLM·에이전트 분류 |
| 설명 번역 | 코딩 에이전트를 위한 디자인 어휘입니다. 폴란드와 볼더로 조작하고, 크리티크와 오딧으로 검토하며, AI 품질 문제를 출시 전에 포착하세요. | 코딩 에이전트를 위한 설계 어휘 모음. polish와 bolder로 방향을 조종하고, critique과 audit으로 검토하며, AI 쓸데없는 코드가 배포되기 전에 잡아냅니다. |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | AI 코딩 에이전트를 위한 디자인 어휘 및 품질 관리 도구입니다. 폴란드/볼더 명령으로 디자인을 조작하고, 크리티크/오딧 명령으로 검토하며, 결정론적 규칙 62개로 AI 생성 디자인의 문제를 사전에 감지합니다. | 코딩 에이전트용 디자인 지휘 도구로, `polish`, `bolder`, `critique`, `audit` 등 24개 명령으로 AI가 생성한 UI를 더 나은 설계로 개선하고 질문제 UI 패턴을 자동 감지합니다. 슬로프(AI 쓸데없는 코드)를 배포 전에 잡아내는 62개 결정론적 규칙을 포함합니다. |

### #8 makecindy/cindy

- 원문 설명: Consider it done. The open-source AI agent that works out of the box · 想到，就能做到。开源、开箱即用的 AI Agent。

| | v1 | v2 |
|---|---|---|
| 카테고리 | LLM·에이전트 | LLM·에이전트 |
| 분류 이유 | - | AI 에이전트 프레임워크이자 Claude Code, Codex 등 여러 에이전트를 통합하는 데스크톱·모바일 앱으로, AI 에이전트 기능이 핵심 목적이므로 LLM·에이전트 카테고리가 최우선이다. |
| 설명 번역 | 생각하면 된다. 개발 후 바로 사용 가능한 오픈소스 AI 에이전트 · 想到，就能做到。开源、开箱即用的 AI Agent。 | 설치 후 바로 쓸 수 있는 오픈소스 AI 에이전트. 당신의 컴퓨터에서 실제 업무를 처리한다. |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | Cindy는 즉시 사용 가능한 오픈소스 AI 에이전트로, 여러 기기(데스크톱, 노트북, 휴대폰)에서 작업을 연속적으로 진행할 수 있습니다. Claude Code, Codex 등 다양한 모델 제공자를 지원하며 자신의 컴퓨터를 서버로 사용하는 방식으로 작동합니다. | Cindy는 컴퓨터와 휴대폰을 연결해 여러 기기에서 일을 계속할 수 있는 오픈소스 AI 에이전트다. Claude Code, Codex 같은 기존 에이전트와 자체 에이전트 Pi를 지원하며, 실제 파일·앱·브라우저와 상호작용하고 자동화·플러그인을 통해 확장할 수 있다. |

### #9 nightly-labs/openbot

- 원문 설명: A local-first desktop workspace for persistent AI teammates. Run Codex, Claude, and Grok with dedicated workspaces, task queues, file sharing, browser control, and agent-to-agent collaboration.

| | v1 | v2 |
|---|---|---|
| 카테고리 | LLM·에이전트 | LLM·에이전트 |
| 분류 이유 | - | AI 에이전트(Codex, Claude, Grok 등)를 중심으로 데스크톱 워크스페이스를 제공하는 것이 핵심 목적이며, 에이전트 간 협업과 작업 관리가 주요 기능이다. |
| 설명 번역 | 여러 AI 팀원을 위한 로컬 우선 데스크톱 워크스페이스입니다. Codex, Claude, Grok을 전용 워크스페이스, 작업 큐, 파일 공유, 브라우저 제어, 에이전트 간 협업 기능과 함께 실행할 수 있습니다. | 여러 AI 팀원을 위한 로컬 우선 데스크톱 워크스페이스. Codex, Claude, Grok을 전용 워크스페이스, 작업 큐, 파일 공유, 브라우저 제어, 에이전트 간 협업 기능과 함께 실행할 수 있다. |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | OpenBot은 로컬에서 실행되는 데스크톱 워크스페이스로, Codex, Claude, Grok 등 여러 AI 모델을 독립적인 워크스페이스와 대화 이력으로 관리할 수 있습니다. 작업 큐, 파일 공유, 브라우저 제어, 에이전트 간 협업 등의 기능을 제공하는 로컬 우선 AI 팀원 관리 플랫폼입니다. | OpenBot은 Codex, Claude, Grok 등 여러 AI 에이전트를 로컬 데스크톱에서 관리할 수 있는 워크스페이스다. 각 에이전트마다 독립적인 작업 공간, 메시지 큐, 파일 공유, 브라우저 제어, 에이전트 간 협업 기능을 제공한다. |

### #10 togg53192-cmd/jailbreaks

- 원문 설명: LIST OF ALL MY JAILBREAKS

| | v1 | v2 |
|---|---|---|
| 카테고리 | Security | Security |
| 분류 이유 | - | LLM 탈옥 프롬프트와 명령어 주입 우회 기법을 다루는 레포로, 보안(탈옥·레드팀)에 분류된다. LLM·에이전트 범주도 적용 가능하나, 레포의 핵심 목적이 LLM 시스템을 우회하고 정책을 무시하도록 하는 기법 모음이므로 보안 분류가 더 정확하다. |
| 설명 번역 | 내 모든 탈옥 프롬프트의 목록 | 내가 만든 모든 탈옥 목록 |
| confidence | high  | medium README에서 '탈옥' 기법 모음임이 명확하나, OpenCode Zen(Big Pickle, Space Bunny 등) 같은 특정 모델·서비스의 정체가 명확하지 않아 각 프롬프트의 정확한 용도 파악에 불확실성이 있다. |
| 형식 보정 | - | - |
| 요약 | 이 저장소는 Claude, Gemini, Grok, DeepSeek, Qwen 등 다양한 AI 모델들에 대한 시스템 프롬프트, 페르소나 정의, 작업공간 정책 등 32개의 '탈옥(jailbreak)' 프롬프트를 수집한 컬렉션입니다. AI 시스템이 명령 조작과 프롬프트 인젝션에 얼마나 취약한지를 연구 및 교육 목적으로 문서화하고 있습니다. | Claude, Gemini, DeepSeek, Grok 등 주요 LLM 모델과 오픈 가중치 모델을 대상으로 한 32개의 탈옥 프롬프트 모음이다. 시스템 프롬프트 우회, 페르소나 잠금 해제, 명령어 계층 충돌 등 다양한 기법을 수집하고 있으며, 각 프롬프트는 바로 사용할 수 있는 완전한 형태로 제공된다. |

### #11 hmjz100/LinkSwift

- 원문 설명: 一个基于 JavaScript 的网盘文件下载地址获取工具。基于【网盘直链下载助手】修改 ，支持 百度网盘 / 阿里云盘 / 中国移动云盘 / 天翼云盘 / 迅雷云盘 / 夸克网盘 / UC网盘 / 123云盘 八大网盘

| | v1 | v2 |
|---|---|---|
| 카테고리 | DevTools·CLI | DevTools·CLI |
| 분류 이유 | - | 브라우저 확장 기반 사용자 스크립트로, 여러 클라우드 스토리지 서비스에서 직접 다운로드 링크를 추출하는 개발자·파워 사용자용 도구다. |
| 설명 번역 | JavaScript 기반의 클라우드 스토리지 파일 다운로드 주소 획득 도구입니다. 바이두 클라우드, 알리바바 클라우드, 중국 이동 클라우드, 텐센트 클라우드, 썬더 클라우드, 광야 클라우드, 쿼크 클라우드, UC 클라우드, 123 클라우드 등 9개의 주요 클라우드 스토리지 서비스를 지원합니다. | JavaScript 기반 네트 스토리지 파일 다운로드 주소 획득 도구. 원본 '네트 스토리지 직링크 다운로드 조수'를 수정해 바이두 네트디스크, 알리바바 클라우드 드라이브, 중국이동클라우드, 천익 클라우드, 썬더 클라우드, 쿼크 네트디스크, UC 네트디스크, 123 클라우드 9개 네트 스토리지를 지원한다. |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | 8개의 주요 클라우드 스토리지 서비스(바이두 클라우드, 알리바바 클라우드, 텐센트 클라우드 등)에서 다운로드 링크를 추출하는 JavaScript 기반 도구입니다. 브라우저 확장 프로그램으로 설치되어 직링크 획득, UI 개선, 다양한 다운로더 지원 등의 기능을 제공합니다. | LinkSwift는 Tampermonkey 사용자 스크립트로, 바이두 네트디스크, 알리바바 클라우드 드라이브, 중국이동클라우드, 천익 클라우드, 썬더 클라우드, 광야 클라우드, 쿼크 네트디스크, UC 네트디스크, 123 클라우드 등 9개 주요 중국 클라우드 스토리지 서비스에서 직접 다운로드 링크를 획득할 수 있게 해준다. 공식 API를 기반으로 하며 Aria2, Motrix 같은 외부 다운로더와 통합을 지원한다. |

### #12 expo/skills ⟵ 카테고리 변경

- 원문 설명: A collection of AI agent skills for working with Expo projects and Expo Application Services

| | v1 | v2 |
|---|---|---|
| 카테고리 | DevTools·CLI | LLM·에이전트 |
| 분류 이유 | - | Claude Code, Cursor, Codex 등 AI 코딩 에이전트용 skills 모음이 핵심이므로. DevTools·CLI도 고려했으나, AI 에이전트 기능이 레포의 핵심 목적이므로 LLM·에이전트 우선. |
| 설명 번역 | Expo 프로젝트 및 Expo Application Services와 함께 작동하는 AI 에이전트 스킬 모음 | Expo 프로젝트 및 Expo Application Services 작업용 AI 에이전트 skills 모음 |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | Expo 프로젝트 개발을 위한 AI 에이전트 스킬 모음입니다. Claude, Cursor, GitHub Copilot 등 다양한 AI 코딩 에이전트에 플러그인 또는 CLI로 설치하여 Expo 앱 빌드, 배포, 업그레이드, 디버깅을 AI 도움으로 수행할 수 있게 해줍니다. | Expo 프로젝트 작업을 위한 AI 에이전트용 skills 모음으로, Claude Code, Cursor, Codex 등 다양한 코딩 에이전트에 설치할 수 있습니다. Expo Router, EAS 빌드, 배포, 업그레이드 등 Expo 작업의 맥락을 AI 에이전트에 제공해 더 정확한 지원을 받을 수 있게 합니다. |

### #13 ruvnet/RuView

- 원문 설명: π RuView turns commodity WiFi signals into real-time spatial intelligence, vital sign monitoring, and presence detection — all without a single pixel of video.

| | v1 | v2 |
|---|---|---|
| 카테고리 | 기타 | 기타 |
| 분류 이유 | - | WiFi 센서 신호 처리와 IoT 홈 자동화가 핵심이지만, 컴퓨터비전(DensePose 기반 자세 추정), 신호 처리, 기계학습 모델, 스마트홈 통합, 펌웨어 개발이 모두 포함되어 단일 카테고리로 분류하기 어렵다. 하드웨어(ESP32) 기반 IoT 플랫폼으로서 '기타'가 가장 적절하다. |
| 설명 번역 | 상용 WiFi 신호를 실시간 공간 지능, 생체신호 모니터링, 사람 감지로 변환합니다 — 영상 없이 모든 것이 가능합니다. | 일반적인WiFi 신호를 실시간 공간 인식, 생체신호 모니터링, 사람 감지로 변환합니다. 비디오 화면 없이 모든 것을 처리합니다. |
| confidence | high  | medium README 내용이 충분하고 기능이 명확하지만, 레포가 IoT·임베디드 하드웨어, 기계학습 모델, 스마트홈 자동화, RF 신호 처리 등 여러 기술 분야를 아우르고 있어 단일 카테고리 분류가 명확하지 않습니다. |
| 형식 보정 | 목록에 없는 카테고리 'IoT' → '기타'로 보정 | - |
| 요약 | RuView는 WiFi 신호를 실시간 공간 감지, 생체신호 모니터링, 사람 감지에 활용하는 오픈소스 플랫폼입니다. ESP32 센서와 채널 상태 정보(CSI)를 통해 카메라나 웨어러블 장치 없이 벽을 뚫고 사람의 존재, 호흡·심박수, 활동 패턴을 감지할 수 있습니다. | RuView는 일반적인 WiFi 라우터에서 송출되는 무선 신호를 포착하여 실시간 공간 인식, 호흡·심박수 모니터링, 사람 감지를 구현하는 오픈소스 WiFi 센싱 플랫폼입니다. 카메라나 웨어러블 기기 없이 벽을 통과해 사람의 위치, 활동, 생체신호를 감지할 수 있으며, Home Assistant, Apple Home, Google Home, Alexa 등 주요 스마트홈 생태계와 기본 통합됩니다. |

### #14 xiaolai/the-craft-of-selfteaching

- 원문 설명: One has no future if one couldn't teach themself.

| | v1 | v2 |
|---|---|---|
| 카테고리 | 학습자료 | 학습자료 |
| 분류 이유 | - | Python 프로그래밍을 통해 독학 능력을 기르는 방법을 체계적으로 설명하는 교육 도서다. Jupyter Notebook 형식의 대규모 튜토리얼·강의 자료로, 코딩 학습과 별도로 자학 방법론 자체가 주제다. |
| 설명 번역 | 자학 능력이 없으면 미래가 없다 | 자신을 스스로 가르칠 수 없는 사람에게는 미래가 없다. |
| confidence | high  | high  |
| 형식 보정 | - | - |
| 요약 | 리 샤오라이(李笑来)가 저술한 자학(自学)의 방법론을 다루는 온라인 교재입니다. Python 프로그래밍을 자학의 입구로 삼아, 기초 문법부터 고급 개념까지 단계적으로 학습하고 실습하는 과정을 Jupyter Notebook으로 구성했습니다. | 저명한 작가 Li Xiaolai가 저술한 '자학은 기술이다(独学是门手艺)'는 Python을 입문으로 삼아 효과적인 독학 방법을 배우는 종합 교과서다. 기초 문법부터 고급 프로그래밍 개념, 그리고 집중력 관리·사고력 강화 같은 학습 방법론까지 43개 강의로 구성되어 있으며, Jupyter Notebook 형식으로 대화형 학습을 지원한다. |
