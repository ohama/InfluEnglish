# CLAUDE.md

## 프로젝트 개요

YouTube 채널 [@influenglish](https://www.youtube.com/@influenglish) (캘리쌤 브이로그 영어)의 영상을 수집하고, 영어 스크립트 · 어휘 · 문법 분석을 제공하는 정적 웹사이트.

**배포 URL:** https://ohama.github.io/InfluEnglish/

## 프로젝트 구조

```
InfluEnglish/
├── tools/                      # 데이터 수집 및 빌드 스크립트
│   ├── crawl.py                # YouTube 영상 메타데이터 수집
│   ├── fetch_scripts.py        # 영어 자막(스크립트) 다운로드
│   ├── analyze_grammar.py      # 문법 패턴 분석 (Units 20-46)
│   ├── analyze_vocab.py        # 어려운 어휘 분석
│   └── generate_html.py        # HTML 페이지 생성
├── data/                       # 수집된 데이터
│   ├── youtube_videos.csv      # 영상 목록
│   ├── scripts/                # 영상별 자막 JSON
│   ├── grammar/                # 영상별 문법 분석 JSON
│   └── vocab/                  # 영상별 어휘 분석 JSON
├── docs/                       # GitHub Pages 배포 (자동 생성)
│   ├── index.html              # 전체 목록 페이지
│   └── pages/                  # 영상별 상세 페이지
├── howto/                      # 운영 가이드 문서
├── .github/workflows/
│   └── deploy.yml              # GitHub Actions 배포
└── README.md
```

## 전체 빌드 파이프라인

새 영상이 추가되었거나 전체 갱신이 필요할 때, 프로젝트 루트에서 순서대로 실행:

```bash
# 1. 영상 목록 수집 (yt-dlp 필요)
python tools/crawl.py

# 2. 자막 다운로드 (youtube-transcript-api 필요, 캐시됨)
python tools/fetch_scripts.py

# 3. 문법 분석
python tools/analyze_grammar.py

# 4. 어휘 분석
python tools/analyze_vocab.py

# 5. HTML 생성
python tools/generate_html.py
```

## 각 도구 설명

### `tools/crawl.py`
- `yt-dlp --dump-json`으로 채널 전체 영상 메타데이터를 한 번에 수집
- 출력: `data/youtube_videos.csv` (title, url, upload_date, duration, view_count, channel)
- 의존성: `pip install yt-dlp`

### `tools/fetch_scripts.py`
- `youtube-transcript-api`로 영어 자막 다운로드 (없으면 한국어 시도)
- 이미 있는 파일은 건너뜀 (캐시)
- YouTube IP 차단 시 시간을 두고 재실행
- 출력: `data/scripts/{video_id}.json`
- 의존성: `pip install youtube-transcript-api`

### `tools/analyze_grammar.py`
- Grammar in Use Units 20~46 (27개 유닛) 의 문법 패턴을 정규식으로 매칭
- 대상: be going to, will/won't, can/could, must/have to, should, would, may/might, 조건문, wish, 수동태 등
- 출력: `data/grammar/{video_id}.json`

### `tools/analyze_vocab.py`
- 기본 단어(~600개)를 제외하고 중급 이상 어휘를 찾음
- 내장 사전(VOCAB_DB)에서 한국어 뜻과 예문 3개를 제공
- 스크립트 내 실제 사용 문맥도 함께 저장
- 출력: `data/vocab/{video_id}.json`
- **새 단어 추가**: `analyze_vocab.py`의 `VOCAB_DB` 딕셔너리에 항목 추가

### `tools/generate_html.py`
- CSV + scripts + grammar + vocab JSON을 읽어 HTML 생성
- `docs/index.html`: 전체 목록 (뱃지: YouTube/상세/Script/Vocab/Grammar)
- `docs/pages/{video_id}.html`: 상세 페이지 (임베드 + Script + Vocabulary + Grammar Notes)
- 자막은 문장 단위로 합쳐서 읽기 쉬운 형태로 출력

## 배포

- `main` 브랜치에 push하면 GitHub Actions가 자동으로 `tools/generate_html.py` 실행 후 `docs/` 를 GitHub Pages에 배포
- Pages 설정: 저장소 Settings → Pages → Source → **GitHub Actions**

## 문법 참고 자료

문법 분석은 `../Run42.195/grammar_in_use/units/unit_020.md` ~ `unit_046.md` 를 참고.

## 주의사항

- `fetch_scripts.py`는 YouTube IP 차단을 받을 수 있음 (0.5초 딜레이 적용됨)
- `yt-dlp`가 PATH에 없을 수 있음 → `pip install yt-dlp` 후 PATH 확인
- Python 3.9에서 동작하나, 3.10+ 권장 (yt-dlp 경고)
- `analyze_vocab.py`의 단어 사전은 수동 관리 — 새 어휘 발견 시 VOCAB_DB에 추가 필요
