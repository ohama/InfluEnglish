# InfluEnglish

[캘리쌤 브이로그 영어(@influenglish)](https://www.youtube.com/@influenglish) 채널의 영상을 수집하고, 영어 스크립트 / 어휘 / 문법 분석을 제공하는 학습 사이트입니다.

**Live:** https://ohama.github.io/InfluEnglish/

## 기능

- 147개 영상 목록 및 상세 페이지
- 영어 스크립트 (YouTube 자막 + Whisper 음성 인식)
- 어휘 분석 (한국어 뜻, 스크립트 내 문맥, 사용 예문)
- 문법 분석 (Grammar in Use Units 20~46 기반 패턴 매칭)

## 프로젝트 구조

```
InfluEnglish/
├── tools/                      # 데이터 수집 및 빌드 스크립트
│   ├── crawl.py                # YouTube 영상 메타데이터 수집
│   ├── fetch_scripts.py        # YouTube 자막 다운로드
│   ├── transcribe_audio.py     # 자막 없는 영상 → Whisper 음성 변환
│   ├── analyze_grammar.py      # 문법 패턴 분석 (Units 20-46)
│   ├── analyze_vocab.py        # 어휘 분석 (뜻 + 예문)
│   ├── generate_html.py        # HTML 페이지 생성
│   └── update.sh               # 전체 파이프라인 일괄 실행
├── data/                       # 수집된 데이터
│   ├── youtube_videos.csv      # 영상 메타데이터
│   ├── scripts/                # 영상별 자막 JSON
│   ├── grammar/                # 영상별 문법 분석 JSON
│   └── vocab/                  # 영상별 어휘 분석 JSON
├── docs/                       # GitHub Pages 배포 (자동 생성)
│   ├── index.html              # 전체 영상 목록 페이지
│   └── pages/                  # 영상별 상세 페이지
├── howto/                      # 운영 가이드 문서
├── .github/workflows/
│   └── deploy.yml              # push 시 자동 Pages 배포
├── CLAUDE.md                   # Claude Code 프로젝트 가이드
└── README.md
```

## 빠른 시작

### 의존성 설치

```bash
pip install yt-dlp youtube-transcript-api pytubefix faster-whisper
brew install ffmpeg
```

### 전체 업데이트 (원커맨드)

```bash
bash tools/update.sh
```

새 영상 확인 → 자막 수집 → 음성 변환 → 문법/어휘 분석 → HTML 생성을 순서대로 실행합니다.

### 개별 실행

```bash
python tools/crawl.py              # 1. 영상 목록 수집
python tools/fetch_scripts.py      # 2. YouTube 자막 다운로드
python tools/transcribe_audio.py   # 3. 자막 없는 영상 음성 변환
python tools/analyze_grammar.py    # 4. 문법 분석
python tools/analyze_vocab.py      # 5. 어휘 분석
python tools/generate_html.py      # 6. HTML 생성
```

## 배포

`main` 브랜치에 push하면 GitHub Actions가 자동으로 `docs/` 디렉토리를 GitHub Pages에 배포합니다.

```bash
git add -A && git commit -m "Update pages" && git push
```
