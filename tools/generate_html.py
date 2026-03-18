import csv
import html
import json
import os
from datetime import datetime

SCRIPTS_DIR = "data/scripts"
GRAMMAR_DIR = "data/grammar"
PAGES_DIR = "docs/pages"
os.makedirs(PAGES_DIR, exist_ok=True)

with open("data/youtube_videos.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    videos = list(reader)

STYLE = """
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #333; }
  .container { max-width: 1100px; margin: 0 auto; padding: 20px; }
  h1 { text-align: center; margin: 20px 0; font-size: 1.8em; }
  .meta { text-align: center; color: #888; margin-bottom: 20px; font-size: 0.9em; }
  a { color: #e74c3c; text-decoration: none; }
  a:hover { text-decoration: underline; }
"""

TABLE_STYLE = """
  table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  th { background: #e74c3c; color: #fff; padding: 12px 10px; text-align: left; font-size: 0.9em; }
  td { padding: 10px; border-bottom: 1px solid #eee; font-size: 0.9em; vertical-align: middle; }
  tr:hover { background: #fafafa; }
  .video-cell { display: flex; align-items: center; gap: 12px; }
  .video-cell img { width: 120px; border-radius: 4px; flex-shrink: 0; }
  .video-info { display: flex; flex-direction: column; gap: 6px; }
  .video-title { color: #333; text-decoration: none; font-weight: 500; }
  .video-title:hover { color: #e74c3c; text-decoration: underline; }
  .video-links { display: flex; gap: 6px; flex-wrap: wrap; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; font-weight: 600; text-decoration: none; }
  .badge:hover { opacity: 0.8; text-decoration: none; }
  .badge.yt { background: #ff0000; color: #fff; }
  .badge.detail { background: #3498db; color: #fff; }
  .badge.script { background: #2ecc71; color: #fff; }
  .badge.grammar { background: #9b59b6; color: #fff; }
  td:first-child, th:first-child { text-align: center; width: 40px; }
  td:nth-child(3), td:nth-child(4), td:nth-child(5), td:nth-child(6) { white-space: nowrap; text-align: center; }
  th:nth-child(3), th:nth-child(4), th:nth-child(5), th:nth-child(6) { text-align: center; }
  @media (max-width: 768px) {
    .video-cell img { width: 80px; }
    td, th { padding: 8px 5px; font-size: 0.8em; }
  }
"""

DETAIL_STYLE = """
  .back { display: inline-block; margin-bottom: 20px; font-size: 0.95em; }
  .video-header { background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .video-header h1 { font-size: 1.4em; text-align: left; margin-bottom: 10px; }
  .video-meta { color: #888; font-size: 0.9em; }
  .video-meta span { margin-right: 16px; }
  .embed { text-align: center; margin-bottom: 20px; }
  .embed iframe { width: 100%; max-width: 720px; aspect-ratio: 16/9; border: none; border-radius: 8px; }
  .transcript { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .transcript h2 { margin-bottom: 16px; font-size: 1.2em; }
  .sentence { margin: 0 0 12px 0; line-height: 1.8; font-size: 1.05em; }
  .no-script { color: #999; font-style: italic; }
  .grammar { background: #fff; border-radius: 8px; padding: 20px; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .grammar h2 { margin-bottom: 16px; font-size: 1.2em; }
  .grammar-unit { margin-bottom: 20px; border-left: 4px solid #3498db; padding-left: 16px; }
  .grammar-unit h3 { font-size: 1em; color: #3498db; margin-bottom: 4px; }
  .grammar-unit .grammar-desc { color: #888; font-size: 0.85em; margin-bottom: 8px; }
  .grammar-unit .example { background: #f8f9fa; border-radius: 4px; padding: 8px 12px; margin: 4px 0; font-size: 0.95em; line-height: 1.6; }
"""


def fmt_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


# --- Generate detail pages ---
detail_count = 0
for i, v in enumerate(videos, 1):
    url = v["url"]
    video_id = url.split("v=")[-1] if "v=" in url else ""
    if not video_id:
        continue

    title = html.escape(v["title"])
    date_raw = v["upload_date"]
    date_fmt = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:8]}" if len(date_raw) == 8 else date_raw
    duration = int(v["duration"]) if v["duration"] else 0
    dur_fmt = fmt_time(duration)
    views = f'{int(v["view_count"]):,}' if v["view_count"] else ""

    script_path = os.path.join(SCRIPTS_DIR, f"{video_id}.json")
    has_script = os.path.exists(script_path)

    lines_html = ""
    if has_script:
        with open(script_path, "r", encoding="utf-8") as sf:
            snippets = json.load(sf)
        # Merge snippets into sentences
        paragraphs = []
        current_text = ""
        current_start = 0
        for s in snippets:
            if not current_text:
                current_start = s["start"]
            current_text += (" " if current_text else "") + s["text"]
            if current_text.rstrip().endswith((".", "!", "?", "...", '"')):
                paragraphs.append({"start": current_start, "text": current_text.strip()})
                current_text = ""
        if current_text.strip():
            paragraphs.append({"start": current_start, "text": current_text.strip()})
        for p in paragraphs:
            text = html.escape(p["text"])
            lines_html += f'<p class="sentence">{text}</p>\n'
        detail_count += 1
    else:
        lines_html = '<p class="no-script">자막을 가져올 수 없는 영상입니다.</p>'

    # Grammar section
    grammar_html = ""
    grammar_path = os.path.join(GRAMMAR_DIR, f"{video_id}.json")
    if os.path.exists(grammar_path):
        with open(grammar_path, "r", encoding="utf-8") as gf:
            grammar_data = json.load(gf)
        if grammar_data:
            grammar_items = ""
            for g in grammar_data:
                examples = ""
                for ex in g["examples"]:
                    examples += f'<div class="example">{html.escape(ex)}</div>\n'
                grammar_items += f"""<div class="grammar-unit">
  <h3>Unit {g["unit"]}: {html.escape(g["title"])}</h3>
  <div class="grammar-desc">{html.escape(g["desc"])}</div>
  {examples}
</div>\n"""
            grammar_html = f"""
  <div class="grammar" id="grammar">
    <h2>Grammar Notes (Units 20-46)</h2>
    {grammar_items}
  </div>"""

    detail_page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Influenglish</title>
<style>{STYLE}{DETAIL_STYLE}</style>
</head>
<body>
<div class="container">
  <a href="../index.html" class="back">&larr; 목록으로</a>
  <div class="video-header">
    <h1>{title}</h1>
    <div class="video-meta">
      <span>{date_fmt}</span>
      <span>{dur_fmt}</span>
      <span>조회수 {views}</span>
      <span><a href="{url}" target="_blank">YouTube에서 보기</a></span>
    </div>
  </div>
  <div class="embed">
    <iframe src="https://www.youtube.com/embed/{video_id}" allowfullscreen></iframe>
  </div>
  <div class="transcript" id="script">
    <h2>Script</h2>
    {lines_html}
  </div>
  {grammar_html}
</div>
</body>
</html>"""

    with open(os.path.join(PAGES_DIR, f"{video_id}.html"), "w", encoding="utf-8") as pf:
        pf.write(detail_page)

# --- Generate index page ---
rows_html = ""
for i, v in enumerate(videos, 1):
    title = html.escape(v["title"])
    url = html.escape(v["url"])
    date_raw = v["upload_date"]
    date_fmt = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:8]}" if len(date_raw) == 8 else date_raw
    duration = int(v["duration"]) if v["duration"] else 0
    dur_fmt = fmt_time(duration)
    views = f'{int(v["view_count"]):,}' if v["view_count"] else ""
    video_id = url.split("v=")[-1] if "v=" in url else ""
    thumb = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id else ""

    has_script = os.path.exists(os.path.join(SCRIPTS_DIR, f"{video_id}.json"))
    has_grammar = os.path.exists(os.path.join(GRAMMAR_DIR, f"{video_id}.json"))
    script_badge = f'<a href="pages/{video_id}.html#script" class="badge script">Script</a>' if has_script else ""
    grammar_badge = f'<a href="pages/{video_id}.html#grammar" class="badge grammar">Grammar</a>' if has_grammar else ""

    rows_html += f"""
    <tr>
      <td>{i}</td>
      <td>
        <div class="video-cell">
          <a href="{url}" target="_blank">
            <img src="{thumb}" alt="thumbnail" loading="lazy">
          </a>
          <div class="video-info">
            <a href="{url}" target="_blank" class="video-title">{title}</a>
            <div class="video-links">
              <a href="{url}" target="_blank" class="badge yt">YouTube</a>
              <a href="pages/{video_id}.html" class="badge detail">상세</a>
              {script_badge}
              {grammar_badge}
            </div>
          </div>
        </div>
      </td>
      <td>{date_fmt}</td>
      <td>{dur_fmt}</td>
      <td>{views}</td>
    </tr>"""

now = datetime.now().strftime("%Y-%m-%d %H:%M")

index_page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Influenglish - YouTube Videos</title>
<style>{STYLE}{TABLE_STYLE}</style>
</head>
<body>
<div class="container">
  <h1>Influenglish YouTube Videos</h1>
  <p class="meta">{len(videos)}개 영상 ({detail_count}개 스크립트) | 업데이트: {now}</p>
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

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(index_page)

print(f"완료: index.html + {len(videos)}개 상세 페이지 ({detail_count}개 스크립트 포함)")
