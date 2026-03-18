import csv
import json
import os
import time
from youtube_transcript_api import YouTubeTranscriptApi

SCRIPTS_DIR = "scripts"
os.makedirs(SCRIPTS_DIR, exist_ok=True)

api = YouTubeTranscriptApi()

with open("youtube_videos.csv", "r", encoding="utf-8-sig") as f:
    videos = list(csv.DictReader(f))

print(f"총 {len(videos)}개 영상에서 자막 수집 시작\n")

results = []
for i, v in enumerate(videos, 1):
    url = v["url"]
    video_id = url.split("v=")[-1] if "v=" in url else ""
    if not video_id:
        continue

    out_path = os.path.join(SCRIPTS_DIR, f"{video_id}.json")
    if os.path.exists(out_path):
        print(f"[{i}/{len(videos)}] SKIP (cached) {v['title'][:50]}")
        results.append({"video_id": video_id, "status": "cached"})
        continue

    try:
        try:
            transcript = api.fetch(video_id)
        except Exception:
            transcript = api.fetch(video_id, languages=["ko"])
        snippets = [{"start": s.start, "text": s.text} for s in transcript.snippets]
        with open(out_path, "w", encoding="utf-8") as jf:
            json.dump(snippets, jf, ensure_ascii=False, indent=2)
        print(f"[{i}/{len(videos)}] OK ({len(snippets)} lines) {v['title'][:50]}")
        results.append({"video_id": video_id, "status": "ok", "lines": len(snippets)})
    except Exception as e:
        print(f"[{i}/{len(videos)}] FAIL {v['title'][:50]} - {e}")
        results.append({"video_id": video_id, "status": "fail", "error": str(e)})

    time.sleep(0.5)

ok = sum(1 for r in results if r["status"] in ("ok", "cached"))
fail = sum(1 for r in results if r["status"] == "fail")
print(f"\n완료: 성공 {ok}, 실패 {fail}")
