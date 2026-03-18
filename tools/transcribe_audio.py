"""
Transcribe audio from YouTube videos that have no subtitle.
Uses pytubefix to download audio and faster-whisper for speech-to-text.
Produces data/scripts/{video_id}.json (same format as fetch_scripts.py).

Usage:
    python tools/transcribe_audio.py          # Process all missing
    python tools/transcribe_audio.py 5        # Process first 5 missing
"""
import csv
import json
import os
import sys

SCRIPTS_DIR = "data/scripts"
AUDIO_DIR = "data/audio"
CSV_PATH = "data/youtube_videos.csv"
WHISPER_MODEL = "base"  # base/small/medium/large

os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)


def get_missing_videos():
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        videos = list(csv.DictReader(f))
    missing = []
    for v in videos:
        url = v["url"]
        video_id = url.split("v=")[-1] if "v=" in url else ""
        if not video_id:
            continue
        if not os.path.exists(os.path.join(SCRIPTS_DIR, f"{video_id}.json")):
            duration = int(v.get("duration", 0) or 0)
            if duration > 1800:  # Skip videos longer than 30 minutes
                continue
            missing.append({"video_id": video_id, "url": url, "title": v["title"]})
    return missing


def download_audio(video_id, url):
    from pytubefix import YouTube
    out_path = os.path.join(AUDIO_DIR, f"{video_id}.mp4")
    if os.path.exists(out_path):
        return out_path
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        if not stream:
            return None
        stream.download(output_path=AUDIO_DIR, filename=f"{video_id}.mp4")
        return out_path
    except Exception as e:
        print(f"  Download error: {e}")
        return None


def transcribe(audio_path):
    from faster_whisper import WhisperModel
    model = WhisperModel(WHISPER_MODEL, compute_type="int8")
    # Auto-detect language; filter English segments
    segments, info = model.transcribe(audio_path)
    snippets = []
    for seg in segments:
        text = seg.text.strip()
        if text:
            snippets.append({"start": round(seg.start, 1), "text": text})
    return snippets, info.language


def main():
    missing = get_missing_videos()
    if not missing:
        print("모든 영상에 스크립트가 있습니다.")
        return

    print(f"자막 없는 영상: {len(missing)}개\n")

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(missing)
    missing = missing[:limit]

    success = 0
    fail = 0
    for i, v in enumerate(missing, 1):
        vid = v["video_id"]
        print(f"[{i}/{len(missing)}] {v['title'][:60]}")

        print("  Downloading audio...")
        audio_path = download_audio(vid, v["url"])
        if not audio_path or not os.path.exists(audio_path):
            print("  FAIL: audio download failed")
            fail += 1
            continue

        print("  Transcribing...")
        try:
            snippets, lang = transcribe(audio_path)
            if snippets:
                out_path = os.path.join(SCRIPTS_DIR, f"{vid}.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(snippets, f, ensure_ascii=False, indent=2)
                print(f"  OK: {len(snippets)} segments (lang={lang})")
                success += 1
            else:
                print("  FAIL: no speech detected")
                fail += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            fail += 1

        # Clean up audio
        if os.path.exists(audio_path):
            os.remove(audio_path)

    print(f"\n완료: 성공 {success}, 실패 {fail}")


if __name__ == "__main__":
    main()
