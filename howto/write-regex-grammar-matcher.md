---
created: 2026-03-19
description: 영어 문법 규칙을 정규식으로 정의하고 텍스트에서 자동 매칭하는 접근법
---

# 정규식 기반 문법 패턴 매칭

영어 문법 교재(Grammar in Use)의 규칙을 정규식으로 변환하여, 텍스트에서 해당 문법이 사용된 문장을 자동으로 찾는 방법.

## The Insight

완벽한 자연어 파싱 없이도, **문법 규칙의 표면적 패턴**을 정규식으로 잡아내면 실용적인 수준의 문법 분석이 가능하다. "be going to + 동사"처럼 고정된 구조를 가진 문법은 정규식으로 높은 정확도를 얻을 수 있다. 반면 문맥 의존적 문법(예: would의 습관 vs 가정법)은 오탐이 생기지만, 학습 보조 도구로서는 충분하다.

## Why This Matters

- NLP 라이브러리 없이 순수 Python + regex로 문법 분석 가능
- 27개 문법 유닛 × 137개 영상 = 대량 분석을 즉시 실행
- 학습자에게 "이 영상에서 이 문법이 쓰인 실제 문장"을 보여줄 수 있다

## Recognition Pattern

- 텍스트에서 특정 문법 패턴을 자동으로 찾아야 할 때
- 문법 교재의 규칙을 코드로 구현해야 할 때
- NLP 의존성 없이 가볍게 처리하고 싶을 때

## The Approach

1. 문법 규칙을 **표면 패턴**으로 분해한다
2. 각 패턴을 정규식으로 변환한다
3. 문장 단위로 매칭하여 유닛별로 그룹화한다

### Step 1: 문법 규칙을 패턴으로 분해

예시 - Unit 20: be going to

```
규칙: "be going to + 동사원형"
패턴들:
  - I'm going to + verb
  - He's going to + verb
  - not going to + verb
```

### Step 2: 정규식으로 변환

```python
{
    "unit": 20,
    "title": "be going to (do)",
    "desc": "계획된 의도 또는 근거 있는 예측",
    "patterns": [
        r"\b(i'm|you're|he's|she's|it's|we're|they're|is|are|am)\s+going\s+to\s+\w+",
        r"\bnot\s+going\s+to\s+\w+",
    ]
}
```

**핵심 기법:**
- `\b` — 단어 경계 (부분 매칭 방지)
- `\w+` — 동사 자리 (아무 단어)
- `\s+` — 공백 허용
- `re.IGNORECASE` — 대소문자 무시

### Step 3: 문장 단위 매칭

```python
import re

def analyze_script(sentences, rules):
    results = []
    for rule in rules:
        matched = []
        for sent in sentences:
            for pat in rule["patterns"]:
                if re.search(pat, sent, re.IGNORECASE):
                    matched.append(sent)
                    break  # 한 문장에 여러 패턴 매칭 방지
        if matched:
            results.append({
                "unit": rule["unit"],
                "title": rule["title"],
                "examples": matched[:5],  # 최대 5개
            })
    return results
```

## 패턴 설계 팁

### 잘 잡히는 문법 (고정 구조)

| 문법 | 패턴 | 정확도 |
|------|------|--------|
| be going to | `going\s+to\s+\w+` | 높음 |
| will/won't | `\bwill\s+\w+`, `\bwon't\s+\w+` | 높음 |
| have to | `\bhave\s+to\s+\w+` | 높음 |
| should have done | `\bshould\s+have\s+\w+(ed\|en\|t)` | 높음 |
| 수동태 | `\b(is\|was)\s+(made\|done\|called\|known)` | 중간 |

### 오탐이 생기는 문법 (문맥 의존)

| 문법 | 문제 | 대응 |
|------|------|------|
| would (습관 vs 가정) | 구분 불가 | 둘 다 표시, 사용자가 판단 |
| can (능력 vs 허락) | 구분 불가 | Unit 26으로 통합 |
| may (가능성 vs 허락) | 구분 불가 | Unit 29로 통합 |

### 과거분사 매칭

영어 과거분사는 불규칙하므로 `\w+(ed|en|t)`로 대부분을 커버한다:
- `-ed`: played, worked, used
- `-en`: taken, given, broken
- `-t`: built, sent, kept

```python
r"\bshould\s+have\s+\w+(ed|en|t)\b"
```

## Example

실행:

```bash
python tools/analyze_grammar.py
# → data/grammar/{video_id}.json 생성
```

출력 예시:

```json
[
  {
    "unit": 20,
    "title": "be going to (do)",
    "desc": "계획된 의도 또는 근거 있는 예측",
    "examples": ["I'm going to find a spot to sit and rest."]
  }
]
```

## 체크리스트

- [ ] `\b` 단어 경계를 빼먹지 않았나 (부분 매칭 방지)
- [ ] `re.IGNORECASE` 적용했나
- [ ] 축약형 처리했나 (I'm, won't, shouldn't 등)
- [ ] 한 문장당 한 번만 매칭하는가 (break 확인)
- [ ] examples 개수 제한했나 (너무 많으면 페이지가 길어짐)

## 관련 문서

- `page-generation.md` - 전체 페이지 생성 가이드
