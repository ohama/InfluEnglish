---
created: 2026-03-19
description: YouTube 자막 수집 시 실패 케이스별 폴백 전략과 IP 차단 대응
---

# YouTube 자막 수집 전략

YouTube 영상에서 자막을 가져올 때 발생하는 다양한 실패 케이스와 단계별 폴백 전략.

## The Insight

YouTube 자막 수집은 **3단계 폴백**으로 접근해야 한다. 하나의 방법으로는 절대 100% 커버리지를 달성할 수 없다. 각 단계가 실패하는 이유가 다르기 때문에, 실패 원인에 따라 다음 단계로 넘어가는 전략이 필요하다.

## Why This Matters

- youtube-transcript-api로는 147개 중 23개(16%)만 성공
- 3단계 폴백 적용 후 137개(93%) 달성
- 나머지 10개는 30분 초과 영상(의도적 스킵)

## Recognition Pattern

- 채널 영상 대량 수집 시 자막 성공률이 낮을 때
- "No transcripts found", "Subtitles are disabled", IP 차단 에러가 발생할 때

## The Approach

```
1단계: youtube-transcript-api (빠름, 무료)
  ↓ 실패
2단계: youtube-transcript-api + 한국어 폴백
  ↓ 실패 / IP 차단
3단계: pytubefix + Whisper (느리지만 확실)
```

### Step 1: 영어 자막 시도

```python
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id)  # 기본: 영어
```

**실패 케이스:**
- `No transcripts found` → 영어 자막 없음 (Step 2로)
- `Subtitles are disabled` → 자막 비활성화 (Step 3로)

### Step 2: 한국어 자막 폴백

```python
try:
    transcript = api.fetch(video_id)
except Exception:
    transcript = api.fetch(video_id, languages=["ko"])
```

**실패 케이스:**
- `IP blocked` → YouTube가 IP 차단 (시간 두고 재시도 또는 Step 3)
- 자막 자체가 없음 → Step 3

### Step 3: Whisper 음성 변환

```python
# pytubefix로 오디오 다운로드 → faster-whisper로 변환
# 상세: setup-whisper-transcription.md 참고
```

## IP 차단 대응

youtube-transcript-api는 짧은 시간에 많은 요청을 보내면 IP가 차단된다.

```python
import time
time.sleep(0.5)  # 요청 간 0.5초 딜레이
```

**차단 증상:** `YouTube is blocking requests from your IP`

**대응:**
1. 시간을 두고 재시도 (수 시간~하루)
2. 이미 받은 파일은 캐시하여 건너뜀
3. 나머지는 Whisper로 처리

## 캐시 전략

```python
out_path = f"data/scripts/{video_id}.json"
if os.path.exists(out_path):
    continue  # 이미 있으면 스킵
```

이 캐시 덕분에 스크립트를 여러 번 실행해도 안전하다. 새 영상만 처리된다.

## 체크리스트

- [ ] fetch_scripts.py 실행 (빠른 자막 수집)
- [ ] IP 차단 시 시간 두고 재실행
- [ ] transcribe_audio.py 실행 (나머지 Whisper 변환)
- [ ] 30분 초과 영상은 수동 확인 또는 스킵

## 관련 문서

- `setup-whisper-transcription.md` - Whisper 변환 상세
- `page-generation.md` - 전체 페이지 생성 가이드
