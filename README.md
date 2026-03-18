# InfluEnglish

[캘리쌤 브이로그 영어(@influenglish)](https://www.youtube.com/@influenglish) 채널의 영상 목록을 수집하고 웹 페이지로 제공합니다.

**Live:** https://ohama.github.io/InfluEnglish/

## 구성

| 파일 | 설명 |
|------|------|
| `crawl.py` | `yt-dlp`로 채널 영상 메타데이터를 수집하여 CSV로 저장 |
| `generate_html.py` | CSV를 읽어 썸네일, 링크, 조회수가 포함된 HTML 페이지 생성 |
| `youtube_videos.csv` | 수집된 영상 데이터 |
| `index.html` | 생성된 웹 페이지 |

## 사용법

```bash
# 영상 목록 수집 (yt-dlp 필요)
pip install yt-dlp
python crawl.py

# HTML 생성
python generate_html.py
```

## 배포

`main` 브랜치에 push하면 GitHub Actions가 자동으로 HTML을 생성하여 GitHub Pages에 배포합니다.
