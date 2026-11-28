import json

import pytest
import requests

from trending import config, consistency, llm


class _Resp:
    status_code = 200

    def json(self):
        return {"content": [{"type": "text", "text": "{}"}], "stop_reason": "end_turn"}


@pytest.mark.parametrize("value, sent", [("0", 0.0), ("0.3", 0.3), ("", None)])
def test_temperature_sent_to_claude(monkeypatch, value, sent):
    seen = {}
    monkeypatch.setattr(config, "LLM_TEMPERATURE", value)
    monkeypatch.setattr(config, "LLM_API_KEY", "k")
    monkeypatch.setattr(config, "LLM_MODEL", "claude-haiku-4-5")
    monkeypatch.setattr(config, "LLM_BASE_URL", "https://x/api/v2/chat/direct/anthropic")
    monkeypatch.setattr(requests, "post", lambda url, **kw: seen.update(kw["json"]) or _Resp())
    llm.Analyzer().complete("s", "p")
    assert seen.get("temperature") == sent          # "0"도 빠뜨리지 않고 보냄
    assert config.temperature() == sent


def test_consistency_splits_by_setting(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "TRENDING_DIR", tmp_path / "t")
    monkeypatch.setattr(config, "INTEREST_DIR", tmp_path / "i")
    (tmp_path / "t").mkdir()

    def day(d, temp, ko, backfilled=False):
        ai = {"category": "기타", "description_ko": ko}
        if backfilled:
            ai["backfilled_at"] = "x"
        data = {"temperature": temp, "repos": [{"full_name": "a/x", "description": "same", "ai": ai}]}
        (tmp_path / "t" / f"{d}.json").write_text(json.dumps(data), encoding="utf-8")

    day("2026-11-01", None, "가")
    day("2026-11-02", None, "나")
    day("2026-11-03", None, "다", backfilled=True)   # 다시 채운 건 제외
    day("2026-11-29", 0, "가")
    day("2026-11-30", 0, "가")
    rows = {r["setting"]: r for r in consistency.summarize("trending", consistency.collect("trending"))}
    assert rows["기본값(미지정)"]["translation_same"] == 0
    assert rows["temperature 0"]["translation_same"] == 1
