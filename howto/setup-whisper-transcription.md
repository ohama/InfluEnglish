---
created: 2026-03-19
description: YouTube 영상에서 자막이 없을 때 Whisper로 음성→텍스트 변환하는 파이프라인 구축
---

# Whisper 음성→텍스트 변환 파이프라인

YouTube 자막이 없는 영상에서 오디오를 추출하고 faster-whisper로 텍스트를 생성하는 방법.

## The Insight

YouTube 자막 API는 자막이 비활성화된 영상, 자동생성 자막이 없는 영상에서 실패한다. 이때 오디오를 직접 다운로드하여 로컬 Whisper 모델로 변환하면 대부분의 영상에서 스크립트를 얻을 수 있다. 핵심은 **다운로드 도구 선택**과 **긴 영상 처리 전략**이다.

## Why This Matters

- YouTube 채널 147개 영상 중 124개가 자막 API로 가져올 수 없었다
- 자막 없이는 스크립트/문법/어휘 분석이 불가능
- Whisper로 102개를 추가 확보하여 총 137/147 커버리지 달성

## Recognition Pattern

- `youtube-transcript-api`가 "No transcripts found" 또는 "Subtitles are disabled" 에러를 던질 때
- 대량의 영상에서 자막이 없는 비율이 높을 때
- 한국어/영어 혼합 영상에서 자막이 아예 없을 때

## The Approach

```
pytubefix(오디오 다운로드) → faster-whisper(음성→텍스트) → JSON 저장 → 오디오 삭제
```

yt-dlp가 아닌 pytubefix를 쓰는 이유: yt-dlp는 버전이 오래되면 YouTube 403 에러를 반환하고, Python 3.9에서는 최신 버전 설치가 불가능하다. pytubefix는 이 제약이 없다.

### Step 1: 의존성 설치

```bash
pip install pytubefix faster-whisper
brew install ffmpeg
```

### Step 2: 오디오 다운로드

```python
from pytubefix import YouTube

yt = YouTube(url)
stream = yt.streams.filter(only_audio=True).first()
stream.download(output_path="data/audio", filename=f"{video_id}.mp4")
```

### Step 3: Whisper 변환

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", compute_type="int8")
segments, info = model.transcribe("data/audio/VIDEO_ID.mp4")
# info.language → 자동 감지된 언어 (ko, en 등)
snippets = [{"start": round(seg.start, 1), "text": seg.text.strip()} for seg in segments]
```

### Step 4: 긴 영상 스킵

8시간짜리 영상을 base 모델 CPU로 돌리면 수 시간 소요된다. 30분 초과 영상은 건너뛴다:

```python
duration = int(video.get("duration", 0) or 0)
if duration > 1800:  # 30분 초과
    continue
```

## Example

전체 파이프라인 실행:

```bash
python tools/transcribe_audio.py      # 전체 처리
python tools/transcribe_audio.py 5    # 5개만 처리
```

## 체크리스트

- [ ] ffmpeg 설치 확인
- [ ] 디스크 공간 확인 (오디오 파일 임시 저장)
- [ ] 긴 영상(30분+)은 별도 처리 또는 스킵
- [ ] 처리 후 오디오 파일 삭제 확인

## 모델 선택 가이드

| 모델 | RAM | 10분 영상 처리 | 정확도 |
|------|-----|----------------|--------|
| `base` | ~1GB | ~2분 | 보통 |
| `small` | ~2GB | ~5분 | 좋음 |
| `medium` | ~5GB | ~10분 | 매우 좋음 |

대량 처리에는 `base`, 정확도가 중요하면 `small` 이상 사용.
