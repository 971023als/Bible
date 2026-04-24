
import requests
import os
import time
import re

API_BASE = "https://bolls.life/get-chapter"

# 지혜 문학 대상
WISDOM_BOOKS = [
    {"id": 19, "name": "시편", "chapters": 150},
    {"id": 20, "name": "잠언", "chapters": 31},
]

NOTES_DB = {
    "시편_23": """
---
## 🌈 다원적 해석 및 심층 분석: 시편 23편
### 💡 핵심 통찰: 목자와 양의 신뢰 관계
* **여호와는 나의 목자**: 고대 근동에서 왕은 백성의 '목자'로 묘사되었습니다. 여기서 시인은 하나님을 자신의 진정한 통치자이자 보호자로 고백합니다.
* **푸른 풀밭과 쉴 만한 물가**: 영혼의 안식과 생명력을 상징합니다.

### 🏛️ 교파별 관점 대조
* **가톨릭**: 선한 목자이신 그리스도와 성체성사의 은총을 통한 영적 영양 공급을 강조합니다.
* **개신교**: 개인과 하나님 사이의 인격적 신뢰와 인도하심에 초점을 맞춥니다.
* **유대교**: 이스라엘 공동체를 돌보시는 하나님의 신실한 언약적 사랑으로 해석합니다.
""",
    "시편_119": """
---
## 🌈 다원적 해석 및 심층 분석: 시편 119편
### 💡 핵심 통찰: 율법(Torah)에 대한 알파벳 찬가
* **답관체(Acrostic) 구조**: 히브리어 알파벳 22자를 순서대로 사용하여, 삶의 모든 영역이 하나님의 말씀 아래 있음을 보여줍니다.
* **말씀의 기능**: 내 발의 등(Lamp)이자 내 길의 빛(Light).

### 🏛️ 교파별 관점 대조
* **동방정교회**: 시편 119편을 장례 예배의 핵심으로 사용하며, 죽음 이후에도 이어지는 하나님의 법에 대한 신비적 순종을 강조합니다.
* **개신교**: '오직 성경(Sola Scriptura)'의 원리를 뒷받침하는 가장 강력한 텍스트로 간주합니다.
""",
    "잠언_8": """
---
## 🌈 다원적 해석 및 심층 분석: 잠언 8장
### 💡 핵심 통찰: 선존하시는 지혜(Chokmah)
* **창조의 설계자**: 지혜는 창조의 도구이자 하나님 곁에 있던 창조의 조력자로 묘사됩니다.
* **기독론적 해석**: 신약의 '로고스(Logos)' 기독론과 연결되어, 그리스도의 선존성을 보여주는 구약적 근거로 쓰입니다.

### 🏛️ 철학적 시선
* **로고스(Logos)와 지혜**: 헬라 철학의 이성적 질서인 로고스와 히브리적 인격적 지혜의 융합을 보여줍니다.
""",
    "잠언_31": """
---
## 🌈 다원적 해석 및 심층 분석: 잠언 31장
### 💡 핵심 통찰: 현숙한 여인(Aishet Chayil)
* **지혜의 완성**: 잠언의 결론은 지혜를 이론이 아닌 삶으로 살아내는 '현숙한 여인'의 모습으로 끝납니다.
* **사회경제적 가치**: 그녀는 단순히 가정 내의 존재가 아니라 경제적 주체이자 공동체의 기둥으로 묘사됩니다.
"""
}

def get_data(url):
    for i in range(5):
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                return r.json()
        except:
            time.sleep(2)
    return None

def apply_emphasis(text, is_orig=False):
    if not text: return ""
    if is_orig:
        text = re.sub(r'(\[.*?\]|\(.*?\))', r'**\1**', text)
        words = text.split()
        if len(words) > 2:
            mid = len(words) // 2
            return " ".join(words[:mid]) + " **" + " ".join(words[mid:]) + "**"
    return text

def process_wisdom():
    base_path = "c:/Users/User/OneDrive - usk.ac.kr/문서/Github/Bible/구약"
    
    for book in WISDOM_BOOKS:
        print(f">>> Processing {book['name']}...")
        book_dir = os.path.join(base_path, book['name'])
        if not os.path.exists(book_dir):
            os.makedirs(book_dir)
            
        for ch in range(1, book['chapters'] + 1):
            k_data = get_data(f"{API_BASE}/KRV/{book['id']}/{ch}/")
            v_data = get_data(f"{API_BASE}/VULG/{book['id']}/{ch}/")
            o_data = get_data(f"{API_BASE}/WLC/{book['id']}/{ch}/")
            
            if not k_data: continue
            
            v_map = {v['verse']: v['text'] for v in (v_data or [])}
            o_map = {o['verse']: o['text'] for o in (o_data or [])}
            
            # 파일 명칭 처리 (시편은 '편', 잠언은 '장')
            suffix = "편" if book['name'] == "시편" else "장"
            content = [f"# {book['name']} {ch}{suffix}\n\n", "📖 **안내**: 이 파일은 대조 분석용으로 제작되었습니다.\n\n"]
            
            for v in k_data:
                v_num = v['verse']
                content.append(f"### {v_num}절\n")
                content.append(f"{v['text']}\n")
                content.append(f"*{v_map.get(v_num, '')}*\n")
                content.append(f"{apply_emphasis(o_map.get(v_num, ''), True)}\n\n")
            
            # 심층 분석 노트 주입
            note_key = f"{book['name']}_{ch}"
            if note_key in NOTES_DB:
                content.append(NOTES_DB[note_key])
            
            content.append("\n---\n\n♾️ **변치 않는 하나님의 언약**: 이 장에서도 하나님의 변함없는 '사랑과 평화(Love and Peace)'의 물줄기를 발견할 수 있습니다.\n")
            
            file_path = os.path.join(book_dir, f"{book['name']}_{ch}{suffix}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(content)
            if ch % 10 == 0:
                print(f"  Progress: {book['name']} {ch} completed")

if __name__ == "__main__":
    process_wisdom()
