# 페이지 생성 가이드

## 전체 흐름

```
1. crawl.py          YouTube 영상 메타데이터 수집
2. fetch_scripts.py  영상별 자막(스크립트) 다운로드
3. analyze_grammar.py 스크립트에서 문법 패턴 분석
4. generate_html.py  CSV + JSON → HTML 페이지 생성
5. git push          GitHub Actions → Pages 배포
```

## 1단계: 영상 목록 수집 (`tools/crawl.py`)

```bash
python tools/crawl.py
```

- `yt-dlp`를 사용하여 `@influenglish` 채널의 전체 영상 메타데이터를 한 번에 수집
- 출력: `data/youtube_videos.csv`
- 수집 항목: title, url, upload_date, duration, view_count, channel

### 의존성
```bash
pip install yt-dlp
```

## 2단계: 자막 수집 (`tools/fetch_scripts.py`)

```bash
python tools/fetch_scripts.py
```

- `youtube-transcript-api`로 각 영상의 영어 자막을 다운로드
- 영어 자막이 없으면 한국어 자막을 시도
- 이미 다운로드된 파일은 건너뜀 (캐시)
- 출력: `data/scripts/{video_id}.json`
- YouTube IP 차단 시 시간을 두고 재실행

### 의존성
```bash
pip install youtube-transcript-api
```

### JSON 포맷
```json
[
  {"start": 2.9, "text": "It's scorching hot."},
  {"start": 5.6, "text": "I'm a wimp."}
]
```

## 3단계: 문법 분석 (`tools/analyze_grammar.py`)

```bash
python tools/analyze_grammar.py
```

- `data/scripts/` 의 자막을 문장 단위로 합침
- Grammar in Use Units 20~46의 문법 패턴(정규식)과 매칭
- 출력: `data/grammar/{video_id}.json`

### 분석 대상 문법 (27개 유닛)

| 유닛 | 문법 | 패턴 예시 |
|------|------|-----------|
| 20 | be going to | `I'm going to + 동사` |
| 21-22 | will / won't | `I'll + 동사`, `won't + 동사` |
| 24 | will be doing / will have done | 미래진행/완료 |
| 25 | When I do (시간절) | `when/before/after + 현재시제` |
| 26 | can / could / be able to | 능력/가능성 |
| 27 | could have done | 과거 가능성 |
| 28 | must / can't (추론) | `must be`, `can't be` |
| 29-30 | may / might | 현재/과거 가능성 |
| 31-32 | have to / must / needn't | 의무/금지/불필요 |
| 33-34 | should / should have | 조언/후회 |
| 35 | had better / it's time | 강한 조언 |
| 36 | would | 과거 습관, 가정법 |
| 37 | Can/Could/Would you? | 요청/허락 |
| 38-40 | If 조건문 | 1형/2형/3형 조건문 |
| 39, 41 | I wish | 소망/후회 |
| 42-45 | Passive | 수동태 |
| 46 | have something done | 사역 수동 |

### JSON 포맷
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

## 4단계: HTML 생성 (`tools/generate_html.py`)

```bash
python tools/generate_html.py
```

### 읽는 파일
- `data/youtube_videos.csv` → 영상 목록
- `data/scripts/{video_id}.json` → 자막
- `data/grammar/{video_id}.json` → 문법 분석

### 생성하는 파일

#### `docs/index.html` (목록 페이지)
- 전체 영상 테이블 (썸네일, 제목, 날짜, 길이, 조회수)
- 각 영상에 뱃지 링크:
  - **YouTube** (빨강) → YouTube 영상
  - **상세** (파랑) → 상세 페이지
  - **Script** (초록) → 상세 페이지 스크립트 섹션
  - **Grammar** (보라) → 상세 페이지 문법 섹션

#### `docs/pages/{video_id}.html` (상세 페이지)
- YouTube 임베드 플레이어
- **Script**: 자막을 문장 단위로 합쳐서 읽기 쉬운 문단 형태로 표시
- **Grammar Notes**: 매칭된 문법 유닛별로 규칙 설명 + 예문

### 자막 → 문장 합치기 로직
- 자막 snippet을 순서대로 연결
- `.`, `!`, `?`, `...`, `"` 로 끝나면 한 문장으로 분리
- 남은 텍스트는 마지막 문장으로 추가

## 5단계: 배포

```bash
git add -A && git commit -m "Update pages" && git push
```

- `.github/workflows/deploy.yml`이 자동 실행
- GitHub Actions가 `tools/generate_html.py`를 실행하여 `docs/` 재생성
- `docs/` 디렉토리가 GitHub Pages에 배포됨

### Pages 설정 (최초 1회)
GitHub 저장소 → Settings → Pages → Source → **GitHub Actions**

## 데이터 흐름 요약

```
YouTube API
    │
    ▼
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ crawl.py    │────▶│ youtube_videos   │     │                  │
│             │     │ .csv             │────▶│ generate_html.py │
└─────────────┘     └──────────────────┘     │                  │
                                              │   ┌─ index.html │
┌─────────────┐     ┌──────────────────┐     │   │              │
│ fetch_      │────▶│ scripts/         │────▶│   └─ pages/      │
│ scripts.py  │     │ {id}.json        │     │      {id}.html   │
└─────────────┘     └──────────────────┘     └──────────────────┘
                                                      ▲
┌─────────────┐     ┌──────────────────┐              │
│ analyze_    │────▶│ grammar/         │──────────────┘
│ grammar.py  │     │ {id}.json        │
└─────────────┘     └──────────────────┘
```

## 새 영상 추가 시

```bash
python tools/crawl.py              # 영상 목록 갱신
python tools/fetch_scripts.py      # 새 영상 자막만 추가 (캐시)
python tools/analyze_grammar.py    # 문법 분석
python tools/generate_html.py      # HTML 재생성
git add -A && git commit -m "Update" && git push
```
