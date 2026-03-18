"""
Analyze scripts for intermediate/advanced vocabulary.
Produces data/vocab/{video_id}.json for each script.
"""
import json
import os
import re

SCRIPTS_DIR = "data/scripts"
VOCAB_DIR = "data/vocab"
os.makedirs(VOCAB_DIR, exist_ok=True)

# Basic words that don't need explanation (~600 most common)
BASIC_WORDS = set("""
a an the this that these those my your his her its our their
i me we us you he she it they him them who what which where when how why
is am are was were be been being do does did done
have has had having will would shall should can could may might must
not no yes and or but if so because when while since until before after
to of in on at by for with from up down out off over under
about into through during between against among around
go goes went gone going get gets got getting come comes came coming
make makes made making take takes took taken taking
give gives gave given giving say says said saying
tell tells told telling see sees saw seen seeing
know knows knew known knowing think thinks thought thinking
want wants wanted wanting look looks looked looking
find finds found finding use uses used using
need needs needed try tries tried trying
ask asks asked asking work works worked working
put puts putting call calls called calling
keep keeps kept keeping let lets letting
begin begins began beginning seem seems seemed
help helps helped showing show shows showed
hear hears heard play plays played
run runs ran running move moves moved moving
like likes liked live lives lived living
believe turn follow bring hold write stand lose pay meet
feel leave mean set read change lead close open watch start stop
really very much many more most some any all both each every
other another new old big small long short great good bad
little high right left first last next few
here there just also still even now then than too only
well back again ever never always sometimes already
people time way day thing man woman child world life hand part
place case week point number group problem year house country home
school water room mother father family night morning
one two three four five six seven eight nine ten
oh ok okay hey well yeah um ah right sure let
lot love thank today bit actually pretty food kind
watching fun nice everything things different best
hard guys happy stuff please bye cool top course
dinner better thanks eat head together days line date
study almost ready hope cute maybe buy something though
don't didn't can't won't shouldn't wouldn't couldn't
i'm it's that's let's you're we're they're he's she's i'll i've what's there's
gonna wanna gotta
""".split())

# Vocabulary dictionary: word -> {meaning, examples}
VOCAB_DB = {
    "scorching": {
        "meaning": "몹시 뜨거운, 타는 듯한",
        "examples": [
            "It's scorching hot outside today.",
            "The scorching sun made it hard to walk.",
            "We stayed inside during the scorching afternoon."
        ]
    },
    "sweaty": {
        "meaning": "땀이 나는, 땀투성이의",
        "examples": [
            "I was sweaty after the workout.",
            "His sweaty hands made it hard to grip the rope.",
            "It's normal to feel sweaty in a sauna."
        ]
    },
    "dehydrated": {
        "meaning": "탈수된, 수분이 부족한",
        "examples": [
            "Drink water so you don't get dehydrated.",
            "I felt dehydrated after running in the heat.",
            "The doctor said I was severely dehydrated."
        ]
    },
    "wimp": {
        "meaning": "겁쟁이, 나약한 사람",
        "examples": [
            "Don't be such a wimp!",
            "I'm a wimp when it comes to spicy food.",
            "He called me a wimp for not jumping in the pool."
        ]
    },
    "fancy": {
        "meaning": "고급스러운, 화려한",
        "examples": [
            "We went to a fancy restaurant for our anniversary.",
            "That's a fancy car you've got there.",
            "She was wearing a fancy dress to the party."
        ]
    },
    "recharge": {
        "meaning": "재충전하다, 기운을 회복하다",
        "examples": [
            "I need a vacation to recharge my batteries.",
            "Taking a nap helps me recharge.",
            "We spent the weekend recharging at the spa."
        ]
    },
    "cashless": {
        "meaning": "현금 없는, 무현금의",
        "examples": [
            "Many stores are going cashless now.",
            "Korea is becoming a cashless society.",
            "I prefer cashless payments for convenience."
        ]
    },
    "terrified": {
        "meaning": "매우 무서워하는, 겁에 질린",
        "examples": [
            "I'm terrified of heights.",
            "She was terrified when she heard the noise.",
            "The kids were terrified of the haunted house."
        ]
    },
    "suffocating": {
        "meaning": "숨이 막히는, 질식할 것 같은",
        "examples": [
            "The heat in the room was suffocating.",
            "I felt like I was suffocating in the crowd.",
            "The smoke was suffocating."
        ]
    },
    "goosebumps": {
        "meaning": "소름, 닭살",
        "examples": [
            "I got goosebumps from the cold.",
            "That scary movie gave me goosebumps.",
            "Her singing was so beautiful it gave me goosebumps."
        ]
    },
    "chattering": {
        "meaning": "(이가) 딱딱 부딪치는, 수다 떠는",
        "examples": [
            "My teeth were chattering from the cold.",
            "The monkeys were chattering in the trees.",
            "Stop chattering and listen to the teacher."
        ]
    },
    "struggling": {
        "meaning": "힘들어하는, 고군분투하는",
        "examples": [
            "I was struggling to keep up with the pace.",
            "Many students are struggling with math.",
            "She's been struggling financially this year."
        ]
    },
    "overflow": {
        "meaning": "넘치다, 넘쳐흐르다",
        "examples": [
            "The bathtub is about to overflow!",
            "The river overflowed after heavy rain.",
            "My inbox is overflowing with emails."
        ]
    },
    "slurped": {
        "meaning": "후루룩 소리내며 먹다",
        "examples": [
            "He slurped his noodles loudly.",
            "It's okay to slurp ramen in Japan.",
            "She slurped the last bit of soup from the bowl."
        ]
    },
    "haggle": {
        "meaning": "흥정하다, 값을 깎다",
        "examples": [
            "You can haggle at the market.",
            "I managed to haggle the price down by half.",
            "Don't be afraid to haggle with street vendors."
        ]
    },
    "bargain": {
        "meaning": "흥정하다; 할인 상품, 좋은 거래",
        "examples": [
            "I got a real bargain at the sale.",
            "She's good at finding bargains.",
            "We bargained with the seller for a lower price."
        ]
    },
    "exhausted": {
        "meaning": "완전히 지친, 기진맥진한",
        "examples": [
            "I was exhausted after the long hike.",
            "She looked exhausted from working overtime.",
            "The kids were exhausted after playing all day."
        ]
    },
    "gorgeous": {
        "meaning": "아주 아름다운, 멋진",
        "examples": [
            "The sunset was absolutely gorgeous.",
            "You look gorgeous in that dress!",
            "What a gorgeous view from the mountain top."
        ]
    },
    "stunning": {
        "meaning": "놀라울 정도로 아름다운, 기절할 만한",
        "examples": [
            "The scenery was absolutely stunning.",
            "She looked stunning at the event.",
            "The building has a stunning design."
        ]
    },
    "breathtaking": {
        "meaning": "숨이 멎을 듯한, 장관인",
        "examples": [
            "The view from the top was breathtaking.",
            "It was a breathtaking performance.",
            "The Grand Canyon is truly breathtaking."
        ]
    },
    "souvenir": {
        "meaning": "기념품",
        "examples": [
            "I bought a souvenir for my mom.",
            "This magnet is a souvenir from Paris.",
            "The gift shop sells all kinds of souvenirs."
        ]
    },
    "authentic": {
        "meaning": "정통의, 진짜의",
        "examples": [
            "This restaurant serves authentic Italian food.",
            "Is this an authentic designer bag?",
            "I want to try authentic Korean kimchi."
        ]
    },
    "touristy": {
        "meaning": "관광객이 많은, 관광지스러운",
        "examples": [
            "This area is too touristy for me.",
            "Let's avoid the touristy restaurants.",
            "Times Square is very touristy but still fun."
        ]
    },
    "definitely": {
        "meaning": "확실히, 분명히",
        "examples": [
            "I'm definitely coming to the party.",
            "This is definitely the best pizza I've ever had.",
            "You should definitely try the cheesecake."
        ]
    },
    "absolutely": {
        "meaning": "절대적으로, 완전히",
        "examples": [
            "That was absolutely amazing!",
            "I absolutely love this song.",
            "You're absolutely right about that."
        ]
    },
    "literally": {
        "meaning": "문자 그대로, 정말로",
        "examples": [
            "I literally can't stop laughing.",
            "She literally ran a marathon yesterday.",
            "The store is literally around the corner."
        ]
    },
    "hilarious": {
        "meaning": "아주 웃긴, 유쾌한",
        "examples": [
            "That joke was hilarious!",
            "He's a hilarious comedian.",
            "The movie was absolutely hilarious."
        ]
    },
    "ridiculous": {
        "meaning": "말도 안 되는, 우스꽝스러운",
        "examples": [
            "That price is ridiculous!",
            "Don't be ridiculous.",
            "It's ridiculous how expensive rent is here."
        ]
    },
    "awkward": {
        "meaning": "어색한, 불편한",
        "examples": [
            "There was an awkward silence.",
            "I felt so awkward at the party.",
            "It was awkward meeting my ex at the store."
        ]
    },
    "insane": {
        "meaning": "미친, 엄청난 (구어)",
        "examples": [
            "The traffic was insane today.",
            "This rollercoaster is insane!",
            "The prices here are absolutely insane."
        ]
    },
    "stoked": {
        "meaning": "매우 신나는, 기대되는 (슬랭)",
        "examples": [
            "I'm so stoked for the concert!",
            "She was stoked about getting the job.",
            "We're stoked to try this new restaurant."
        ]
    },
    "bland": {
        "meaning": "싱거운, 맛없는; 특색 없는",
        "examples": [
            "The soup tastes a bit bland.",
            "Add some seasoning, it's too bland.",
            "The movie was kind of bland and boring."
        ]
    },
    "craving": {
        "meaning": "갈망, 간절히 먹고 싶은",
        "examples": [
            "I'm craving pizza right now.",
            "She always has cravings for chocolate.",
            "I've been craving Korean food all week."
        ]
    },
    "massive": {
        "meaning": "거대한, 엄청난",
        "examples": [
            "There was a massive crowd at the concert.",
            "That's a massive improvement!",
            "He lives in a massive house."
        ]
    },
    "steep": {
        "meaning": "가파른; (가격이) 비싼",
        "examples": [
            "The mountain trail was very steep.",
            "That's a steep price for a coffee.",
            "Be careful on the steep stairs."
        ]
    },
    "affordable": {
        "meaning": "가격이 적당한, 알맞은",
        "examples": [
            "This restaurant is affordable and delicious.",
            "We're looking for affordable housing.",
            "The new phone is surprisingly affordable."
        ]
    },
    "pricey": {
        "meaning": "비싼 (구어)",
        "examples": [
            "The food here is a bit pricey.",
            "Organic vegetables can be pricey.",
            "New York is known for being pricey."
        ]
    },
    "overwhelmed": {
        "meaning": "압도된, 감당이 안 되는",
        "examples": [
            "I was overwhelmed by the amount of work.",
            "She felt overwhelmed with emotion.",
            "Don't feel overwhelmed; take it step by step."
        ]
    },
    "nostalgic": {
        "meaning": "향수를 느끼는, 그리운",
        "examples": [
            "This song makes me feel nostalgic.",
            "I'm feeling nostalgic about my college days.",
            "The old photos made us all nostalgic."
        ]
    },
    "refreshing": {
        "meaning": "상쾌한, 기분 좋은",
        "examples": [
            "This iced tea is so refreshing.",
            "It was refreshing to hear a different opinion.",
            "A refreshing breeze came through the window."
        ]
    },
    "cozy": {
        "meaning": "아늑한, 포근한",
        "examples": [
            "This café is really cozy.",
            "I love staying in my cozy bed on rainy days.",
            "They have a cozy little apartment."
        ]
    },
    "hideous": {
        "meaning": "매우 흉한, 끔찍한",
        "examples": [
            "That sweater is hideous!",
            "The monster looked absolutely hideous.",
            "The weather has been hideous all week."
        ]
    },
    "chill": {
        "meaning": "느긋한, 편안한; 쉬다 (슬랭)",
        "examples": [
            "Let's just chill at home tonight.",
            "He's a really chill person.",
            "We spent the weekend chilling by the pool."
        ]
    },
    "vibe": {
        "meaning": "분위기, 느낌",
        "examples": [
            "This place has a great vibe.",
            "I'm getting good vibes from this restaurant.",
            "The vibe at the concert was electric."
        ]
    },
    "swamped": {
        "meaning": "일에 파묻힌, 매우 바쁜",
        "examples": [
            "I'm swamped with work this week.",
            "The store was swamped with customers.",
            "Sorry I couldn't reply; I was swamped."
        ]
    },
    "commute": {
        "meaning": "통근하다; 통근",
        "examples": [
            "My daily commute takes about an hour.",
            "I commute by subway every day.",
            "Long commutes can be very tiring."
        ]
    },
    "chaotic": {
        "meaning": "혼란스러운, 무질서한",
        "examples": [
            "The morning was completely chaotic.",
            "Traffic was chaotic during rush hour.",
            "Moving to a new city can be chaotic."
        ]
    },
    "procrastinate": {
        "meaning": "미루다, 질질 끌다",
        "examples": [
            "Stop procrastinating and start studying!",
            "I tend to procrastinate when I'm stressed.",
            "He procrastinated until the last minute."
        ]
    },
    "nauseous": {
        "meaning": "메스꺼운, 구역질 나는",
        "examples": [
            "I feel nauseous after eating too much.",
            "The boat ride made me nauseous.",
            "She felt nauseous during the flight."
        ]
    },
    "sketchy": {
        "meaning": "수상한, 미심쩍은 (슬랭)",
        "examples": [
            "That alley looks a bit sketchy.",
            "I wouldn't eat there; it looks sketchy.",
            "He sent me a sketchy link."
        ]
    },
    "hectic": {
        "meaning": "매우 바쁜, 정신없는",
        "examples": [
            "It's been a hectic week at work.",
            "The holidays are always hectic.",
            "Her schedule is incredibly hectic."
        ]
    },
    "spontaneous": {
        "meaning": "즉흥적인, 자발적인",
        "examples": [
            "It was a spontaneous decision to travel.",
            "She's very spontaneous and fun.",
            "We took a spontaneous road trip."
        ]
    },
    "savory": {
        "meaning": "짭짤한, 감칠맛 나는",
        "examples": [
            "I prefer savory food over sweet.",
            "The stew had a rich, savory flavor.",
            "Korean food is known for its savory dishes."
        ]
    },
    "texture": {
        "meaning": "식감, 질감",
        "examples": [
            "The cake has a soft, fluffy texture.",
            "I love the crunchy texture of fried chicken.",
            "The texture of this fabric is so smooth."
        ]
    },
    "crispy": {
        "meaning": "바삭바삭한",
        "examples": [
            "The chicken was perfectly crispy.",
            "I like my bacon extra crispy.",
            "These fries are nice and crispy."
        ]
    },
    "chewy": {
        "meaning": "쫄깃쫄깃한",
        "examples": [
            "Tteokbokki has a chewy texture.",
            "The bread is soft and chewy.",
            "I love chewy gummy bears."
        ]
    },
    "spicy": {
        "meaning": "매운, 양념이 센",
        "examples": [
            "Korean food can be very spicy.",
            "I can't handle spicy food well.",
            "Would you like it mild or spicy?"
        ]
    },
    "seasoning": {
        "meaning": "양념, 조미료",
        "examples": [
            "Add some seasoning to the soup.",
            "The seasoning on this steak is perfect.",
            "Korean cooking uses a lot of different seasonings."
        ]
    },
    "ingredient": {
        "meaning": "재료, 성분",
        "examples": [
            "What are the main ingredients in this dish?",
            "Fresh ingredients make all the difference.",
            "I need to buy a few ingredients for dinner."
        ]
    },
    "fluent": {
        "meaning": "유창한",
        "examples": [
            "She's fluent in three languages.",
            "I want to become fluent in English.",
            "He speaks fluent Korean."
        ]
    },
    "pronounce": {
        "meaning": "발음하다",
        "examples": [
            "How do you pronounce this word?",
            "It's hard to pronounce some English sounds.",
            "She pronounces every word clearly."
        ]
    },
    "pronunciation": {
        "meaning": "발음",
        "examples": [
            "Your pronunciation has really improved.",
            "English pronunciation can be tricky.",
            "Focus on pronunciation, not just grammar."
        ]
    },
    "exaggerate": {
        "meaning": "과장하다",
        "examples": [
            "Don't exaggerate; it wasn't that bad.",
            "He tends to exaggerate his stories.",
            "I'm not exaggerating—it was incredible!"
        ]
    },
    "subtle": {
        "meaning": "미묘한, 은근한",
        "examples": [
            "There's a subtle difference between the two.",
            "She gave him a subtle hint.",
            "The flavor is subtle but delicious."
        ]
    },
    "outskirts": {
        "meaning": "외곽, 변두리",
        "examples": [
            "They live on the outskirts of the city.",
            "The factory is on the outskirts of town.",
            "We drove to the outskirts to find cheaper housing."
        ]
    },
    "landmark": {
        "meaning": "랜드마크, 유명 건물/장소",
        "examples": [
            "The Eiffel Tower is a famous landmark.",
            "Can you see any landmarks from here?",
            "We visited several historic landmarks."
        ]
    },
    "immigration": {
        "meaning": "출입국 관리, 이민",
        "examples": [
            "We had to wait in line at immigration.",
            "The immigration officer checked my passport.",
            "Immigration policies vary by country."
        ]
    },
    "customs": {
        "meaning": "세관; 관습",
        "examples": [
            "We passed through customs at the airport.",
            "Do you have anything to declare at customs?",
            "It's important to respect local customs."
        ]
    },
    "itinerary": {
        "meaning": "여행 일정",
        "examples": [
            "What's our itinerary for tomorrow?",
            "I planned a detailed itinerary for the trip.",
            "The tour guide handed out the itinerary."
        ]
    },
    "jet lag": {
        "meaning": "시차 피로",
        "examples": [
            "I'm still suffering from jet lag.",
            "It takes a few days to recover from jet lag.",
            "Drink lots of water to help with jet lag."
        ]
    },
    "layover": {
        "meaning": "경유, 환승 대기",
        "examples": [
            "We have a 3-hour layover in Tokyo.",
            "I hate long layovers at the airport.",
            "During the layover, we explored the city."
        ]
    },
    "reservation": {
        "meaning": "예약",
        "examples": [
            "I made a reservation for 7 pm.",
            "Do you have a reservation?",
            "You need a reservation at that restaurant."
        ]
    },
    "accommodate": {
        "meaning": "수용하다, 편의를 제공하다",
        "examples": [
            "The hotel can accommodate 200 guests.",
            "We'll try to accommodate your request.",
            "The room accommodates up to four people."
        ]
    },
    "complimentary": {
        "meaning": "무료의; 칭찬하는",
        "examples": [
            "The hotel offers complimentary breakfast.",
            "Here's a complimentary drink on the house.",
            "She was very complimentary about your work."
        ]
    },
    "inevitable": {
        "meaning": "피할 수 없는, 불가피한",
        "examples": [
            "Change is inevitable.",
            "Making mistakes is inevitable when learning.",
            "It was inevitable that they would meet again."
        ]
    },
    "perspective": {
        "meaning": "관점, 시각",
        "examples": [
            "Try to see things from a different perspective.",
            "Living abroad changed my perspective on life.",
            "Everyone has a unique perspective."
        ]
    },
    "embrace": {
        "meaning": "포용하다, 받아들이다",
        "examples": [
            "You should embrace new challenges.",
            "She embraced the opportunity to study abroad.",
            "Let's embrace the changes ahead of us."
        ]
    },
    "motivated": {
        "meaning": "동기부여된, 의욕적인",
        "examples": [
            "I feel really motivated to study English.",
            "She's a highly motivated student.",
            "What keeps you motivated every day?"
        ]
    },
    "dedicated": {
        "meaning": "헌신적인, 전념하는",
        "examples": [
            "She's very dedicated to her work.",
            "You need to be dedicated to improve.",
            "He's a dedicated teacher."
        ]
    },
    "consistent": {
        "meaning": "꾸준한, 일관된",
        "examples": [
            "Be consistent with your study habits.",
            "Consistent practice leads to improvement.",
            "Her performance has been very consistent."
        ]
    },
}


def merge_sentences(snippets):
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


def find_vocab(sentences):
    """Find vocabulary words used in the script."""
    # Collect all words in the script
    script_words = set()
    word_contexts = {}
    for sent in sentences:
        words = re.findall(r"[a-zA-Z]+", sent.lower())
        for w in words:
            if w not in BASIC_WORDS and len(w) > 3:
                script_words.add(w)
                if w not in word_contexts:
                    word_contexts[w] = []
                if len(word_contexts[w]) < 2:
                    word_contexts[w].append(sent)

    results = []
    for word in sorted(script_words):
        if word in VOCAB_DB:
            entry = VOCAB_DB[word]
            results.append({
                "word": word,
                "meaning": entry["meaning"],
                "examples": entry["examples"],
                "context": word_contexts.get(word, [])[:2],
            })
    return results


def main():
    script_files = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".json")]
    total = 0
    for fname in sorted(script_files):
        video_id = fname.replace(".json", "")
        with open(os.path.join(SCRIPTS_DIR, fname), "r", encoding="utf-8") as f:
            snippets = json.load(f)
        sentences = merge_sentences(snippets)
        vocab = find_vocab(sentences)
        if vocab:
            with open(os.path.join(VOCAB_DIR, f"{video_id}.json"), "w", encoding="utf-8") as vf:
                json.dump(vocab, vf, ensure_ascii=False, indent=2)
            total += 1
            words = [v["word"] for v in vocab]
            print(f"[{total}] {video_id}: {len(vocab)} words - {', '.join(words[:8])}")
    print(f"\n완료: {total}개 영상에서 어휘 분석 완료")


if __name__ == "__main__":
    main()
