import json
import subprocess
import csv

CHANNEL_URL = "https://www.youtube.com/@influenglish/videos"

# 한 번의 호출로 전체 영상 상세 정보 가져오기
cmd = [
    "yt-dlp",
    "--dump-json",
    "--skip-download",
    CHANNEL_URL
]

result = subprocess.run(cmd, capture_output=True, text=True)

rows = []
for line in result.stdout.strip().split("\n"):
    if not line:
        continue
    try:
        detail = json.loads(line)
    except json.JSONDecodeError:
        continue

    rows.append({
        "title": detail.get("title", ""),
        "url": detail.get("webpage_url", ""),
        "upload_date": detail.get("upload_date", ""),
        "duration": detail.get("duration", ""),
        "view_count": detail.get("view_count", ""),
        "channel": detail.get("channel", ""),
    })
    print(f"[{len(rows)}] {detail.get('title', '')}")

# CSV 저장
with open("data/youtube_videos.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["title", "url", "upload_date", "duration", "view_count", "channel"]
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"\n완료: {len(rows)}개 영상 → youtube_videos.csv 저장됨")
