
import requests
import os
import time
import re

API_BASE = "https://bolls.life/get-chapter"

# 정밀 타격 대상: 역사서
TARGET_BOOKS = [
    {"id": 6, "name": "여호수아", "chapters": 24},
    {"id": 7, "name": "사사기", "chapters": 21},
    {"id": 8, "name": "룻기", "chapters": 4},
    {"id": 9, "name": "사무엘상", "chapters": 31},
    {"id": 10, "name": "사무엘하", "chapters": 24},
    {"id": 11, "name": "열왕기상", "chapters": 22},
    {"id": 12, "name": "열왕기하", "chapters": 25},
]

NOTES_DB = {
    "여호수아_10": "### [💡 의미심장한 인물: 아도니세덱]\n* **아도니세덱 vs 멜기세덱**: 이름은 '의의 주'이나 하나님을 대적하는 예루살렘 왕입니다. 겉모습(이름)과 본질(대적자)의 차이를 보여줍니다.",
    # 추가적인 역사서 인사이트들을 여기에 배치할 수 있습니다.
}

def get_data(url):
    for i in range(5): # 5번까지 재시도
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.json()
        except:
            time.sleep(2)
    return None

def apply_emphasis(text, is_orig=False):
    if not text: return ""
    # 원어 강조 로직: 후반부 볼드 + 특수기호 볼드
    if is_orig:
        text = re.sub(r'(\[.*?\]|\(.*?\))', r'**\1**', text)
        words = text.split()
        if len(words) > 2:
            mid = len(words) // 2
            return " ".join(words[:mid]) + " **" + " ".join(words[mid:]) + "**"
    return text

def process_historical():
    base_path = "c:/Users/User/OneDrive - usk.ac.kr/문서/Github/Bible/구약"
    
    for book in TARGET_BOOKS:
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
            
            content = [f"# {book['name']} {ch}장\n\n", "📖 **안내**: 이 파일은 대조 분석용으로 제작되었습니다.\n\n"]
            
            for v in k_data:
                v_num = v['verse']
                content.append(f"### {v_num}절\n")
                content.append(f"{v['text']}\n")
                content.append(f"*{v_map.get(v_num, '')}*\n")
                content.append(f"{apply_emphasis(o_map.get(v_num, ''), True)}\n\n")
            
            # 신학적 노트 주입
            note_key = f"{book['name']}_{ch}"
            if note_key in NOTES_DB:
                content.append(f"\n---\n{NOTES_DB[note_key]}\n")
            
            content.append("\n---\n\n♾️ **변치 않는 하나님의 언약**: 이 장에서도 하나님의 변함없는 '사랑과 평화(Love and Peace)'의 물줄기를 발견할 수 있습니다.\n")
            
            file_path = os.path.join(book_dir, f"{book['name']}_{ch}장.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(content)
            print(f"  Completed {book['name']} {ch}")

if __name__ == "__main__":
    process_historical()
