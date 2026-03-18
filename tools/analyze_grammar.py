"""
Analyze script sentences against Grammar in Use Units 20-46.
Produces data/grammar/{video_id}.json for each script.
"""
import json
import os
import re

SCRIPTS_DIR = "data/scripts"
GRAMMAR_DIR = "data/grammar"
os.makedirs(GRAMMAR_DIR, exist_ok=True)

# Grammar rules: unit number, title, regex patterns, Korean explanation
GRAMMAR_RULES = [
    {
        "unit": 20, "title": "be going to (do)",
        "desc": "계획된 의도 또는 근거 있는 예측",
        "patterns": [
            r"\b(i'?m|you'?re|he'?s|she'?s|it'?s|we'?re|they'?re|is|are|am)\s+going\s+to\s+\w+",
            r"\b(i\s+am|you\s+are|he\s+is|she\s+is|we\s+are|they\s+are)\s+going\s+to\s+\w+",
            r"\bnot\s+going\s+to\s+\w+",
        ]
    },
    {
        "unit": 21, "title": "will / shall",
        "desc": "예측, 즉석 결정, 약속/제안",
        "patterns": [
            r"\bi'?ll\s+\w+",
            r"\bwe'?ll\s+\w+",
            r"\b(he|she|it|you|they)'?ll\s+\w+",
            r"\bwill\s+(not\s+)?\w+",
            r"\bshall\s+(i|we)\s+\w+",
        ]
    },
    {
        "unit": 22, "title": "will / won't",
        "desc": "거부, 불가, 확신 표현",
        "patterns": [
            r"\bwon'?t\s+\w+",
        ]
    },
    {
        "unit": 24, "title": "will be doing / will have done",
        "desc": "미래진행 / 미래완료",
        "patterns": [
            r"\bwill\s+be\s+\w+ing\b",
            r"\bwill\s+have\s+\w+(ed|en|t)\b",
        ]
    },
    {
        "unit": 25, "title": "When I do / When I've done",
        "desc": "시간/조건절에서 현재시제 사용",
        "patterns": [
            r"\b(when|before|after|until|as\s+soon\s+as)\s+(i|you|he|she|it|we|they)\s+(get|come|arrive|finish|see|have|leave|start|go)\b",
        ]
    },
    {
        "unit": 26, "title": "can / could / be able to",
        "desc": "능력과 가능성",
        "patterns": [
            r"\bcan'?t?\s+\w+",
            r"\bcould(n'?t)?\s+\w+",
            r"\b(be|been|is|are|am|was|were)\s+able\s+to\s+\w+",
        ]
    },
    {
        "unit": 27, "title": "could have (done)",
        "desc": "과거 가능했지만 하지 않은 일",
        "patterns": [
            r"\bcould\s+have\s+\w+(ed|en|t)\b",
            r"\bcouldn'?t\s+have\s+\w+(ed|en|t)\b",
        ]
    },
    {
        "unit": 28, "title": "must / can't (deduction)",
        "desc": "추론 (확실/불가능)",
        "patterns": [
            r"\bmust\s+be\b",
            r"\bmust\s+have\s+\w+(ed|en|t)\b",
            r"\bcan'?t\s+be\b",
            r"\bcan'?t\s+have\s+\w+(ed|en|t)\b",
        ]
    },
    {
        "unit": 29, "title": "may / might (possibility)",
        "desc": "현재 가능성 (~일 수도 있다)",
        "patterns": [
            r"\bmay\s+(not\s+)?\w+",
            r"\bmight\s+(not\s+)?\w+",
        ]
    },
    {
        "unit": 30, "title": "may/might have (done)",
        "desc": "과거 가능성 추측",
        "patterns": [
            r"\b(may|might)\s+have\s+\w+(ed|en|t)\b",
        ]
    },
    {
        "unit": 31, "title": "have to / must",
        "desc": "의무 (외부/내부)",
        "patterns": [
            r"\bhave\s+to\s+\w+",
            r"\bhas\s+to\s+\w+",
            r"\bhad\s+to\s+\w+",
            r"\bdon'?t\s+have\s+to\b",
            r"\bmust\s+(?!be\b|have\b)\w+",
        ]
    },
    {
        "unit": 32, "title": "mustn't / needn't",
        "desc": "금지 / 불필요",
        "patterns": [
            r"\bmustn'?t\s+\w+",
            r"\bneedn'?t\s+\w+",
            r"\bdon'?t\s+need\s+to\b",
        ]
    },
    {
        "unit": 33, "title": "should (advice)",
        "desc": "조언, 의견, 당연한 상태",
        "patterns": [
            r"\bshould(n'?t)?\s+\w+",
        ]
    },
    {
        "unit": 34, "title": "should have (done)",
        "desc": "과거 후회 (했어야/하지 말았어야)",
        "patterns": [
            r"\bshould(n'?t)?\s+have\s+\w+(ed|en|t)\b",
        ]
    },
    {
        "unit": 35, "title": "had better / it's time",
        "desc": "강한 조언 / 때가 되었다",
        "patterns": [
            r"\b(had|'?d)\s+better\s+(not\s+)?\w+",
            r"\bit'?s\s+time\s+(to|for)\b",
            r"\bit'?s\s+time\s+(i|you|he|she|we|they)\s+\w+",
        ]
    },
    {
        "unit": 36, "title": "would (habit/conditional)",
        "desc": "과거 습관, 가정법, 정중한 표현",
        "patterns": [
            r"\bwould(n'?t)?\s+\w+",
            r"\b(i|he|she|we|they)'?d\s+\w+",
        ]
    },
    {
        "unit": 37, "title": "Can/Could/Would you...?",
        "desc": "요청, 제안, 허락",
        "patterns": [
            r"\b(can|could|would|may)\s+(you|i|we)\s+\w+\?",
            r"\bwould\s+you\s+mind\b",
        ]
    },
    {
        "unit": 38, "title": "If I do / If I did",
        "desc": "1형/2형 조건문",
        "patterns": [
            r"\bif\s+(i|you|he|she|it|we|they)\s+(do|does|did|had|were|was|get|go|take|come|have|know|could)\b",
        ]
    },
    {
        "unit": 39, "title": "I wish I knew",
        "desc": "현재 반대 소망",
        "patterns": [
            r"\bi\s+wish\s+(i|you|he|she|it|we|they)\s+(could|had|were|was|knew|didn'?t)\b",
        ]
    },
    {
        "unit": 40, "title": "If I had known / I wish I had",
        "desc": "과거 반대 가정/후회",
        "patterns": [
            r"\bif\s+(i|you|he|she|we|they)\s+had\s+\w+(ed|en|t)\b",
            r"\bi\s+wish\s+(i|you|he|she|we|they)\s+had\s+\w+(ed|en|t)\b",
        ]
    },
    {
        "unit": 42, "title": "Passive (is done / was done)",
        "desc": "수동태 기본",
        "patterns": [
            r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en|t)\s+(by|in|at|on|for|from|with|to)\b",
            r"\b(is|are|was|were)\s+(made|done|called|known|given|taken|built|sold|used|held|born|found|seen|told|shown|left|kept|set|sent|paid|said|felt|thought|put)\b",
        ]
    },
    {
        "unit": 43, "title": "Passive (been done / being done)",
        "desc": "수동태 진행/완료",
        "patterns": [
            r"\b(has|have|had)\s+been\s+\w+(ed|en|t)\b",
            r"\b(is|are|was|were)\s+being\s+\w+(ed|en|t)\b",
            r"\b(will|can|could|should|must|may|might)\s+be\s+\w+(ed|en|t)\b",
        ]
    },
    {
        "unit": 44, "title": "Passive (special: get + p.p.)",
        "desc": "get 수동태, 전치사 수동태",
        "patterns": [
            r"\b(get|got|getting)\s+(married|hurt|lost|stuck|dressed|paid|fired|arrested|killed|involved|used|bored|tired|confused|excited|scared|burned|invited)\b",
        ]
    },
    {
        "unit": 45, "title": "It is said that / be said to",
        "desc": "보도/전달 수동태",
        "patterns": [
            r"\bit\s+is\s+(said|known|believed|reported|thought|expected|considered)\s+that\b",
            r"\b(is|are|was|were)\s+(said|known|believed|reported|thought|expected|considered)\s+to\b",
        ]
    },
    {
        "unit": 46, "title": "have something done",
        "desc": "사역 수동 (시키다/당하다)",
        "patterns": [
            r"\b(have|has|had|get|got)\s+(my|your|his|her|our|their|the|a)\s+\w+\s+\w+(ed|en|t)\b",
        ]
    },
]


def merge_sentences(snippets):
    """Merge subtitle snippets into sentences."""
    paragraphs = []
    current_text = ""
    for s in snippets:
        current_text += (" " if current_text else "") + s["text"]
        if current_text.rstrip().endswith((".", "!", "?", "...", '"')):
            paragraphs.append(current_text.strip())
            current_text = ""
    if current_text.strip():
        paragraphs.append(current_text.strip())
    return paragraphs


def analyze_script(sentences):
    """Find grammar patterns in sentences. Returns list of matched rules with examples."""
    results = []
    for rule in GRAMMAR_RULES:
        matched_sentences = []
        for sent in sentences:
            for pat in rule["patterns"]:
                if re.search(pat, sent, re.IGNORECASE):
                    matched_sentences.append(sent)
                    break
        if matched_sentences:
            results.append({
                "unit": rule["unit"],
                "title": rule["title"],
                "desc": rule["desc"],
                "examples": matched_sentences[:5],  # max 5 examples per rule
            })
    return results


def main():
    script_files = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".json")]
    total = 0
    for fname in script_files:
        video_id = fname.replace(".json", "")
        with open(os.path.join(SCRIPTS_DIR, fname), "r", encoding="utf-8") as f:
            snippets = json.load(f)
        sentences = merge_sentences(snippets)
        grammar = analyze_script(sentences)
        if grammar:
            with open(os.path.join(GRAMMAR_DIR, f"{video_id}.json"), "w", encoding="utf-8") as gf:
                json.dump(grammar, gf, ensure_ascii=False, indent=2)
            total += 1
            print(f"[{total}] {video_id}: {len(grammar)} grammar units found")
    print(f"\n완료: {total}개 영상에서 문법 분석 완료")


if __name__ == "__main__":
    main()
