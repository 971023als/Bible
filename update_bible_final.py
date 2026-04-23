import os
import requests
import json
import re
import time

# --- 설정 및 데이터베이스 ---
API_BASE = "https://bolls.life/get-chapter"
MODERN_REPLACEMENTS = {
    "가라사대": "말씀하시되",
    "가라사되": "말씀하시되",
    "기록하였으되": "기록된 대로",
    "이루려 하심이라": "이루기 위해서이다",
}

# 주요 분석 노트 데이터베이스
NOTES_DB = {
    "창세기_3장": """
### [💡 다양한 해석 및 교파별 관점]
* **'아룸(עָר֔וּם)'의 양면성**: 뱀의 '간교함'으로 번역된 이 단어는 '지혜로움/영리함'이라는 뜻도 가집니다. 지혜가 타락하여 기만이 된 상태를 보여줍니다.
* **니체의 시선**: 기독교적 '타락'을 생명 본능의 억압으로 보았던 니체는, 뱀의 유혹을 인간이 신의 구속에서 벗어나 스스로 가치를 창조하려는 첫 시도로 재해석하기도 합니다.
""",
    "창세기_4장": """
### [💡 신구약 대조 레퍼런스: 복수에서 용서로]
* **77배의 복수 (라멕)**: 인간의 끝없는 보복 심리를 상징합니다.
* **77번의 용서 (예수)**: 마태복음 18:22에서 예수님은 이 숫자를 그대로 가져와 '무한한 용서'로 전복시키셨습니다.
""",
    "출애굽기_4장": """
### [💡 다양한 해석 및 교파별 관점]
* **십보라의 피 남편**: 이 사건에서 '그'가 누구인지는 교파마다 해석이 갈립니다. 
    - **가톨릭**: 모세의 정화와 중보자적 자격을 갖추는 과정으로 중시합니다.
    - **개신교**: 언약(할례)의 절대적 중요성을 강조합니다.
""",
    "레위기_16장": """
### [💡 다양한 해석 및 교파별 관점]
* **아자젤(Azazel)의 정체**: 
    - **개신교**: 세상 죄를 지고 가는 그리스도의 예표.
    - **동방정교회**: 죄를 본래의 자리(광야/악)로 돌려보내는 우주적 정결.
""",
    "여호수아_10장": """
### [💡 의미심장한 인물: 아도니세덱]
* **아도니세덱 vs 멜기세덱**: 이름은 '의의 주'이나 하나님을 대적하는 예루살렘 왕입니다. 겉모습(이름)과 본질(대적자)의 차이를 보여줍니다.
""",
    "마태복음_16장": """
### [💡 교파별 관점: 반석 위에 세운 교회]
* **가톨릭**: 반석 = 베드로 개인 (교황권의 기초).
* **개신교**: 반석 = 베드로의 신앙 고백 혹은 그리스도 자신.
* **정교회**: 반석 = 사도들로부터 이어지는 올바른 신앙의 전통.
""",
    "요한복음_2장": """
### [💡 시대적 배경: 성전과 예수의 몸]
* **성전의 전환**: 웅장한 헤로데 성전에서 '부활하실 예수의 몸'으로 예배의 중심이 옮겨가는 대전환을 다룹니다. 서기 70년 성전 파괴를 예견하는 신학적 장치입니다.
""",
    "요한계시록_19장": """
### [💡 재림에 대한 올바른 이해]
* **사이비 교주 경계**: 재림은 특정 개인에게 은밀히 임하는 것이 아니라, 우주적이고 가시적인 사건입니다. 자신을 재림주라 칭하는 모든 인간 교주를 단호히 배격하는 것이 정통 신학의 핵심입니다.
"""
}

# 머메이드 다이어그램 데이터베이스
MERMAID_DB = {
    "여호수아_1장": """
```mermaid
graph TD
    A[요단강 도하] --> B[여리고성 함락]
    B --> C[아이성 전투]
    C --> D[남부/북부 정복]
    D --> E[땅의 분배]
```
""",
    "요한계시록_1장": """
```mermaid
graph TD
    A[일곱 인] --> B[일곱 나팔]
    B --> C[일곱 대접]
    C --> D[어린 양의 혼인 잔치]
    D --> E[새 하늘과 새 땅]
```
"""
}

BOOK_DATA = {
    "창세기": (1, 50), "출애굽기": (2, 40), "레위기": (3, 27), "민수기": (4, 36), "신명기": (5, 34),
    "여호수아": (6, 24), "사사기": (7, 21), "루기": (8, 4), "사무엘상": (9, 31), "사무엘하": (10, 24),
    "열왕기상": (11, 22), "열왕기하": (12, 25), "역대상": (13, 29), "역대하": (14, 36), "에스라": (15, 10),
    "느헤미야": (16, 13), "에스더": (17, 10), "욥기": (18, 42), "시편": (19, 150), "잠언": (20, 31),
    "전도서": (21, 12), "아가": (22, 8), "이사야": (23, 66), "예레미야": (24, 52), "예레미야애가": (25, 5),
    "에스겔": (26, 48), "다니엘": (27, 12), "호세아": (28, 14), "요엘": (29, 3), "아모스": (30, 9),
    "오바댜": (31, 1), "요나": (32, 4), "미가": (33, 7), "나훔": (34, 3), "하박국": (35, 3),
    "스바냐": (36, 3), "학개": (37, 2), "스가랴": (38, 14), "말라기": (39, 3),
    "마태복음": (40, 28), "마가복음": (41, 16), "누가복음": (42, 24), "요한복음": (43, 21), "사도행전": (44, 28),
    "로마서": (45, 16), "고린도전서": (46, 16), "고린도후서": (47, 13), "갈라디아서": (48, 6), "에베소서": (49, 6),
    "빌립보서": (50, 4), "골로새서": (51, 4), "데살로니가전서": (52, 5), "데살로니가후서": (53, 3),
    "디모데전서": (54, 6), "디모데후서": (55, 4), "디도서": (56, 3), "빌레몬서": (57, 1), "히브리서": (58, 13),
    "야고보서": (59, 5), "베드로전서": (60, 5), "베드로후서": (61, 3), "요한1서": (62, 5), "요한2서": (63, 1),
    "요한3서": (64, 1), "유다서": (65, 1), "요한계시록": (66, 22)
}

def modernize_korean(text):
    for old, new in MODERN_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text

def apply_original_emphasis(text):
    words = text.split()
    if len(words) <= 3:
        return f"**{text}**"
    # 후반부 40% 정도를 볼드 처리
    split_point = int(len(words) * 0.6)
    return " ".join(words[:split_point]) + " **" + " ".join(words[split_point:]) + "**"

def get_chapter_data(trans, book_id, chapter):
    try:
        url = f"{API_BASE}/{trans}/{book_id}/{chapter}/"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []

def process_chapter(book_name, book_id, chapter):
    krv_data = get_chapter_data("KRV", book_id, chapter)
    vulg_data = get_chapter_data("VULG", book_id, chapter)
    
    # 구약(1-39)은 WLC, 신약(40-66)은 TR (Bolls API 기준)
    orig_trans = "WLC" if book_id <= 39 else "TR"
    orig_data = get_chapter_data(orig_trans, book_id, chapter)

    # 매핑 (절 번호 기준)
    vulg_map = {v['verse']: v['text'] for v in vulg_data}
    orig_map = {o['verse']: o['text'] for o in orig_data}

    lines = [f"# {book_name} {chapter}장", "\n", "📖 **안내**: 이 파일은 대조 분석용으로 제작되었습니다. 읽기 전 [FAQ.md](../../FAQ.md)를 참고하시면 구조를 이해하는 데 도움이 됩니다.", "\n"]
    
    for v in krv_data:
        verse_num = v['verse']
        k_text = modernize_korean(v['text'])
        v_text = vulg_map.get(verse_num, "")
        o_text = orig_map.get(verse_num, "")
        
        lines.append(f"### {verse_num}절")
        lines.append(k_text)
        if v_text:
            lines.append(f"*{v_text}*")
        if o_text:
            lines.append(apply_original_emphasis(o_text))
        lines.append("\n")

    # 분석 노트 및 머메이드 삽입
    key = f"{book_name}_{chapter}장"
    if key in MERMAID_DB:
        lines.append(MERMAID_DB[key])
        lines.append("\n")
    if key in NOTES_DB:
        lines.append(NOTES_DB[key])
        lines.append("\n")
    
    # 하단 공통 테마
    lines.append("\n---\n")
    lines.append("♾️ **변치 않는 하나님의 언약**: 이 장에서도 하나님의 변함없는 '사랑과 평화(Love and Peace)'의 물줄기를 발견할 수 있습니다.")

    return "\n".join(lines)

def main():
    root = "c:\\Users\\User\\OneDrive - usk.ac.kr\\문서\\Github\\Bible"
    for book_name, (book_id, chapters) in BOOK_DATA.items():
        subdir = "구약" if book_id <= 39 else "신약"
        dir_path = os.path.join(root, subdir, book_name)
        os.makedirs(dir_path, exist_ok=True)
        
        print(f"Updating {book_name} ({chapters} chapters)...", flush=True)
        for ch in range(1, chapters + 1):
            file_path = os.path.join(dir_path, f"{book_name}_{ch}장.md")
            content = process_chapter(book_name, book_id, ch)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            time.sleep(0.3) # API 부하 방지

if __name__ == "__main__":
    main()
