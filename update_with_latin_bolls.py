import os
import json
import urllib.request
import time

# Mapping Korean book names to Bolls Bible API IDs
BOOK_DATA = {
    "창세기": 1, "출애굽기": 2, "레위기": 3, "민수기": 4, "신명기": 5,
    "여호수아": 6, "사사기": 7, "룻기": 8, "사무엘상": 9, "사무엘하": 10,
    "열왕기상": 11, "열왕기하": 12, "역대상": 13, "역대하": 14, "에스라": 15,
    "느헤미야": 16, "에스더": 17, "욥기": 18, "시편": 19, "잠언": 20,
    "전도서": 21, "아가": 22, "이사야": 23, "예레미야": 24, "예레미야에가": 25,
    "에스겔": 26, "다니엘": 27, "호세아": 28, "요엘": 29, "아모스": 30,
    "오바댜": 31, "요나": 32, "미가": 33, "나훔": 34, "하박국": 35,
    "스바냐": 36, "학개": 37, "스가랴": 38, "말라기": 39, "마태복음": 40,
    "마가복음": 41, "누가복음": 42, "요한복음": 43, "사도행전": 44, "로마서": 45,
    "고린도전서": 46, "고린도후서": 47, "갈라디아서": 48, "에베소서": 49, "빌립보서": 50,
    "골로새서": 51, "데살로니가전서": 52, "데살로니가후서": 53, "디모데전서": 54, "디모데후서": 55,
    "디도서": 56, "빌레몬서": 57, "히브리서": 58, "야고보서": 59, "베드로전서": 60,
    "베드로후서": 61, "요한1서": 62, "요한2서": 63, "요한3서": 64, "유다서": 65, "요한계시록": 66
}

BASE_DIR = r"c:\Users\User\OneDrive - usk.ac.kr\문서\Github\Bible"

def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        # Silently fail for individual chapter errors
        return None

def generate_markdown(book_name, chapter, korean_verses, original_verses, latin_verses):
    lines = [f"# {book_name} {chapter}장\n\n"]
    
    orig_map = {v['verse']: v['text'] for v in original_verses} if original_verses else {}
    latin_map = {v['verse']: v['text'] for v in latin_verses} if latin_verses else {}
    
    for v in korean_verses:
        verse_num = v['verse']
        korean_text = v['text']
        lines.append(f"### {verse_num}절\n")
        lines.append(f"{korean_text}\n")
        
        # Add Latin if available
        if verse_num in latin_map:
            lines.append(f"*{latin_map[verse_num].strip()}*\n")
            
        # Add Original if available
        if verse_num in orig_map:
            lines.append(f"{orig_map[verse_num]}\n")
            
        lines.append("\n")
    
    return "".join(lines)

def process_book(dir_path, book_name, is_old_testament):
    book_id = BOOK_DATA.get(book_name)
    if not book_id:
        return
    
    book_dir = os.path.join(dir_path, book_name)
    if not os.path.exists(book_dir):
        os.makedirs(book_dir)
        
    translation_orig = "WLC" if is_old_testament else "SBLGNT"
    translation_ko = "KRV"
    translation_latin = "VULG"

    # We iterate until we hit an empty chapter or a reasonable limit
    chapter = 1
    while True:
        filename = f"{book_name}_{chapter}장.md"
        file_path = os.path.join(book_dir, filename)
        
        print(f"  Updating {book_name} {chapter}장 with Latin bridge...", flush=True)
        
        ko_url = f"https://bolls.life/get-chapter/{translation_ko}/{book_id}/{chapter}/"
        orig_url = f"https://bolls.life/get-chapter/{translation_orig}/{book_id}/{chapter}/"
        lat_url = f"https://bolls.life/get-chapter/{translation_latin}/{book_id}/{chapter}/"
        
        ko_data = fetch_json(ko_url)
        if not ko_data: # If Korean chapter is missing, we likely hit the end of the book
            break
            
        time.sleep(0.1)
        orig_data = fetch_json(orig_url)
        time.sleep(0.1)
        lat_data = fetch_json(lat_url)
        
        md_content = generate_markdown(book_name, chapter, ko_data, orig_data, lat_data)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        chapter += 1
        time.sleep(0.2)

if __name__ == "__main__":
    # Clean up and re-process everything
    for part in ["구약", "신약"]:
        part_dir = os.path.join(BASE_DIR, part)
        is_ot = (part == "구약")
        
        # We process in the order of BOOK_DATA keys to be systematic
        for book_name in BOOK_DATA.keys():
            book_path = os.path.join(part_dir, book_name)
            if os.path.isdir(book_path):
                print(f"Processing {part}: {book_name}...", flush=True)
                process_book(part_dir, book_name, is_ot)
