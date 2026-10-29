"""'근거 부족' 경고 배지 판정.

AI 자기평가(confidence)만 믿지 않고, 코드로 확인 가능한 조건을 함께 본다.
→ 보고서에서 "AI가 틀리기 쉬운 조건"을 미리 표시한 근거가 된다.
"""
from __future__ import annotations

import re

_BADGE = re.compile(r"!\[[^\]]*\]\([^)]*\)|<img[^>]*>|<[^>]+>")
_HAN = re.compile(r"[一-鿿]")          # 한자 (중국어 README 판별)
_KANA = re.compile(r"[぀-ヿ]")         # 일본어
_CYR = re.compile(r"[Ѐ-ӿ]")          # 러시아어 등
_HANGUL = re.compile(r"[가-힣]")


def clean_readme(readme: str) -> str:
    """배지 이미지·HTML 태그를 지운 본문 (길이 판정과 '원문 보기'용)."""
    text = _BADGE.sub(" ", readme or "")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


_CJK = re.compile(r"[一-鿿぀-ヿ가-힣]")


def _inline(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)                 # 이미지
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)              # [글자](주소) → 글자
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)             # [글자][참조]
    text = re.sub(r"\[([^\]]*)\]\([^)]*$", r"\1", text)               # 잘린 링크
    text = re.sub(r"<[^>]+>", " ", text)                              # HTML 태그
    text = re.sub(r"(\*\*|__|\*|`)", "", text)                         # 강조·코드 표시
    return re.sub(r"\s+", " ", text).strip()


def readable_excerpt(readme: str, limit: int = 800) -> str:
    """README를 사람이 읽기 좋은 평문 앞부분으로 만든다 ('원문 보기'용).

    마크다운·HTML 표시, 코드 블록, 표, 메뉴처럼 짧은 줄(배지·내비게이션)을 걸러내고
    문단 단위로 자른다. 제목 줄은 앞에 '# '를 붙여 표시한다.
    """
    text = re.sub(r"<!--.*?-->", "", readme or "", flags=re.S)
    text = re.sub(r"```.*?```", "\n", text, flags=re.S)                # 코드 블록 제거
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.S | re.I)
    blocks: list[str] = []
    para: list[str] = []

    def flush():
        if para:
            blocks.append(" ".join(para))
            para.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        m = re.match(r"^#{1,6}\s*(.*?)\s*#*$", line)
        if m:
            flush()
            title = _inline(m.group(1))
            if title:
                blocks.append("# " + title)
            continue
        if line.startswith("|") or re.fullmatch(r"[-=*_\s|:]+", line):   # 표, 구분선
            continue
        bullet = re.match(r"^([-*+]|\d+[.)])\s+", line)
        body = _inline(line[bullet.end():] if bullet else line)
        if not body:
            continue
        # 메뉴·배지 같은 짧은 줄은 버린다 (한중일 문자는 글자 수, 그 외는 단어 수로 판단)
        cjk = len(_CJK.findall(body))
        if (cjk and cjk < 12) or (not cjk and len(body.split()) < 4):
            continue
        if bullet:
            flush()
            blocks.append("• " + body)
        else:
            para.append(body)
    flush()

    out, size = [], 0
    for b in blocks:
        if size + len(b) > limit:
            if not out:
                out.append(b[:limit].rstrip() + "…")
            break
        out.append(b)
        size += len(b) + 2
    # 제목만 남고 끝나면 의미가 없으므로 뒤쪽 제목은 제거
    while out and out[-1].startswith("# "):
        out.pop()
    return "\n\n".join(out)


def readme_language_hint(text: str) -> str | None:
    letters = max(len(re.findall(r"\w", text)), 1)
    if len(_HANGUL.findall(text)) / letters > 0.2:
        return None  # 한국어는 경고하지 않음
    for name, pat in (("중국어", _HAN), ("일본어", _KANA), ("키릴 문자", _CYR)):
        if len(pat.findall(text)) / letters > 0.15:
            return name
    return None


def warnings_for(repo: dict, readme: str, ai: dict) -> list[str]:
    body = clean_readme(readme)
    w = []
    if not body:
        w.append("README 없음")
    elif len(body) < 300:
        w.append("README가 매우 짧음")
    if not (repo.get("description") or "").strip():
        w.append("레포 설명 없음")
    lang = readme_language_hint(body)
    if lang:
        w.append(f"README가 {lang} 위주")
    if ai.get("confidence") == "low":
        w.append("AI 확신 낮음" + (f": {ai['confidence_reason']}" if ai.get("confidence_reason") else ""))
    if ai.get("llm_issues"):
        w.append("AI 출력 형식 보정됨")
    return w
