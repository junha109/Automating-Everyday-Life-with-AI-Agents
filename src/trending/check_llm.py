"""LLM 연결 확인: 요청 1번으로 키·주소·모델이 맞는지 확인한다. (크레딧은 아주 조금 씀)

    uv run python -m trending.check_llm

API 키·주소를 바꾼 뒤 전체 수집을 돌리기 전에 실행한다. 성공하면 0, 실패하면 1로 끝난다.
"""
from __future__ import annotations

import sys
import time

from . import config
from .llm import Analyzer, _extract_json


def _warnings(base_url: str, model: str, provider: str) -> list[str]:
    w = []
    if "/bridge/openai" in base_url:
        w.append("LLM_BASE_URL이 종료된 옛 주소(.../chat/bridge/openai)입니다. 410 오류가 납니다.")
    if "/" in model:
        w.append(f"모델 이름 '{model}'에 접두사가 있습니다. 새 API는 'claude-haiku-4-5'처럼 접두사 없이 씁니다.")
    if provider == "openai" and model.lower().startswith("claude"):
        w.append("Claude 모델은 OpenAI 주소로 호출할 수 없습니다. "
                 "LLM_BASE_URL을 .../chat/direct/anthropic 으로 바꾸세요.")
    if provider == "anthropic" and not model.lower().split("/")[-1].startswith("claude"):
        w.append("Claude 주소(/anthropic)인데 모델이 Claude가 아닙니다.")
    if provider == "anthropic" and base_url.rstrip("/").endswith("/v1"):
        w.append("Claude 주소 끝에 /v1을 붙이지 않습니다 (코드가 /v1/messages를 붙임).")
    return w


def main() -> int:
    key = config.LLM_API_KEY
    analyzer = Analyzer()
    print(f"호출 방식 : {analyzer.provider}")
    print(f"주소      : {config.LLM_BASE_URL or '(비어 있음)'}")
    print(f"모델      : {config.LLM_MODEL or '(비어 있음)'}")
    t = config.temperature()
    print(f"temperature: {t if t is not None else '보내지 않음 (모델 기본값)'}")
    print(f"키        : {(key[:8] + '…(' + str(len(key)) + '자)') if key else '(비어 있음)'}")
    for w in _warnings(config.LLM_BASE_URL, config.LLM_MODEL, analyzer.provider):
        print(f"[주의] {w}")
    if analyzer.mock:
        print("실패: LLM_API_KEY 또는 LLM_MODEL이 비어 있습니다.")
        return 1

    t0 = time.time()
    try:
        text = analyzer.complete(
            "JSON 객체 하나만 출력한다.",
            '다음 JSON을 그대로 출력해라: {"ok": true, "ko": "연결 성공"}',
        )
    except Exception as e:
        print(f"실패: {e}")
        return 1
    print(f"응답 ({time.time() - t0:.1f}초): {text.strip()[:200]}")
    try:
        _extract_json(text)
    except Exception:
        print("주의: 연결은 됐지만 응답을 JSON으로 읽지 못했습니다.")
        return 1
    print("성공: 키·주소·모델 모두 정상입니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
