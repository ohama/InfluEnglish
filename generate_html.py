import csv
import html
from datetime import datetime

with open("youtube_videos.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    videos = list(reader)

rows_html = ""
for i, v in enumerate(videos, 1):
    title = html.escape(v["title"])
    url = html.escape(v["url"])
    date_raw = v["upload_date"]
    date_fmt = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:8]}" if len(date_raw) == 8 else date_raw
    duration = int(v["duration"]) if v["duration"] else 0
    dur_fmt = f"{duration // 60}:{duration % 60:02d}"
    views = f'{int(v["view_count"]):,}' if v["view_count"] else ""
    video_id = url.split("v=")[-1] if "v=" in url else ""
    thumb = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id else ""

    rows_html += f"""
    <tr>
      <td>{i}</td>
      <td>
        <div class="video-cell">
          <a href="{url}" target="_blank">
            <img src="{thumb}" alt="thumbnail" loading="lazy">
          </a>
          <a href="{url}" target="_blank" class="video-title">{title}</a>
        </div>
      </td>
      <td>{date_fmt}</td>
      <td>{dur_fmt}</td>
      <td>{views}</td>
    </tr>"""

now = datetime.now().strftime("%Y-%m-%d %H:%M")

page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Influenglish - YouTube Videos</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #333; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 20px; }}
  h1 {{ text-align: center; margin: 20px 0; font-size: 1.8em; }}
  .meta {{ text-align: center; color: #888; margin-bottom: 20px; font-size: 0.9em; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  th {{ background: #e74c3c; color: #fff; padding: 12px 10px; text-align: left; font-size: 0.9em; }}
  td {{ padding: 10px; border-bottom: 1px solid #eee; font-size: 0.9em; vertical-align: middle; }}
  tr:hover {{ background: #fafafa; }}
  .video-cell {{ display: flex; align-items: center; gap: 12px; }}
  .video-cell img {{ width: 120px; border-radius: 4px; flex-shrink: 0; }}
  .video-title {{ color: #333; text-decoration: none; font-weight: 500; }}
  .video-title:hover {{ color: #e74c3c; text-decoration: underline; }}
  td:first-child, th:first-child {{ text-align: center; width: 40px; }}
  td:nth-child(3), td:nth-child(4), td:nth-child(5) {{ white-space: nowrap; text-align: center; }}
  th:nth-child(3), th:nth-child(4), th:nth-child(5) {{ text-align: center; }}
  @media (max-width: 768px) {{
    .video-cell img {{ width: 80px; }}
    td, th {{ padding: 8px 5px; font-size: 0.8em; }}
  }}
</style>
</head>
<body>
<div class="container">
  <h1>Influenglish YouTube Videos</h1>
  <p class="meta">{len(videos)}개 영상 | 업데이트: {now}</p>
  <table>
    <thead>
      <tr><th>#</th><th>제목</th><th>업로드일</th><th>길이</th><th>조회수</th></tr>
    </thead>
    <tbody>{rows_html}
    </tbody>
  </table>
</div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(page)

print(f"완료: {len(videos)}개 영상 → index.html 생성됨")
