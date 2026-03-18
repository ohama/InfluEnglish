# InfluEnglish

[캘리쌤 브이로그 영어(@influenglish)](https://www.youtube.com/@influenglish) 채널의 영상 목록과 영어 스크립트를 수집하여 웹 페이지로 제공합니다.

**Live:** https://ohama.github.io/InfluEnglish/

## 프로젝트 구조

```
InfluEnglish/
├── tools/                  # 데이터 수집 및 빌드 스크립트
│   ├── crawl.py            # yt-dlp로 채널 영상 메타데이터 수집 → CSV
│   ├── fetch_scripts.py    # YouTube 자막(스크립트) 다운로드 → JSON
│   └── generate_html.py    # CSV + JSON → HTML 페이지 생성
├── data/                   # 수집된 데이터
│   ├── youtube_videos.csv  # 영상 메타데이터 (제목, URL, 조회수 등)
│   └── scripts/            # 영상별 자막 JSON 파일
├── docs/                   # GitHub Pages 배포 디렉토리
│   ├── index.html          # 전체 영상 목록 페이지
│   └── pages/              # 영상별 상세 페이지 (임베드 + 스크립트)
└── .github/workflows/
    └── deploy.yml          # push 시 자동 빌드 & Pages 배포
```

## 사용법

모든 명령은 프로젝트 루트에서 실행합니다.

```bash
# 1. 영상 목록 수집 (yt-dlp 필요)
pip install yt-dlp
python tools/crawl.py

# 2. 자막 수집 (youtube-transcript-api 필요)
pip install youtube-transcript-api
python tools/fetch_scripts.py

# 3. HTML 생성
python tools/generate_html.py
```

## 배포

`main` 브랜치에 push하면 GitHub Actions가 자동으로 `docs/` 디렉토리를 GitHub Pages에 배포합니다.
