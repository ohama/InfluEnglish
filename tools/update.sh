#!/bin/bash
# InfluEnglish 전체 업데이트 스크립트
# 새 영상 확인 → 자막 수집 → 문법/어휘 분석 → HTML 생성
#
# Usage: bash tools/update.sh

set -e
cd "$(dirname "$0")/.."

export PATH="/Users/ohama/Library/Python/3.9/bin:$PATH"

OLD_COUNT=$(wc -l < data/youtube_videos.csv)

echo "=== 1/6. 영상 목록 수집 ==="
python3 tools/crawl.py

NEW_COUNT=$(wc -l < data/youtube_videos.csv)
DIFF=$((NEW_COUNT - OLD_COUNT))

if [ "$DIFF" -eq 0 ]; then
    echo ""
    echo "새 영상 없음. 기존 ${OLD_COUNT}개 유지."
    echo ""
    read -p "그래도 나머지 파이프라인을 실행할까요? (y/N) " answer
    if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
        echo "종료."
        exit 0
    fi
else
    echo ""
    echo "새 영상 ${DIFF}개 발견! (${OLD_COUNT} → ${NEW_COUNT})"
    echo ""
fi

echo "=== 2/6. 자막 다운로드 (YouTube API) ==="
python3 tools/fetch_scripts.py || true

echo ""
echo "=== 3/6. 자막 없는 영상 음성 변환 (Whisper) ==="
python3 tools/transcribe_audio.py

echo ""
echo "=== 4/6. 문법 분석 ==="
python3 tools/analyze_grammar.py

echo ""
echo "=== 5/6. 어휘 분석 ==="
python3 tools/analyze_vocab.py

echo ""
echo "=== 6/6. HTML 생성 ==="
python3 tools/generate_html.py

echo ""
echo "========================================="
echo "  완료!"
echo "  scripts: $(ls data/scripts/ | wc -l | tr -d ' ')개"
echo "  grammar: $(ls data/grammar/ | wc -l | tr -d ' ')개"
echo "  vocab:   $(ls data/vocab/ | wc -l | tr -d ' ')개"
echo "  pages:   $(ls docs/pages/ | wc -l | tr -d ' ')개"
echo "========================================="
echo ""
echo "git add -A && git commit -m 'Update pages' && git push"
